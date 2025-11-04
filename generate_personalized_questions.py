#!/usr/bin/env python3
"""
Generate personalized questions from real chat data.
"""

import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_path = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_path))

from app.models import Database, Message, Question
from app.generators.question_generator import QuestionGeneratorManager
from app.config import Config

def generate_questions_from_chats():
    """Generate questions from the parsed chat messages."""
    
    print("🎯 Generating personalized questions from your chat data...")
    
    # Initialize database
    db = Database(str(Config.DATABASE_PATH))
    message_model = Message(db)
    question_model = Question(db)
    
    # Get all messages from database
    print("📊 Loading messages from database...")
    
    # Get messages from each chat
    all_messages = []
    chat_stats = {}
    
    for chat_name in Config.TARGET_CHATS:
        messages = message_model.get_messages_by_chat(chat_name, limit=1000)
        if messages:
            all_messages.extend(messages)
            chat_stats[chat_name] = len(messages)
            print(f"   📱 {chat_name}: {len(messages)} messages")
    
    if not all_messages:
        print("❌ No messages found in database. Run parse_chats.py first.")
        return
    
    print(f"✅ Loaded {len(all_messages)} total messages")
    
    # Initialize question generator
    generator_manager = QuestionGeneratorManager()
    
    # Generate a larger set of questions (50 total)
    print("🔄 Generating questions...")
    
    try:
        questions = generator_manager.generate_question_set(all_messages, num_questions=50)
        
        # Store questions in database
        stored_count = 0
        category_counts = {}
        
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
                
                # Count by category
                category = question['category']
                category_counts[category] = category_counts.get(category, 0) + 1
                
            except Exception as e:
                print(f"Error storing question: {e}")
        
        print(f"\n🎉 Generated {stored_count} personalized questions!")
        print("📊 Question breakdown:")
        for category, count in category_counts.items():
            print(f"   - {category}: {count} questions")
        
        # Show some sample questions
        print(f"\n📝 Sample questions preview:")
        for i, question in enumerate(questions[:5]):
            print(f"\n{i+1}. [{question['category']}] {question['question_text']}")
            print(f"   ✅ {question['correct_answer']}")
            print(f"   ❌ {', '.join(question['wrong_answers'][:2])}")
        
        print(f"\n🎮 Ready to play with personalized questions!")
        print(f"   Start server: source .venv/bin/activate && python3 run_server.py")
        print(f"   Go to: http://localhost:5001")
        
        return stored_count
        
    except Exception as e:
        print(f"❌ Error generating questions: {e}")
        return 0

if __name__ == "__main__":
    generate_questions_from_chats()