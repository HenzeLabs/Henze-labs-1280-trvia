#!/usr/bin/env python3
"""Generate a sample 10-round game to show what 1280 Trivia looks like."""

import sys
from pathlib import Path
import random

# Add the backend directory to the Python path
backend_path = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_path))

from app.generators.question_generator import QuestionGeneratorManager

def main():
    # Initialize the question generator
    generator_manager = QuestionGeneratorManager()

    # Mock some sample messages for chat-based questions
    sample_messages = [
        {'sender': 'Alex', 'message_text': 'I can\'t believe I locked myself out in my underwear AGAIN', 'timestamp': '2024-01-15'},
        {'sender': 'Jordan', 'message_text': 'Why did I wake up with a traffic cone in my room?', 'timestamp': '2024-01-20'},
        {'sender': 'Taylor', 'message_text': 'I may have accidentally joined a CrossFit cult', 'timestamp': '2024-02-01'},
        {'sender': 'Casey', 'message_text': 'Just ordered 200 dollars worth of DoorDash at 3am... no regrets', 'timestamp': '2024-02-10'},
        {'sender': 'Riley', 'message_text': 'Update: still haven\'t left my apartment today', 'timestamp': '2024-02-15'},
        {'sender': 'Morgan', 'message_text': 'Accidentally sent my boss a selfie instead of the quarterly report', 'timestamp': '2024-02-20'},
        {'sender': 'Alex', 'message_text': 'Pro tip: don\'t drunk order a pet snake', 'timestamp': '2024-02-25'},
        {'sender': 'Jordan', 'message_text': 'Currently hiding in the bathroom at this networking event', 'timestamp': '2024-03-01'},
        {'sender': 'Taylor', 'message_text': 'I think I just agreed to run a marathon. Help.', 'timestamp': '2024-03-05'},
        {'sender': 'Casey', 'message_text': 'Breaking: I survived my first Pilates class without crying', 'timestamp': '2024-03-10'}
    ]

    # Generate 10 questions for a sample game
    questions = generator_manager.generate_question_set(sample_messages, num_questions=10)
    
    # Add some manual "Receipts" questions since the generator needs chat_name
    manual_receipts = [
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
            'correct_answer': 'Jordan',
            'wrong_answers': ['Alex', 'Taylor', 'Casey'],
            'context': 'chat:Rooftop Crew',
            'difficulty': 2
        },
        {
            'category': 'Receipts',
            'question_type': 'who_said_this', 
            'question_text': 'Who said: "Just ordered 200 dollars worth of DoorDash at 3am... no regrets"?',
            'correct_answer': 'Casey',
            'wrong_answers': ['Alex', 'Jordan', 'Taylor'],
            'context': 'chat:Midnight Confessions',
            'difficulty': 2
        }
    ]
    
    # Replace some questions with receipts to get a good mix
    questions = questions[:7] + manual_receipts
    random.shuffle(questions)

    print('🎮 SAMPLE 1280 TRIVIA GAME - 10 ROUNDS')
    print('=' * 60)
    print('🏠 Room Code: ABC123')
    print('👥 Players: Alex, Jordan, Taylor, Casey, Riley, Morgan')
    print('=' * 60)

    for i, q in enumerate(questions, 1):
        print(f'\n🔥 ROUND {i} - {q["category"]}')
        print(f'❓ {q["question_text"]}')
        print('')
        
        # Shuffle answers for display
        all_answers = [q['correct_answer']] + q['wrong_answers']
        random.shuffle(all_answers)
        
        for j, answer in enumerate(all_answers, 1):
            marker = '✅' if answer == q['correct_answer'] else '  '
            print(f'{marker} {chr(64+j)}) {answer}')
        
        print('')
        print(f'💬 {q.get("context", "General knowledge")}')
        print(f'🌶️  Spice Level: {"🔥" * q.get("difficulty", 1)}')
        
        if i < len(questions):
            print('-' * 40)

    print('\n' + '=' * 60)
    print('🏆 Game Summary:')
    
    # Count question types
    category_counts = {}
    for q in questions:
        cat = q['category']
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    for category, count in category_counts.items():
        print(f'   {category}: {count} questions')
    
    print(f'\n🎯 Total Questions: {len(questions)}')
    print('💀 Roast Level: Maximum Savage')
    print('🎉 Ready to expose your friends!')

if __name__ == "__main__":
    main()