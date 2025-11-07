#!/usr/bin/env python3
"""
End-to-End Poll Question Test
Tests full game flow with poll questions to ensure:
1. Poll questions generate correctly
2. Votes are recorded without immediate scoring
3. Winner is determined by most votes
4. Points are awarded correctly (150 + 25*votes)
5. Scores update properly in leaderboard
"""

import sys
sys.path.insert(0, 'backend')

from backend.app.game.engine import GameEngine
from backend.app.generators.question_generator import QuestionGeneratorManager
from backend.app.parsers.imessage_parser import iMessageParser
from backend.app.config import Config
import time

def test_full_game_with_polls():
    """Run a complete game with poll questions and verify everything works."""

    print("=" * 80)
    print("🎮 END-TO-END POLL QUESTION TEST")
    print("=" * 80)
    print()

    # Initialize game engine
    engine = GameEngine()
    print("✅ Game engine initialized\n")

    # Load real messages for question generation
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

    # Generate 15 questions (should include 2 polls)
    print("🎲 Generating 15 questions (including 2 poll questions)...")
    manager = QuestionGeneratorManager()
    questions = manager.generate_question_set(all_messages, num_questions=15)

    poll_questions = [q for q in questions if q.get('question_type') == 'poll']
    normal_questions = [q for q in questions if q.get('question_type') != 'poll']

    print(f"   ✅ Generated {len(questions)} total questions")
    print(f"   📊 {len(poll_questions)} poll questions")
    print(f"   📊 {len(normal_questions)} normal questions\n")

    if len(poll_questions) == 0:
        print("❌ ERROR: No poll questions generated!")
        return False

    # Create game session
    print("🎮 Creating game...")
    room_code, host_token = engine.create_session(host_name="TestHost", questions=questions)
    print(f"   ✅ Game created: {room_code}\n")

    # Add 4 players (matching the poll answer options)
    players = ['Benny', 'Gina', 'Ian', 'Lauren']
    player_ids = {}

    print("👥 Adding players...")
    for player_name in players:
        player_id = engine.join_session(room_code, player_name)
        player_ids[player_name] = player_id
        print(f"   ✅ {player_name} joined (ID: {player_id[:8]}...)")
    print()

    # Start game
    print("🚀 Starting game...")
    engine.start_game(room_code)
    print("   ✅ Game started\n")

    # Play through all questions
    for q_num in range(len(questions)):
        question = questions[q_num]
        is_poll = question.get('question_type') == 'poll'

        print("-" * 80)
        print(f"📝 Question {q_num + 1}/{len(questions)}")
        print(f"   Category: {question['category']}")
        print(f"   Type: {question.get('question_type', 'normal')}")
        print(f"   Question: {question['question_text'][:70]}...")

        if is_poll:
            print("\n   🗳️  POLL QUESTION - Testing vote mechanics:")
            print(f"   Available options: {question['wrong_answers'] + [question['correct_answer']]}")

            # For poll questions, simulate voting
            # Let's make Benny get the most votes (3 votes)
            votes = {
                'Benny': 'Benny',    # Benny votes for himself
                'Gina': 'Benny',     # Gina votes for Benny
                'Ian': 'Benny',      # Ian votes for Benny
                'Lauren': 'Lauren'   # Lauren votes for herself
            }

            print("\n   📊 Voting pattern:")
            vote_counts = {}
            for voter, voted_for in votes.items():
                print(f"      {voter} → {voted_for}")
                vote_counts[voted_for] = vote_counts.get(voted_for, 0) + 1

            print(f"\n   Expected winner: Benny ({vote_counts.get('Benny', 0)} votes)")
            expected_points = 150 + (vote_counts.get('Benny', 0) * 25)
            print(f"   Expected points: {expected_points} (150 base + {vote_counts.get('Benny', 0)} × 25 bonus)")

            # Get Benny's score before poll
            benny_score_before = engine.active_sessions[room_code].players[player_ids['Benny']].score
            print(f"\n   Benny's score BEFORE poll: {benny_score_before}")

            # Submit votes
            print("\n   Submitting votes...")
            for player_name, vote in votes.items():
                result = engine.submit_answer(player_ids[player_name], vote)

                # Verify poll vote response
                if not result.get('is_poll'):
                    print(f"   ❌ ERROR: Vote for {player_name} not marked as poll!")
                    return False

                if 'points_earned' in result and result['points_earned'] != 0:
                    print(f"   ❌ ERROR: Points awarded during voting (should be deferred)!")
                    return False

                print(f"      ✅ {player_name}'s vote recorded (no immediate points)")

            # Reveal answer (this triggers vote counting and scoring)
            print("\n   🎯 Revealing poll results...")
            stats = engine.get_answer_stats(room_code)

            if not stats:
                print("   ❌ ERROR: No stats returned!")
                return False

            if not stats.get('is_poll'):
                print("   ❌ ERROR: Stats not marked as poll!")
                return False

            poll_winner = stats.get('poll_winner')
            if not poll_winner:
                print("   ❌ ERROR: No poll winner returned!")
                return False

            print(f"\n   🏆 Poll Winner: {poll_winner['name']}")
            print(f"   📊 Votes received: {poll_winner['votes']}")
            print(f"   💰 Points awarded: {poll_winner['points_earned']}")

            # Verify winner is correct
            if poll_winner['name'] != 'Benny':
                print(f"   ❌ ERROR: Wrong winner! Expected Benny, got {poll_winner['name']}")
                return False

            if poll_winner['votes'] != 3:
                print(f"   ❌ ERROR: Wrong vote count! Expected 3, got {poll_winner['votes']}")
                return False

            if poll_winner['points_earned'] != expected_points:
                print(f"   ❌ ERROR: Wrong points! Expected {expected_points}, got {poll_winner['points_earned']}")
                return False

            # Verify Benny's score increased correctly
            benny_score_after = engine.active_sessions[room_code].players[player_ids['Benny']].score
            print(f"\n   Benny's score AFTER poll: {benny_score_after}")
            print(f"   Score increase: +{benny_score_after - benny_score_before}")

            if benny_score_after - benny_score_before != expected_points:
                print(f"   ❌ ERROR: Score didn't increase correctly!")
                return False

            print("   ✅ Poll scoring verified correctly!")

        else:
            print("\n   📝 Normal question - simulating answers...")
            # For normal questions, just have everyone answer correctly
            correct = question['correct_answer']

            for player_name in players:
                result = engine.submit_answer(player_ids[player_name], correct)
                if result.get('is_correct'):
                    print(f"      ✅ {player_name} answered correctly (+{result.get('points_earned', 0)} pts)")

            # Reveal answer
            stats = engine.get_answer_stats(room_code)

        # Advance to next question (if not last)
        if q_num < len(questions) - 1:
            engine.next_question(room_code)
            print(f"\n   ➡️  Advanced to question {q_num + 2}")

        print()

    # Show final results
    print("=" * 80)
    print("🏆 GAME COMPLETE - FINAL RESULTS")
    print("=" * 80)

    summary = engine.get_session_summary(room_code)

    print("\n📊 Final Leaderboard:")
    for i, player in enumerate(summary['leaderboard'], 1):
        print(f"   {i}. {player['name']}: {player['score']} points")

    print(f"\n🎯 Winner: {summary['winner']['name']} with {summary['winner']['score']} points!")
    print(f"📈 Total Players: {summary['total_players']}")
    print(f"❓ Total Questions: {summary['total_questions']}")
    print(f"📊 Poll Questions: {len(poll_questions)}")

    print("\n" + "=" * 80)
    print("✅ ALL TESTS PASSED!")
    print("=" * 80)
    print("\n✨ Poll question mechanics verified:")
    print("   • Votes recorded without immediate scoring")
    print("   • Winner determined by most votes")
    print("   • Points awarded correctly (150 + 25*votes)")
    print("   • Leaderboard updated properly")
    print()

    return True

if __name__ == '__main__':
    try:
        success = test_full_game_with_polls()
        if not success:
            print("\n❌ TEST FAILED")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 TEST CRASHED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
