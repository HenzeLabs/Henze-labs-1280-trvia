#!/usr/bin/env python3
"""
Generate sample questions for testing (without requiring real chat data).
"""

import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_path = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_path))

from app.models import Database, Question
from app.config import Config

def generate_sample_questions():
    """Generate sample questions for testing."""
    
    print("🎯 Generating sample questions for 1280 Trivia...")
    
    # Initialize database
    db = Database(str(Config.DATABASE_PATH))
    question_model = Question(db)
    
    # Sample roast-style questions
    roast_questions = [
        {
            'category': 'Red Flags',
            'question_type': 'roast',
            'question_text': 'Who most recently had an embarrassing drunk text incident?',
            'correct_answer': 'Alex',
            'wrong_answers': ['Jordan', 'Taylor', 'Casey'],
            'context': 'chat:1280 Group',
            'difficulty': 2
        },
        {
            'category': 'Red Flags', 
            'question_type': 'roast',
            'question_text': 'Who is most likely to show up to brunch still drunk from the night before?',
            'correct_answer': 'Jordan',
            'wrong_answers': ['Alex', 'Taylor', 'Casey'],
            'context': 'chat:Weekend Plans',
            'difficulty': 1
        },
        {
            'category': 'Degenerate of the Week',
            'question_type': 'most_likely',
            'question_text': 'Who\'s most likely to order $200 worth of DoorDash at 3am?',
            'correct_answer': 'Taylor',
            'wrong_answers': ['Alex', 'Jordan', 'Casey'],
            'context': 'chat:Degen Hours',
            'difficulty': 2
        }
    ]
    
    # Sample "who said this" questions
    receipt_questions = [
        {
            'category': 'Receipts',
            'question_type': 'who_said_this',
            'question_text': 'Who said: "I can\'t believe I locked myself out in my underwear AGAIN"?',
            'correct_answer': 'Alex',
            'wrong_answers': ['Jordan', 'Taylor', 'Casey'],
            'context': 'chat:1280 Group',
            'difficulty': 1
        },
        {
            'category': 'Receipts',
            'question_type': 'who_said_this',
            'question_text': 'Who said: "Why did I wake up with a traffic cone in my room?"',
            'correct_answer': 'Casey',
            'wrong_answers': ['Alex', 'Jordan', 'Taylor'],
            'context': 'chat:Rooftop Crew',
            'difficulty': 2
        },
        {
            'category': 'Receipts',
            'question_type': 'who_said_this', 
            'question_text': 'Who said: "I may have accidentally joined a CrossFit cult"?',
            'correct_answer': 'Jordan',
            'wrong_answers': ['Alex', 'Taylor', 'Casey'],
            'context': 'chat:Weekend Plans',
            'difficulty': 1
        }
    ]
    
    # Sample normal trivia questions
    trivia_questions = [
        {
            'category': 'Random Trivia',
            'question_type': 'general',
            'question_text': 'What year did the first iPhone launch?',
            'correct_answer': '2007',
            'wrong_answers': ['2005', '2006', '2008'],
            'context': 'general',
            'difficulty': 1
        },
        {
            'category': 'Random Trivia',
            'question_type': 'general',
            'question_text': 'Which planet is known as the Red Planet?',
            'correct_answer': 'Mars',
            'wrong_answers': ['Venus', 'Jupiter', 'Saturn'],
            'context': 'general',
            'difficulty': 1
        }
    ]
    
    # Store all questions
    all_questions = roast_questions + receipt_questions + trivia_questions
    stored_count = 0
    
    for question in all_questions:
        try:
            question_model.add_question(
                category=question['category'],
                question_type=question['question_type'],
                question_text=question['question_text'],
                correct_answer=question['correct_answer'],
                wrong_answers=question['wrong_answers'],
                context=question['context'],
                difficulty=question['difficulty']
            )
            stored_count += 1
        except Exception as e:
            print(f"Error storing question: {e}")
    
    print(f"✅ Generated {stored_count} sample questions:")
    print(f"   - {len(roast_questions)} roast/embarrassing questions")
    print(f"   - {len(receipt_questions)} 'who said this' questions") 
    print(f"   - {len(trivia_questions)} normal trivia questions")
    
    print(f"\n🎮 Ready to play! You can now:")
    print(f"   1. Start the server: source .venv/bin/activate && python3 run_server.py")
    print(f"   2. Go to http://localhost:5000 to host a game")
    print(f"   3. Players join with room codes on their phones")
    
    return stored_count

if __name__ == "__main__":
    generate_sample_questions()