#!/usr/bin/env python3
"""
Question Preview Script - NO SPOILERS MODE
Shows question quality without revealing correct answers.
"""

import sys
sys.path.insert(0, 'backend')

from backend.app.generators.question_generator import QuestionGeneratorManager
from backend.app.parsers.imessage_parser import iMessageParser
from backend.app.config import Config
import random

def preview_questions(num_questions=15, show_options=True):
    """
    Generate and preview questions WITHOUT spoiling correct answers.

    Args:
        num_questions: How many questions to generate
        show_options: Whether to show answer options (shuffled, no indication of correct)
    """
    print("🔍 Question Quality Preview - NO SPOILERS MODE")
    print("=" * 70)
    print("\n⚠️  IMPORTANT: This shows questions WITHOUT revealing correct answers")
    print("   You'll see the question text and shuffled options, but not the solution.\n")

    # Load real messages
    print("📱 Loading chat messages...")
    parser = iMessageParser(
        imessage_db_path=str(Config.IMESSAGE_DB_PATH),
        contact_map=Config.CONTACT_MAP
    )

    all_messages = []
    for chat_name in Config.TARGET_CHATS:
        try:
            chat_messages = parser.get_chat_messages(chat_name, limit=1000, months_back=12)
            all_messages.extend(chat_messages)
            print(f"   ✅ {chat_name}: {len(chat_messages)} messages")
        except Exception as e:
            print(f"   ⚠️ {chat_name}: {e}")

    print(f"\n✅ Total messages loaded: {len(all_messages)}\n")

    # Generate questions
    print(f"🎲 Generating {num_questions} questions...\n")
    manager = QuestionGeneratorManager()
    questions = manager.generate_question_set(all_messages, num_questions=num_questions)

    print("=" * 70)
    print(f"📋 PREVIEW: {len(questions)} Questions Generated\n")

    # Show each question (WITHOUT correct answer)
    for idx, q in enumerate(questions, 1):
        category = q.get('category', 'Unknown')
        q_type = q.get('question_type', 'unknown')
        question_text = q.get('question_text', '')

        # Truncate very long questions for readability
        if len(question_text) > 100:
            display_text = question_text[:100] + "..."
        else:
            display_text = question_text

        print(f"Q{idx}. [{category}]")
        print(f"    {display_text}")
        print(f"    Type: {q_type}")

        # Show shuffled answer options (NO indication of which is correct)
        if show_options:
            all_options = q.get('wrong_answers', []) + [q.get('correct_answer', '')]
            random.shuffle(all_options)  # Shuffle so correct answer isn't obvious

            print("    Options:")
            for option in all_options:
                if option:  # Skip empty options
                    print(f"      • {option}")

        # Quality checks
        checks = []
        if q.get('correct_answer'):
            checks.append("✓ Has answer")
        if len(q.get('wrong_answers', [])) >= 3:
            checks.append("✓ 4 choices")
        if len(question_text) > 10:
            checks.append("✓ Valid text")

        print(f"    Quality: {', '.join(checks)}")
        print()

    print("=" * 70)
    print("✅ Preview Complete!\n")
    print("📊 Question Distribution:")

    # Show category breakdown
    categories = {}
    for q in questions:
        cat = q.get('category', 'Unknown')
        categories[cat] = categories.get(cat, 0) + 1

    for cat, count in sorted(categories.items()):
        print(f"   • {cat}: {count} questions")

    print("\n🎮 Ready to play? These questions look good!")
    print("   (Correct answers are hidden to preserve gameplay)")

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Preview trivia questions without spoilers')
    parser.add_argument('-n', '--num-questions', type=int, default=15,
                        help='Number of questions to generate (default: 15)')
    parser.add_argument('--hide-options', action='store_true',
                        help='Hide answer options entirely (only show question text)')

    args = parser.parse_args()

    try:
        preview_questions(
            num_questions=args.num_questions,
            show_options=not args.hide_options
        )
    except Exception as e:
        print(f"\n❌ Preview failed: {e}")
        import traceback
        traceback.print_exc()
