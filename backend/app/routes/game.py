"""Game-related routes and WebSocket events."""

from flask import Blueprint, request, jsonify
from flask_socketio import emit, join_room, leave_room
from typing import Dict, Optional
from ..game.engine import game_engine
from ..game.models_v1 import APIValidator, enforce_api_contract
from ..generators.question_generator import QuestionGeneratorManager
from ..parsers.imessage_parser import iMessageParser
from ..models import Database, Message
from ..config import Config
from .. import socketio

bp = Blueprint('game', __name__, url_prefix='/api/game')

# Track active auto-advance tasks - no longer needed with SocketIO background tasks
# _auto_advance_timers = {}

# Initialize components
question_manager = QuestionGeneratorManager()
db = Database(str(Config.DATABASE_PATH))
message_model = Message(db)

def auto_advance_after_all_answered(room_code: str):
    """Auto-advance to next question after all players answered.

    This function runs as a SocketIO background task, which ensures:
    1. It has access to the SocketIO context for emitting events
    2. It survives server reloads (as long as use_reloader=False)
    3. It can emit events to rooms without additional context setup
    """
    print(f"⏱️  All players answered in {room_code} - auto-advancing in 5 seconds...")

    # Wait 5 seconds to show results
    socketio.sleep(5)  # Use socketio.sleep() instead of time.sleep() for better integration

    print(f"🚀 Auto-advance timer expired for {room_code}, advancing now...")

    # Advance to next question
    result = game_engine.next_question(room_code)
    result_type = result.get('type')

    if result_type == 'question':
        question = result.get('question') or game_engine.get_current_question(room_code)
        if question:
            socketio.emit('new_question', {'question': question}, room=room_code)
            print(f"✅ Auto-advanced to next question in {room_code}")
        else:
            print(f"❌ No question found after auto-advance in {room_code}")

    elif result_type == 'final_sprint':
        question = result.get('question') or game_engine.get_current_question(room_code)
        socketio.emit('final_sprint_started', {
            'question': question,
            'positions': result.get('positions', {}),
            'goal': result.get('goal')
        }, room=room_code)
        if question:
            socketio.emit('new_question', {'question': question}, room=room_code)
        print(f"✅ Auto-started final sprint in {room_code}")

    elif result_type == 'game_finished':
        summary = result.get('summary')
        socketio.emit('game_finished', {'summary': summary}, room=room_code)
        print(f"🏁 Game finished in {room_code}")

@bp.route('/create', methods=['POST'])
def create_game():
    """Create a new game session."""
    data = request.get_json()

    # 🔒 API Contract Validation
    try:
        creator_name = APIValidator.validate_player_name(data.get('player_name', data.get('host_name', '')))
        num_questions = data.get('num_questions', 15)  # Default to 15 if not specified
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e),
            'error_code': 'INVALID_PAYLOAD'
        }), 400

    try:
        # Load real iMessage data for question generation
        parser = iMessageParser(
            imessage_db_path=str(Config.IMESSAGE_DB_PATH),
            contact_map=Config.CONTACT_MAP
        )

        # Load messages from all target chats
        all_messages = []
        for chat_name in Config.TARGET_CHATS:
            try:
                chat_messages = parser.get_chat_messages(chat_name, limit=1000, months_back=12)
                all_messages.extend(chat_messages)
                print(f"✅ Loaded {len(chat_messages)} messages from '{chat_name}'")
            except Exception as e:
                print(f"⚠️ Error loading chat '{chat_name}': {e}")

        # Fallback to sample data if no messages loaded
        if not all_messages:
            print("⚠️ No real messages loaded, using sample data")
            all_messages = [
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
        else:
            print(f"🎉 Total messages loaded: {len(all_messages)}")

        # Generate core and final sprint question sets
        # Use num_questions from request, default to 15 if not specified
        core_questions = num_questions if num_questions and num_questions > 0 else 15
        questions = question_manager.generate_question_set(all_messages, num_questions=core_questions)
        # Sprint questions should be ~40% of core questions, minimum 3
        sprint_count = max(3, int(core_questions * 0.4))
        sprint_questions = question_manager.generate_question_set(all_messages, num_questions=sprint_count)

        # Create game session (no creator player needed)
        room_code = game_engine.create_session(questions, sprint_questions)

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
    
    # 🔒 API Contract Validation
    try:
        room_code = APIValidator.validate_room_code(data.get('room_code', ''))
        player_name = APIValidator.validate_player_name(data.get('player_name', ''))
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e),
            'error_code': 'INVALID_PAYLOAD'
        }), 400
    
    player_id, error_message = game_engine.join_session(room_code, player_name)
    
    if player_id:
        # Get the updated session
        session = game_engine.get_session(room_code)
        if session:
            # Create player list for broadcasting
            player_list = [{'id': p.id, 'name': p.name, 'score': p.score, 'status': p.status, 'answered_current': p.answered_current} 
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
            'message': error_message or 'Could not join game. Check room code and try again.'
        }), 400

@bp.route('/start/<room_code>', methods=['POST'])
def start_game_api(room_code):
    """Start a game session via API (deprecated - use socket instead)."""
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
    """Get the current question for a room (player version - no answer)."""
    question = game_engine.get_current_question(room_code, include_answer=False)

    if question:
        return jsonify({'success': True, 'question': question})
    else:
        return jsonify({
            'success': False,
            'message': 'No current question available'
        }), 404

@bp.route('/question/<room_code>/host')
def get_current_question_host(room_code):
    """Get the current question for a room (includes answer for TV view)."""
    question = game_engine.get_current_question(room_code, include_answer=True)

    if question:
        return jsonify({'success': True, 'question': question})
    else:
        return jsonify({
            'success': False,
            'message': 'No current question available'
        }), 404

@bp.route('/reveal/<room_code>')
def reveal_answer(room_code):
    """Reveal the correct answer for the current question."""
    answer = game_engine.get_question_answer(room_code)
    stats = game_engine.get_answer_stats(room_code)

    if answer and stats:
        return jsonify({
            'success': True,
            'correct_answer': answer,
            'stats': stats
        })
    else:
        return jsonify({
            'success': False,
            'message': 'No question to reveal'
        }), 404

@bp.route('/answer', methods=['POST'])
def submit_answer():
    """Submit an answer for a player."""
    data = request.get_json()
    
    # 🔒 API Contract Validation
    try:
        player_id = APIValidator.validate_player_id(data.get('player_id', ''))
        answer = data.get('answer', '').strip()
        if not answer:
            raise ValueError("Answer cannot be empty")
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e),
            'error_code': 'INVALID_PAYLOAD'
        }), 400
    
    result = game_engine.submit_answer(player_id, answer)
    
    session = game_engine.get_player_session(player_id)
    if session:
        room_code = session.room_code

        def broadcast_player_list():
            player_list = [
                {
                    'id': p.id,
                    'name': p.name,
                    'score': p.score,
                    'status': p.status,
                    'answered_current': p.answered_current
                }
                for p in session.players.values()
            ]
            socketio.emit('player_list_updated', {
                'players': player_list,
                'total_players': len(player_list)
            }, room=room_code)

        def emit_next_step(step: Optional[Dict]):
            if not step:
                return
            step_type = step.get('type')
            if step_type == 'question':
                question = step.get('question') or game_engine.get_current_question(room_code)
                if question:
                    socketio.emit('new_question', {'question': question}, room=room_code)
            elif step_type == 'final_sprint':
                question = step.get('question') or game_engine.get_current_question(room_code)
                socketio.emit('final_sprint_started', {
                    'question': question,
                    'positions': step.get('positions', {}),
                    'goal': step.get('goal')
                }, room=room_code)
                if question:
                    socketio.emit('new_question', {'question': question}, room=room_code)
            elif step_type == 'game_finished':
                summary = step.get('summary')
                socketio.emit('game_finished', {'summary': summary}, room=room_code)

        phase = result.get('phase')

        if phase == 'question' and result.get('success'):
            socketio.emit('player_answered', {
                'player_id': player_id,
                'is_correct': result.get('is_correct', False),
                'phase': 'question'
            }, room=room_code)

            broadcast_player_list()

            # 🚀 AUTO-ADVANCE: Check if all players have answered
            if game_engine.all_players_answered(room_code):
                print(f"✅ All players answered in {room_code}, starting auto-advance background task...")

                # Start auto-advance as a SocketIO background task
                # This ensures proper context and survival across reloads
                socketio.start_background_task(auto_advance_after_all_answered, room_code)

                # Notify players that everyone answered
                answered, total = game_engine.get_answered_count(room_code)
                socketio.emit('all_players_answered', {
                    'message': f'All players answered! Moving to next question in 5 seconds...',
                    'answered': answered,
                    'total': total
                }, room=room_code)
                print(f"📢 Broadcast all_players_answered to room {room_code}")

        elif phase == 'final_sprint':
            if result.get('awaiting'):
                socketio.emit('final_sprint_waiting', {'player_id': player_id}, room=room_code)
            elif result.get('question_complete'):
                socketio.emit('final_sprint_update', {
                    'results': result['results'],
                    'positions': result.get('positions', {})
                }, room=room_code)
                emit_next_step(result.get('next_step'))
            elif result.get('final_sprint_complete'):
                socketio.emit('final_sprint_update', {
                    'results': result['results'],
                    'winner_id': result.get('winner_id'),
                    'positions': session.final_sprint_state.get('positions', {}) if session.final_sprint_state else {}
                }, room=room_code)
                summary = result.get('summary')
                if summary:
                    socketio.emit('game_finished', {'summary': summary}, room=room_code)
                broadcast_player_list()

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
    result = game_engine.next_question(room_code)

    result_type = result.get('type')

    if result_type == 'question':
        question = result.get('question') or game_engine.get_current_question(room_code)
        if question:
            socketio.emit('new_question', {'question': question}, room=room_code)
        session = game_engine.get_session(room_code)
        if session:
            player_list = [
                {
                    'id': p.id,
                    'name': p.name,
                    'score': p.score,
                    'status': p.status,
                    'answered_current': p.answered_current
                }
                for p in session.players.values()
            ]
            socketio.emit('player_list_updated', {
                'players': player_list,
                'total_players': len(player_list)
            }, room=room_code)
        return jsonify({'success': True, 'message': 'Next question loaded'})

    if result_type == 'final_sprint':
        question = result.get('question') or game_engine.get_current_question(room_code)
        socketio.emit('final_sprint_started', {
            'question': question,
            'positions': result.get('positions', {}),
            'goal': result.get('goal')
        }, room=room_code)
        if question:
            socketio.emit('new_question', {'question': question}, room=room_code)
        session = game_engine.get_session(room_code)
        if session and session.final_sprint_state:
            positions = session.final_sprint_state.get('positions', {})
            socketio.emit('final_sprint_update', {
                'positions': positions,
                'goal': session.final_sprint_state.get('goal')
            }, room=room_code)
        return jsonify({'success': True, 'final_sprint_started': True})

    if result_type == 'game_finished':
        summary = result.get('summary') or game_engine.get_session_summary(room_code)
        socketio.emit('game_finished', {'summary': summary}, room=room_code)
        return jsonify({'success': True, 'game_finished': True, 'summary': summary})

    if result_type == 'final_sprint_in_progress':
        return jsonify({
            'success': False,
            'message': 'Final sprint underway—wait for players to answer.'
        }), 400

    if result_type == 'error':
        return jsonify({
            'success': False,
            'message': result.get('message', 'Could not advance game')
        }), 400

    return jsonify({'success': True, 'message': 'No further action required'})

# WebSocket Events
@socketio.on('create_room')
def on_create_room(data):
    """Handle creating a room via socket (no auto-join)."""
    
    try:
        # Get sample messages for question generation
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
            },
            {
                'id': 4,
                'sender': 'Sam',
                'message_text': 'I matched with my ex on Bumble... should I swipe right?',
                'chat_name': '1280 Group',
                'timestamp': '2024-01-04'
            },
            {
                'id': 5,
                'sender': 'Riley',
                'message_text': 'Update: I got kicked out of Target for trying on clothes in the aisle',
                'chat_name': '1280 Group',
                'timestamp': '2024-01-05'
            }
        ]
        
        # Generate questions (no sprint questions for simpler gameplay)
        questions = question_manager.generate_question_set(sample_messages, num_questions=10)

        # Create game session (no creator player, no sprint questions)
        room_code = game_engine.create_session(questions, sprint_questions=None)

        # Emit room created event
        emit('room_created', {
            'room_code': room_code,
            'total_questions': len(questions),
            'final_sprint_questions': 0
        })

        print(f"Game room {room_code} created (waiting for players to join)")
        
    except Exception as e:
        emit('error', {'message': f'Failed to create room: {str(e)}'})
        print(f"Error creating room: {e}")

@socketio.on('start_game')
def on_start_game(data):
    """Handle starting the game via socket (from TV view)."""
    room_code = data.get('room_code')

    if not room_code:
        emit('error', {'message': 'No room code provided'})
        return

    success = game_engine.start_game(room_code)

    if success:
        # Notify all players that game is starting
        socketio.emit('game_started', room=room_code)

        # Send the first question immediately (no answer for players)
        question = game_engine.get_current_question(room_code, include_answer=False)
        if question:
            socketio.emit('question_started', {'question': question}, room=room_code)

        emit('game_state_update', {'state': 'playing'})
        print(f"Game started in room {room_code}")
    else:
        emit('error', {'message': 'Could not start game'})

@socketio.on('next_question')
def on_next_question(data):
    """Handle requesting next question via socket (from TV view)."""
    room_code = data.get('room_code')

    if not room_code:
        emit('error', {'message': 'No room code provided'})
        return

    result = game_engine.next_question(room_code)
    result_type = result.get('type')

    if result_type == 'question':
        question = result.get('question') or game_engine.get_current_question(room_code, include_answer=False)
        if question:
            socketio.emit('question_started', {'question': question}, room=room_code)
            emit('question_started', {'question': question})
        return

    if result_type == 'final_sprint':
        question = result.get('question') or game_engine.get_current_question(room_code, include_answer=False)
        socketio.emit('final_sprint_started', {
            'question': question,
            'positions': result.get('positions', {}),
            'goal': result.get('goal')
        }, room=room_code)
        if question:
            socketio.emit('question_started', {'question': question}, room=room_code)
            emit('question_started', {'question': question})
        return

    if result_type == 'game_finished':
        summary = result.get('summary') or game_engine.get_session_summary(room_code)
        socketio.emit('game_ended', {'summary': summary}, room=room_code)
        emit('game_ended', {'summary': summary})
        return

    if result_type == 'final_sprint_in_progress':
        emit('error', {'message': 'Final sprint underway—wait for the results'})
        return

    if result_type == 'error':
        emit('error', {'message': result.get('message', 'Could not advance game')})

@socketio.on('join_game')
def on_join_game(data):
    """Handle player joining via socket."""
    room_code = data.get('room_code', '').upper()
    player_name = data.get('player_name', '')
    
    if not room_code or not player_name:
        emit('join_error', {'message': 'Room code and player name are required'})
        return
    
    player_id, error_message = game_engine.join_session(room_code, player_name)

    if player_id:
        # Join the socket room
        join_room(room_code)
        
        # Emit success to the player
        emit('joined_game', {
            'player_id': player_id,
            'room_code': room_code,
            'player_name': player_name
        })
        
        # Update all clients with new player list
        session = game_engine.get_session(room_code)
        if session:
            player_list = [{'id': p.id, 'name': p.name, 'score': p.score, 'status': p.status, 'answered_current': p.answered_current} 
                          for p in session.players.values()]
            
            socketio.emit('player_joined', {
                'player_name': player_name,
                'player_id': player_id,
                'total_players': len(player_list)
            }, room=room_code)
            
            socketio.emit('player_list_updated', {
                'players': player_list,
                'total_players': len(player_list)
            }, room=room_code)
        
        print(f"Player {player_name} ({player_id}) joined room {room_code}")
    else:
        emit('join_error', {'message': error_message or 'Could not join game. Check room code and try again.'})

@socketio.on('submit_answer')
def on_submit_answer(data):
    """Handle player submitting answer via socket."""
    player_id = data.get('player_id')
    answer = data.get('answer', '').strip()
    
    if not player_id or not answer:
        emit('answer_error', {'message': 'Player ID and answer are required'})
        return
    
    result = game_engine.submit_answer(player_id, answer)
    
    if result.get('success'):
        # Send feedback to the player
        emit('answer_feedback', {
            'correct': result.get('is_correct', False),
            'points': result.get('points_earned', 0),
            'total_score': result.get('total_score', 0),
            'correct_answer': result.get('correct_answer', '')
        })
        
        # Notify the room about the answer
        session = game_engine.get_player_session(player_id)
        if session:
            socketio.emit('player_answered', {
                'player_id': player_id,
                'is_correct': result.get('is_correct', False)
            }, room=session.room_code)
            
            # Check if all players have answered
            stats = game_engine.get_game_stats(session.room_code)
            if stats.get('players_answered') == stats.get('total_players'):
                socketio.emit('all_answers_received', {
                    'results': game_engine.get_leaderboard(session.room_code)
                }, room=session.room_code)
        
        print(f"Player {player_id} submitted answer: {answer} ({'correct' if result.get('is_correct') else 'incorrect'})")
    else:
        emit('answer_error', {'message': result.get('message', 'Failed to submit answer')})

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
            player_list = [{'id': p.id, 'name': p.name, 'score': p.score, 'status': p.status, 'answered_current': p.answered_current} 
                          for p in session.players.values()]
            socketio.emit('player_list_updated', {
                'players': player_list,
                'total_players': len(player_list)
            }, room=room_code)
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
