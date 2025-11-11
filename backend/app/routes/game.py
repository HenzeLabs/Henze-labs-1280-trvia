"""Game-related routes and WebSocket events."""

import logging
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
logger = logging.getLogger(__name__)


def log_event(event: str, **payload):
    logger.info("%s | %s", event, payload)

def _build_player_list(session):
    """Return leaderboard-style player data with ranks for socket broadcasts."""
    leaderboard = game_engine.get_leaderboard(session.room_code)
    if leaderboard:
        return [
            {
                'id': entry['player_id'],
                'name': entry['name'],
                'score': entry['score'],
                'rank': entry['rank'],
                'status': entry.get('status'),
                'answered_current': entry.get('answered_current', False)
            }
            for entry in leaderboard
        ]

    # Fallback if leaderboard is empty (e.g., before any scoring)
    fallback = []
    for idx, player in enumerate(session.players.values()):
        fallback.append({
            'id': player.id,
            'name': player.name,
            'score': player.score,
            'rank': idx + 1,
            'status': player.status,
            'answered_current': player.answered_current
        })
    return fallback

def auto_advance_after_all_answered(room_code: str):
    """Auto-advance to next question after all players answered.

    This function runs as a SocketIO background task, which ensures:
    1. It has access to the SocketIO context for emitting events
    2. It survives server reloads (as long as use_reloader=False)
    3. It can emit events to rooms without additional context setup
    """
    try:
        log_event("auto_advance_pending", room_code=room_code)
        session = game_engine.get_session(room_code)
        if not session:
            log_event("auto_advance_missing_session", room_code=room_code)
            return

        if session.phase != "question":
            log_event("auto_advance_skipped", room_code=room_code, phase=session.phase)
            return

        socketio.sleep(Config.AUTO_REVEAL_DELAY)

        # Get answer stats (triggers poll scoring) and reveal answer
        stats = game_engine.get_answer_stats(room_code)
        answer = game_engine.get_question_answer(room_code)
        reveal_duration = 0
        
        if stats and answer:
            socketio.emit('answer_revealed', {
                'room_code': room_code,
                'correct_answer': answer,
                'stats': stats
            }, room=room_code)
            log_event("answer_revealed", room_code=room_code, is_poll=stats.get('is_poll', False))
            reveal_duration = Config.AUTO_REVEAL_DISPLAY_TIME
        
        # Update leaderboard after scoring (especially for poll questions)
        refreshed_session = game_engine.get_session(room_code)
        if refreshed_session:
            player_list = _build_player_list(refreshed_session)
            socketio.emit('player_list_updated', {
                'players': player_list,
                'total_players': len(player_list)
            }, room=room_code)
        
        if reveal_duration:
            socketio.sleep(reveal_duration)

        log_event("auto_advance_run", room_code=room_code)

        # Advance to next question
        result = game_engine.next_question(room_code)
        result_type = result.get('type')

        if result_type == 'question':
            question = result.get('question') or game_engine.get_current_question(room_code)
            if question:
                socketio.emit('new_question', {'question': question}, room=room_code)
                log_event("auto_advance_question", room_code=room_code)
            else:
                log_event("auto_advance_missing_question", room_code=room_code)

        elif result_type == 'final_sprint':
            question = result.get('question') or game_engine.get_current_question(room_code)
            socketio.emit('final_sprint_started', {
                'question': question,
                'positions': result.get('positions', {}),
                'goal': result.get('goal')
            }, room=room_code)
            if question:
                socketio.emit('new_question', {'question': question}, room=room_code)
            log_event("auto_advance_final_sprint", room_code=room_code)

        elif result_type == 'game_finished':
            summary = result.get('summary')
            socketio.emit('game_finished', {'summary': summary}, room=room_code)
            log_event("auto_advance_game_finished", room_code=room_code)
    finally:
        # Reset auto-advance flag
        session = game_engine.get_session(room_code)
        if session:
            session.auto_advance_pending = False

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
                log_event("chat_messages_loaded", chat_name=chat_name, count=len(chat_messages))
            except Exception as e:
                log_event("chat_messages_error", chat_name=chat_name, error=str(e))

        # Fallback to sample data if no messages loaded
        if not all_messages:
            log_event("chat_messages_sample_data")
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
            log_event("chat_messages_total", count=len(all_messages))

        # Generate core and final sprint question sets
        # Use num_questions from request, default to 15 if not specified
        core_questions = num_questions if num_questions and num_questions > 0 else 15
        questions = question_manager.generate_question_set(all_messages, num_questions=core_questions)
        # Sprint questions should be ~40% of core questions, minimum 3
        sprint_count = max(3, int(core_questions * 0.4))
        sprint_candidates = question_manager.generate_question_set(all_messages, num_questions=sprint_count)
        sprint_questions = [
            question for question in sprint_candidates
            if question.get('question_type') not in ('poll', 'personalized_roast', 'personalized_ranking')
        ]
        if not sprint_questions:
            sprint_questions = [
                question for question in questions
                if question.get('question_type') not in ('poll', 'personalized_roast', 'personalized_ranking')
            ]

        # Create game session (no creator player needed)
        room_code = game_engine.create_session(questions, sprint_questions)
        log_event("game_created", room_code=room_code, total_questions=len(questions), sprint_questions=len(sprint_questions))

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
            player_list = _build_player_list(session)
            
            # Emit to all clients in the room (including host)
            socketio.emit('player_list_updated', {
                'players': player_list,
                'total_players': len(player_list)
            }, room=room_code)
        
        log_event("player_joined", room_code=room_code, player_id=player_id, player_name=player_name)
        return jsonify({
            'success': True,
            'player_id': player_id,
            'room_code': room_code,
            'is_creator': session.creator_player_id == player_id,
            'message': f'Joined game successfully!'
        })
    else:
        log_event("player_join_failed", room_code=room_code, player_name=player_name, error=error_message)
        return jsonify({
            'success': False,
            'message': error_message or 'Could not join game. Check room code and try again.'
        }), 400

@bp.route('/start/<room_code>', methods=['POST'])
def start_game_api(room_code):
    """
    DEPRECATED: HTTP start endpoint disabled for security (BUG #1 extension).
    Host must use WebSocket start_game event with proper authentication.
    """
    return jsonify({
        'success': False,
        'message': 'HTTP start endpoint disabled. Use WebSocket connection.',
        'error_code': 'ENDPOINT_DISABLED',
        'hint': 'TV view should emit start_game event via Socket.IO'
    }), 410  # 410 Gone

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
    """
    DEPRECATED: Host question endpoint disabled for security (BUG #4).
    This endpoint leaked correct answers to anyone who knew the room code.
    Use WebSocket events which have proper authentication.
    """
    return jsonify({
        'success': False,
        'message': 'Host endpoint disabled for security. Use WebSocket connection.',
        'error_code': 'ENDPOINT_DISABLED',
        'hint': 'TV view receives questions via question_started socket event'
    }), 410  # 410 Gone

# Manual reveal route removed - auto-reveal is now mandatory

@bp.route('/answer', methods=['POST'])
def submit_answer():
    """
    DEPRECATED: HTTP answer submission disabled for security (BUG #2).
    Players must use WebSocket submit_answer which has proper authentication.
    """
    return jsonify({
        'success': False,
        'message': 'HTTP answer submission disabled. Use WebSocket connection.',
        'error_code': 'ENDPOINT_DISABLED',
        'hint': 'Connect via Socket.IO and emit submit_answer event'
    }), 410  # 410 Gone

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
    """
    DEPRECATED: HTTP next endpoint disabled for security (BUG #1 extension).
    Host must use WebSocket next_question event with proper authentication.
    """
    return jsonify({
        'success': False,
        'message': 'HTTP next endpoint disabled. Use WebSocket connection.',
        'error_code': 'ENDPOINT_DISABLED',
        'hint': 'TV view should emit next_question event via Socket.IO'
    }), 410  # 410 Gone

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

        # Validate we got enough questions (BUG #12: prevent generator exhaustion)
        if len(questions) < 3:
            emit('error', {'message': 'Not enough questions available. Need at least 3 questions to start.'})
            log_event("socket_room_create_failed", error="Insufficient questions generated")
            return

        # Create game session (no creator player, no sprint questions)
        room_code = game_engine.create_session(questions, sprint_questions=None)

        # Emit room created event
        emit('room_created', {
            'room_code': room_code,
            'total_questions': len(questions),
            'final_sprint_questions': 0
        })

        log_event("socket_room_created", room_code=room_code, total_questions=len(questions))
        
    except Exception as e:
        emit('error', {'message': f'Failed to create room: {str(e)}'})
        log_event("socket_room_create_failed", error=str(e))

@socketio.on('start_game')
def on_start_game(data):
    """Handle starting the game via socket (from TV view)."""
    try:
        room_code = data.get('room_code')

        if not room_code:
            emit('error', {'message': 'No room code provided'})
            return

        # SECURITY (BUG #1): Get player_id from socket session
        player_id = game_engine.socket_sessions.get(request.sid)
        if not player_id:
            emit('error', {'message': 'Not authenticated'})
            return

        success = game_engine.start_game(room_code, host_player_id=player_id)

        if success:
            # Notify all players that game is starting
            socketio.emit('game_started', room=room_code)

            # Send the first question immediately (no answer for players)
            question = game_engine.get_current_question(room_code, include_answer=False)
            if question:
                socketio.emit('question_started', {'question': question}, room=room_code)

            emit('game_state_update', {'state': 'playing'})
            log_event("socket_game_started", room_code=room_code)
        else:
            emit('error', {'message': 'Could not start game'})
    except Exception as e:
        emit('error', {'message': f'Failed to start game: {str(e)}'})
        log_event("socket_start_game_failed", error=str(e))

@socketio.on('next_question')
def on_next_question(data):
    """Handle requesting next question via socket (from TV view)."""
    room_code = data.get('room_code')

    if not room_code:
        emit('error', {'message': 'No room code provided'})
        return

    # SECURITY (BUG #1 extension): Get player_id from socket session
    player_id = game_engine.socket_sessions.get(request.sid)
    if not player_id:
        emit('error', {'message': 'Not authenticated'})
        return

    result = game_engine.next_question(room_code, host_player_id=player_id)
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
    try:
        room_code = data.get('room_code', '').upper()
        player_name_raw = data.get('player_name', '')

        # SECURITY (BUG #3): Validate and sanitize player name on socket path
        try:
            player_name = APIValidator.validate_player_name(player_name_raw)
        except ValueError as e:
            emit('join_error', {'message': f'Invalid player name: {str(e)}'})
            return
    
    if not room_code or not player_name:
        emit('join_error', {'message': 'Room code and player name are required'})
        return
    
    player_id, error_message = game_engine.join_session(room_code, player_name)

    if player_id:
        session = game_engine.get_session(room_code)

        # Bind this socket session to the player_id for authentication
        game_engine.bind_socket_to_player(request.sid, player_id)

        # Join the socket room
        join_room(room_code)
        
        # Emit success to the player
        emit('joined_game', {
            'player_id': player_id,
            'room_code': room_code,
            'player_name': player_name,
            'is_creator': session.creator_player_id == player_id if session else False
        })
        
        # Update all clients with new player list
        if session:
            player_list = _build_player_list(session)
            
            socketio.emit('player_joined', {
                'player_name': player_name,
                'player_id': player_id,
                'total_players': len(player_list)
            }, room=room_code)
            
            socketio.emit('player_list_updated', {
                'players': player_list,
                'total_players': len(player_list)
            }, room=room_code)
        
        log_event("socket_player_joined", room_code=room_code, player_id=player_id, player_name=player_name)
    else:
        emit('join_error', {'message': error_message or 'Could not join game. Check room code and try again.'})
    except Exception as e:
        emit('join_error', {'message': f'Failed to join game: {str(e)}'})
        log_event("socket_join_game_failed", error=str(e))

@socketio.on('submit_answer')
def on_submit_answer(data):
    """Handle player submitting answer via socket."""
    player_id = data.get('player_id')
    answer = data.get('answer', '').strip()

    if not player_id or not answer:
        emit('answer_error', {'message': 'Player ID and answer are required'})
        return

    # SECURITY: Verify that this socket session owns the claimed player_id
    if not game_engine.verify_socket_owns_player(request.sid, player_id):
        emit('answer_error', {'message': 'Authentication failed: Invalid player session'})
        log_event("auth_failure", player_id=player_id, socket_id=request.sid)
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
        
        log_event("socket_player_answered", player_id=player_id, answer=answer, is_correct=result.get('is_correct'))
    else:
        emit('answer_error', {'message': result.get('message', 'Failed to submit answer')})

@socketio.on('join_room')
def on_join_room(data):
    """Handle player joining a room."""
    room_code = data.get('room_code')
    player_id = data.get('player_id')
    
    log_event("socket_join_room_attempt", player_id=player_id, room_code=room_code)
    
    if room_code:
        join_room(room_code)
        log_event("socket_join_room_success", player_id=player_id, room_code=room_code)
        
        # Get updated player list and broadcast
        session = game_engine.get_session(room_code)
        if session:
            player_list = _build_player_list(session)
            socketio.emit('player_list_updated', {
                'players': player_list,
                'total_players': len(player_list)
            }, room=room_code)
            log_event("socket_player_list_emitted", room_code=room_code, total_players=len(player_list))
        else:
            log_event("socket_join_room_missing_session", room_code=room_code)
    else:
        log_event("socket_join_room_missing_code", player_id=player_id)

@socketio.on('leave_room')
def on_leave_room(data):
    """Handle player leaving a room."""
    room_code = data.get('room_code')
    if room_code:
        leave_room(room_code)

@socketio.on('disconnect')
def on_disconnect():
    """Handle socket disconnection - clean up socket bindings."""
    socket_id = request.sid
    player_id = game_engine.unbind_socket(socket_id)

    if player_id:
        log_event("socket_disconnected", socket_id=socket_id, player_id=player_id)
        # Note: We don't remove the player from the game session here
        # This allows them to reconnect and resume playing
        # Session cleanup will happen via TTL mechanism

@socketio.on('ping')
def handle_ping():
    """Handle ping for connection testing."""
    socketio.emit('pong')

@socketio.on('request_game_state')
def handle_game_state_request(data):
    """Send current game state to requesting client (SECURITY: BUG #5 fixed)."""
    room_code = data.get('room_code')
    if room_code:
        # SECURITY (BUG #5): Verify requester is in the room
        player_id = game_engine.socket_sessions.get(request.sid)
        if player_id:
            player_room = game_engine.player_sessions.get(player_id)
            if player_room != room_code:
                emit('error', {'message': 'Not authorized to view this room'})
                return

        stats = game_engine.get_game_stats(room_code)
        question = game_engine.get_current_question(room_code)
        leaderboard = game_engine.get_leaderboard(room_code)

        # SECURITY (BUG #5): Send only to requester, not broadcast
        emit('game_state_update', {
            'stats': stats,
            'question': question,
            'leaderboard': leaderboard
        })
