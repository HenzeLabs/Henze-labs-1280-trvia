#!/usr/bin/env python3
"""
LAUREN ROAST MODE - Special savage questions targeting the creator herself!
"""

import sys
from pathlib import Path
import random

# Add the backend directory to the Python path
backend_path = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_path))

from app.models import Database, Message
from app.config import Config

def generate_lauren_specific_savage_questions():
    """Generate savage questions specifically targeting Lauren."""
    
    # Connect to database to get real Lauren messages
    db = Database(str(Config.DATABASE_PATH))
    message_model = Message(db)
    real_messages = message_model.get_random_messages(limit=200)
    
    # Find Lauren's actual embarrassing messages
    lauren_messages = [msg for msg in real_messages if msg['sender'] == 'You']
    
    print('💀 LAUREN-SPECIFIC SAVAGE QUESTIONS - THE CREATOR GETS DESTROYED')
    print('=' * 70)
    print('🎯 Target: LAUREN (No mercy for the game creator!)')
    print(f'📱 Lauren\'s Messages Found: {len(lauren_messages)}')
    print('=' * 70)
    
    # Show some of Lauren's actual messages for roasting
    if lauren_messages:
        print('\n📱 LAUREN\'S ACTUAL EMBARRASSING MESSAGES:')
        for i, msg in enumerate(lauren_messages[:5], 1):
            text = msg['message_text'][:100] + '...' if len(msg['message_text']) > 100 else msg['message_text']
            print(f'{i}. Lauren said: "{text}"')
    
    # Create savage questions targeting Lauren specifically
    lauren_savage_questions = [
        {
            'category': 'CREATOR GETS ROASTED',
            'question_text': 'Who\'s the absolute genius that created this savage game to roast herself?',
            'correct_answer': 'Lauren',
            'wrong_answers': ['Ian', 'Benny', 'Gina'],
            'context': 'Self-inflicted destruction',
            'difficulty': 5
        },
        {
            'category': 'RECEIPTS & REGRETS',
            'question_text': 'Which mastermind thought it was smart to make a game that exposes everyone\'s secrets?',
            'correct_answer': 'Lauren',
            'wrong_answers': ['Ian', 'Benny', 'Gina'],
            'context': 'Peak chaotic energy',
            'difficulty': 4
        },
        {
            'category': 'SELF-ROAST SUPREME',
            'question_text': 'Who\'s most likely to create their own destruction by making this savage trivia game?',
            'correct_answer': 'Lauren',
            'wrong_answers': ['Ian', 'Benny', 'Gina'],
            'context': 'Self-sabotage level: Expert',
            'difficulty': 6
        },
        {
            'category': 'CREATOR CALLOUT',
            'question_text': 'Which walking chaos decided "let\'s make Cards Against Humanity look like Disney"?',
            'correct_answer': 'Lauren',
            'wrong_answers': ['Ian', 'Benny', 'Gina'],
            'context': 'Big brain energy (questionable)',
            'difficulty': 5
        },
        {
            'category': 'FRIENDSHIP DESTROYER',
            'question_text': 'Who\'s the savage mastermind that wanted 10% of questions to be about sex?',
            'correct_answer': 'Lauren',
            'wrong_answers': ['Ian', 'Benny', 'Gina'],
            'context': 'Absolutely unhinged request',
            'difficulty': 6
        }
    ]
    
    # Add real Lauren message roasts if available
    if lauren_messages:
        spicy_lauren_messages = [msg for msg in lauren_messages if any(word in msg['message_text'].lower() for word in ['fuck', 'shit', 'wtf', 'omg', 'sorry', 'help'])]
        
        for msg in spicy_lauren_messages[:3]:
            text = msg['message_text'][:80] + '...' if len(msg['message_text']) > 80 else msg['message_text']
            lauren_savage_questions.append({
                'category': 'LAUREN\'S ACTUAL RECEIPTS',
                'question_text': f'Which absolute trainwreck said: "{text}"?',
                'correct_answer': 'Lauren',
                'wrong_answers': ['Ian', 'Benny', 'Gina'],
                'context': f'Real receipt from {msg.get("chat_name", "the group")}',
                'difficulty': 4
            })
    
    print(f'\n💀 GENERATED {len(lauren_savage_questions)} LAUREN-SPECIFIC ROASTS:')
    
    for i, q in enumerate(lauren_savage_questions, 1):
        print(f'\n🔥 ROUND {i} - {q["category"]}')
        print(f'💀 {q["question_text"]}')
        print('')
        
        # Shuffle answers
        all_answers = [q['correct_answer']] + q['wrong_answers']
        random.shuffle(all_answers)
        
        for j, answer in enumerate(all_answers, 1):
            marker = '💀' if answer == q['correct_answer'] else '  '
            print(f'{marker} {chr(64+j)}) {answer}')
        
        print('')
        print(f'💬 {q["context"]}')
        print(f'🌶️  Savage Level: {"🔥" * q["difficulty"]}')
        
        if i < len(lauren_savage_questions):
            print('-' * 50)
    
    print('\n' + '=' * 70)
    print('🏆 LAUREN ACHIEVEMENT UNLOCKED: SELF-DESTRUCTION MASTER')
    print('💀 You asked for savage content... you got it!')
    print('🎉 No one is safe - especially the game creator!')
    print('😈 Enjoy getting roasted by your own creation!')

if __name__ == "__main__":
    generate_lauren_specific_savage_questions()