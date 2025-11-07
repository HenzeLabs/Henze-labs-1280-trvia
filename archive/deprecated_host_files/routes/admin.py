"""Admin routes for managing chat data and questions."""

from flask import Blueprint, request, jsonify, render_template
from ..parsers.imessage_parser import iMessageParser
from ..generators.question_generator import QuestionGeneratorManager
from ..models import Database, Message, Question
from ..config import Config
import os

bp = Blueprint('admin', __name__, url_prefix='/api/admin')

# Initialize components
db = Database(str(Config.DATABASE_PATH))
message_model = Message(db)
question_model = Question(db)
question_manager = QuestionGeneratorManager()

@bp.route('/chats')
def list_chats():
    """List available chat groups."""
    try:
        parser = iMessageParser(Config.IMESSAGE_DB_PATH)
        chats = parser.get_all_chat_names()
        return jsonify({
            'success': True,
            'chats': chats[:20]  # Limit to first 20 for performance
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error accessing chat database: {str(e)}'
        }), 500

@bp.route('/parse-chat', methods=['POST'])
def parse_chat():
    """Parse messages from a specific chat."""
    data = request.get_json()
    chat_name = data.get('chat_name')
    limit = data.get('limit', 1000)
    
    if not chat_name:
        return jsonify({
            'success': False,
            'message': 'Chat name is required'
        }), 400
    
    try:
        parser = iMessageParser(Config.IMESSAGE_DB_PATH)
        messages = parser.get_chat_messages(chat_name, limit=limit)
        
        # Store messages in database
        stored_count = 0
        for message in messages:
            try:
                message_model.add_message(
                    chat_name=message['chat_name'],
                    sender=message['sender'],
                    message_text=message['message_text'],
                    timestamp=message['timestamp'],
                    message_type=message['message_type']
                )
                stored_count += 1
            except Exception as e:
                print(f"Error storing message: {e}")
        
        return jsonify({
            'success': True,
            'message': f'Parsed and stored {stored_count} messages from {chat_name}',
            'messages_count': stored_count
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error parsing chat: {str(e)}'
        }), 500

@bp.route('/generate-questions', methods=['POST'])
def generate_questions():
    """Generate questions from stored messages."""
    data = request.get_json()
    chat_name = data.get('chat_name')
    num_questions = data.get('num_questions', 20)
    
    try:
        # Get messages from database
        if chat_name:
            messages = message_model.get_messages_by_chat(chat_name, limit=500)
        else:
            messages = message_model.get_random_messages(limit=500)
        
        if not messages:
            return jsonify({
                'success': False,
                'message': 'No messages found to generate questions from'
            }), 400
        
        # Generate questions
        questions = question_manager.generate_question_set(messages, num_questions=num_questions)
        
        # Store questions in database
        stored_count = 0
        for question in questions:
            try:
                question_model.add_question(
                    category=question['category'],
                    question_type=question['question_type'], 
                    question_text=question['question_text'],
                    correct_answer=question['correct_answer'],
                    wrong_answers=question['wrong_answers'],
                    context=question.get('context', ''),
                    difficulty=question.get('difficulty', 1),
                    source_message_id=question.get('source_message_id')
                )
                stored_count += 1
            except Exception as e:
                print(f"Error storing question: {e}")
        
        return jsonify({
            'success': True,
            'message': f'Generated and stored {stored_count} questions',
            'questions_count': stored_count,
            'sample_questions': questions[:3]  # Show first 3 as preview
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error generating questions: {str(e)}'
        }), 500

@bp.route('/questions')
def list_questions():
    """List stored questions."""
    try:
        category = request.args.get('category')
        limit = int(request.args.get('limit', 50))
        
        questions = question_model.get_random_questions(category=category, limit=limit)
        
        return jsonify({
            'success': True,
            'questions': questions,
            'count': len(questions)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving questions: {str(e)}'
        }), 500

@bp.route('/export-csv', methods=['POST'])
def export_chat_csv():
    """Export chat data to CSV."""
    data = request.get_json()
    chat_name = data.get('chat_name')
    
    if not chat_name:
        return jsonify({
            'success': False,
            'message': 'Chat name is required'
        }), 400
    
    try:
        parser = iMessageParser(Config.IMESSAGE_DB_PATH)
        output_path = f"/tmp/{chat_name.replace(' ', '_')}_export.csv"
        parser.export_to_csv(chat_name, output_path)
        
        return jsonify({
            'success': True,
            'message': f'Chat exported to {output_path}',
            'file_path': output_path
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error exporting chat: {str(e)}'
        }), 500

@bp.route('/stats')
def get_stats():
    """Get database statistics."""
    try:
        with db.get_connection() as conn:
            # Get message count by chat
            cursor = conn.execute('''
                SELECT chat_name, COUNT(*) as message_count
                FROM messages 
                GROUP BY chat_name 
                ORDER BY message_count DESC
            ''')
            chat_stats = [{'chat_name': row[0], 'message_count': row[1]} 
                         for row in cursor.fetchall()]
            
            # Get question count by category
            cursor = conn.execute('''
                SELECT category, COUNT(*) as question_count
                FROM questions 
                GROUP BY category 
                ORDER BY question_count DESC
            ''')
            question_stats = [{'category': row[0], 'question_count': row[1]} 
                            for row in cursor.fetchall()]
            
            # Get total counts
            cursor = conn.execute('SELECT COUNT(*) FROM messages')
            total_messages = cursor.fetchone()[0]
            
            cursor = conn.execute('SELECT COUNT(*) FROM questions')
            total_questions = cursor.fetchone()[0]
            
            return jsonify({
                'success': True,
                'stats': {
                    'total_messages': total_messages,
                    'total_questions': total_questions,
                    'chat_breakdown': chat_stats,
                    'question_breakdown': question_stats
                }
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting stats: {str(e)}'
        }), 500

@bp.route('/test-connection')
def test_imessage_connection():
    """Test connection to iMessage database."""
    try:
        if not os.path.exists(Config.IMESSAGE_DB_PATH):
            return jsonify({
                'success': False,
                'message': f'iMessage database not found at {Config.IMESSAGE_DB_PATH}',
                'path': Config.IMESSAGE_DB_PATH
            })
        
        parser = iMessageParser(Config.IMESSAGE_DB_PATH)
        chats = parser.get_all_chat_names()
        
        return jsonify({
            'success': True,
            'message': f'Successfully connected to iMessage database',
            'chat_count': len(chats),
            'sample_chats': chats[:5]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error connecting to iMessage database: {str(e)}'
        }), 500