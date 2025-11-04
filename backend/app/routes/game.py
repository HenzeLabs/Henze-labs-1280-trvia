"""Game-related routes and WebSocket events."""

from flask import Blueprint, request, jsonify
from flask_socketio import emit, join_room, leave_room
from ..game.engine import game_engine
from ..generators.question_generator import QuestionGeneratorManager
from ..parsers.imessage_parser import iMessageParser
from ..models import Database, Message
from ..config import Config
from .. import socketio

bp = Blueprint('game', __name__, url_prefix='/api/game')

# Initialize components
question_manager = QuestionGeneratorManager()
db = Database(str(Config.DATABASE_PATH))
message_model = Message(db)

@bp.route('/create', methods=['POST'])
def create_game():
    """Create a new game session."""
    data = request.get_json()
    host_name = data.get('host_name', 'Anonymous Host')
    
    try:
        # Get messages for question generation
        # For now, use sample data - you'll need to parse real chat data
        sample_messages = [
            {
                'id': 1,
                'sender': 'Alex',
                'message_text': 'I can\'t believe I locked myself out in my underwear again',
                'chat_name': '1280 Group',
                'timestamp': '2024-01-01'
            },
            {
                'id': 2, 
                'sender': 'Jordan',
                'message_text': 'Who wants to get absolutely destroyed at trivia tonight?',
                'chat_name': '1280 Group',
                'timestamp': '2024-01-02'
            },
            {
                'id': 3,
                'sender': 'Taylor',
                'message_text': 'I may have drunk ordered $200 worth of sushi last night',
                'chat_name': '1280 Group',
                'timestamp': '2024-01-03'
            }
        ]
        
        # Generate questions
        questions = question_manager.generate_question_set(sample_messages, num_questions=10)
        
        # Create game session
        room_code = game_engine.create_session(host_name, questions)
        
        return jsonify({
            'success': True,
            'room_code': room_code,
            'message': f'Game created! Room code: {room_code}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error creating game: {str(e)}'
        }), 500

@bp.route('/join', methods=['POST'])
def join_game():
    """Join an existing game session."""
    data = request.get_json()
    room_code = data.get('room_code', '').upper()
    player_name = data.get('player_name', '')
    
    if not room_code or not player_name:
        return jsonify({
            'success': False,
            'message': 'Room code and player name are required'
        }), 400
    
    player_id = game_engine.join_session(room_code, player_name)
    
    if player_id:
        # Get the updated session
        session = game_engine.get_session(room_code)
        if session:
            # Create player list for broadcasting
            player_list = [{'id': p.id, 'name': p.name, 'score': p.score} 
                          for p in session.players.values()]
            
            # Emit to all clients in the room (including host)
            socketio.emit('player_list_updated', {
                'players': player_list,
                'total_players': len(player_list)
            }, room=room_code)
        
        return jsonify({
            'success': True,
            'player_id': player_id,
            'room_code': room_code,
            'message': f'Joined game successfully!'
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Could not join game. Check room code and try again.'
        }), 400

@bp.route('/start/<room_code>', methods=['POST'])
def start_game(room_code):
    """Start a game session."""
    success = game_engine.start_game(room_code)
    
    if success:
        # Notify all players that game is starting
        socketio.emit('game_started', room=room_code)
        
        # Send the first question immediately
        question = game_engine.get_current_question(room_code)
        if question:
            socketio.emit('new_question', {'question': question}, room=room_code)
            
        return jsonify({'success': True, 'message': 'Game started!'})
    else:
        return jsonify({
            'success': False,
            'message': 'Could not start game'
        }), 400

@bp.route('/question/<room_code>')
def get_current_question(room_code):
    """Get the current question for a room."""
    question = game_engine.get_current_question(room_code)
    
    if question:
        return jsonify({'success': True, 'question': question})
    else:
        return jsonify({
            'success': False,
            'message': 'No current question available'
        }), 404

@bp.route('/answer', methods=['POST'])
def submit_answer():
    """Submit an answer for a player."""
    data = request.get_json()
    player_id = data.get('player_id')
    answer = data.get('answer')
    
    if not player_id or not answer:
        return jsonify({
            'success': False,
            'message': 'Player ID and answer are required'
        }), 400
    
    result = game_engine.submit_answer(player_id, answer)
    
    # Notify the room about the answer
    session = game_engine.get_player_session(player_id)
    if session:
        socketio.emit('player_answered', {
            'player_id': player_id,
            'is_correct': result.get('is_correct', False)
        }, room=session.room_code)
    
    return jsonify(result)

@bp.route('/leaderboard/<room_code>')
def get_leaderboard(room_code):
    """Get current leaderboard for a room."""
    leaderboard = game_engine.get_leaderboard(room_code)
    return jsonify({'leaderboard': leaderboard})

@bp.route('/stats/<room_code>')
def get_game_stats(room_code):
    """Get game statistics for a room."""
    stats = game_engine.get_game_stats(room_code)
    return jsonify(stats)

@bp.route('/player-session/<player_id>')
def get_player_session(player_id):
    """Get session info for a player."""
    session = game_engine.get_player_session(player_id)
    if session:
        return jsonify({
            'success': True,
            'session': {
                'room_code': session.room_code,
                'status': session.status,
                'player_count': len(session.players)
            }
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Player session not found'
        }), 404

@bp.route('/next/<room_code>', methods=['POST'])
def next_question(room_code):
    """Move to the next question."""
    has_next = game_engine.next_question(room_code)
    
    if has_next:
        # Notify all players about new question
        question = game_engine.get_current_question(room_code)
        socketio.emit('new_question', {'question': question}, room=room_code)
        return jsonify({'success': True, 'message': 'Next question loaded'})
    else:
        # Game finished
        summary = game_engine.get_session_summary(room_code)
        socketio.emit('game_finished', {'summary': summary}, room=room_code)
        return jsonify({'success': True, 'game_finished': True, 'summary': summary})

# WebSocket Events
@socketio.on('join_room')
def on_join_room(data):
    """Handle player joining a room."""
    room_code = data.get('room_code')
    player_id = data.get('player_id')
    
    print(f"Player {player_id} attempting to join room {room_code}")
    
    if room_code:
        join_room(room_code)
        print(f"Player {player_id} joined room {room_code}")
        
        # Get updated player list and broadcast
        session = game_engine.get_session(room_code)
        if session:
            player_list = [{'id': p.id, 'name': p.name, 'score': p.score} 
                          for p in session.players.values()]
            socketio.emit('player_list_updated', {'players': player_list}, room=room_code)
            print(f"Emitted player_list_updated to room {room_code}")
        else:
            print(f"No session found for room {room_code}")
    else:
        print("No room code provided in join_room event")

@socketio.on('leave_room')
def on_leave_room(data):
    """Handle player leaving a room."""
    room_code = data.get('room_code')
    if room_code:
        leave_room(room_code)

@socketio.on('ping')
def handle_ping():
    """Handle ping for connection testing."""
    socketio.emit('pong')

@socketio.on('request_game_state')
def handle_game_state_request(data):
    """Send current game state to requesting client."""
    room_code = data.get('room_code')
    if room_code:
        stats = game_engine.get_game_stats(room_code)
        question = game_engine.get_current_question(room_code)
        leaderboard = game_engine.get_leaderboard(room_code)
        
        socketio.emit('game_state_update', {
            'stats': stats,
            'question': question,
            'leaderboard': leaderboard
        })