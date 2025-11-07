#!/usr/bin/env python3
"""
TEST THE MAXIMUM SAVAGE MODE - Cards Against Humanity WISHES it was this brutal
"""

import sys
from pathlib import Path
import random

# Add the backend directory to the Python path
backend_path = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_path))

from app.models import Database, Message
from app.config import Config
from app.generators.question_generator import QuestionGeneratorManager

def main():
    print('💀💀💀 MAXIMUM SAVAGE 1280 TRIVIA - DISNEY GAME NO MORE 💀💀💀')
    print('⚠️  WARNING: THIS MAKES CARDS AGAINST HUMANITY LOOK LIKE SESAME STREET')
    print('=' * 80)
    
    # Connect to the real chat database
    db = Database(str(Config.DATABASE_PATH))
    message_model = Message(db)
    generator_manager = QuestionGeneratorManager()
    
    # Get real messages from the database
    real_messages = message_model.get_random_messages(limit=200)
    
    if not real_messages:
        print("❌ No messages found in database")
        return
    
    # Get actual names - INCLUDE LAUREN AS A ROAST TARGET!
    real_senders = list(set([msg['sender'] if msg['sender'] != 'You' else 'Lauren' for msg in real_messages if msg['sender']]))
    print(f'🎯 SAVAGE TARGETS: {", ".join(real_senders)} (YES, LAUREN TOO!)')
    print(f'📱 Messages Analyzed: {len(real_messages)}')
    
    print('\n🔥 GENERATING ABSOLUTE CHAOS...\n')
    
    # Generate 10 SAVAGE questions
    try:
        savage_questions = generator_manager.generate_question_set(real_messages, num_questions=10)
        
        for i, q in enumerate(savage_questions, 1):
            print(f'💀 ROUND {i} - {q["category"]}')
            print(f'🔥 {q["question_text"]}')
            print('')
            
            # Shuffle answers
            all_answers = [q['correct_answer']] + q['wrong_answers']
            random.shuffle(all_answers)
            
            for j, answer in enumerate(all_answers, 1):
                marker = '💀' if answer == q['correct_answer'] else '  '
                print(f'{marker} {chr(64+j)}) {answer}')
            
            print('')
            print(f'💬 {q.get("context", "Pure chaos")}')
            print(f'🌶️  Savage Level: {"🔥" * q.get("difficulty", 1)}')
            
            if i < len(savage_questions):
                print('-' * 60)
    
    except Exception as e:
        print(f"Error generating savage questions: {e}")
        return
    
    print('\n' + '=' * 80)
    print('🏆 CONGRATULATIONS - YOU\'VE CREATED A FRIENDSHIP DESTROYER')
    print('📊 SAVAGE ANALYTICS:')
    
    # Count categories
    category_counts = {}
    total_savage_level = 0
    for q in savage_questions:
        cat = q['category']
        category_counts[cat] = category_counts.get(cat, 0) + 1
        total_savage_level += q.get('difficulty', 1)
    
    for category, count in category_counts.items():
        print(f'   💀 {category}: {count} questions')
    
    avg_savage = total_savage_level / len(savage_questions) if savage_questions else 0
    print(f'\n📈 Average Savage Level: {avg_savage:.1f}/6 🔥')
    
    if avg_savage >= 4:
        print('🏆 ACHIEVEMENT UNLOCKED: FRIENDSHIP ANNIHILATOR')
    elif avg_savage >= 3:
        print('🥈 ACHIEVEMENT UNLOCKED: RELATIONSHIP WRECKER')
    else:
        print('🥉 ACHIEVEMENT UNLOCKED: MILD CHAOS CREATOR')
    
    print('\n💀 SIDE EFFECTS MAY INCLUDE:')
    print('   - Complete social destruction')
    print('   - People blocking you on all platforms')
    print('   - Being uninvited from future gatherings')
    print('   - Your friends forming a support group')
    print('   - Legendary status as the savage friend')
    
    print('\n🎉 DISNEY COULD NEVER! 💀')

if __name__ == "__main__":
    main()