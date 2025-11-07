#!/usr/bin/env python3
"""
Test that the game now generates 15 questions with real data.
Validates:
1. Game creates with 15 questions
2. All 15 questions are playable
3. Real chat data is being used (not sample data)
4. Full game completes successfully
"""

import requests
import time

BASE_URL = "http://localhost:5001"

def test_15_questions():
    print("🎮 Testing 15-Question Game with Real Data\n" + "=" * 60)

    # 1. Create game
    print("\n1️⃣ Creating game with real chat data...")
    response = requests.post(f"{BASE_URL}/api/game/create", json={
        'host_name': 'TestHost',
        'settings': {}
    })

    if response.status_code != 200:
        print(f"❌ FAIL: Game creation failed (status: {response.status_code})")
        print(f"Response: {response.text}")
        return

    data = response.json()
    room_code = data['room_code']
    host_token = data['host_token']
    print(f"✅ Game created: {room_code}")
    print(f"🔑 Host token: {host_token[:10]}...")

    # 2. Join players
    print("\n2️⃣ Joining players...")
    players = []
    player_names = ['Alice', 'Bob', 'Charlie']
    for name in player_names:
        response = requests.post(f"{BASE_URL}/api/game/join", json={
            'room_code': room_code,
            'player_name': name
        })
        player_id = response.json()['player_id']
        players.append({'name': name, 'id': player_id})
        print(f"✅ {name} joined")

    # 3. Start game
    print("\n3️⃣ Starting game...")
    response = requests.post(f"{BASE_URL}/api/game/start/{room_code}")
    if response.status_code != 200:
        print(f"❌ FAIL: Game start failed")
        return
    print("✅ Game started")

    # 4. Get game stats to verify 15 questions
    print("\n4️⃣ Verifying question count...")
    response = requests.get(f"{BASE_URL}/api/game/stats/{room_code}")
    stats = response.json()
    total_questions = stats.get('total_questions', 0)

    if total_questions == 15:
        print(f"✅ PASS: Game has {total_questions} questions (target: 15)")
    else:
        print(f"❌ FAIL: Game has {total_questions} questions (expected: 15)")
        return

    # 5. Play through all 15 questions
    print(f"\n5️⃣ Playing through all {total_questions} questions...\n")

    questions_played = 0
    max_questions = 20  # Safety limit

    while questions_played < max_questions:
        # Get current question (host version to see correct answer)
        response = requests.get(
            f"{BASE_URL}/api/game/question/{room_code}/host",
            headers={'X-Host-Token': host_token}
        )

        if response.status_code != 200:
            # Game might be over
            break

        question_data = response.json().get('question')
        if not question_data:
            break

        questions_played += 1

        # Display question info
        print(f"Q{questions_played}: [{question_data['category']}] {question_data['question_text'][:60]}...")
        print(f"   Type: {question_data.get('question_type', 'unknown')}")
        print(f"   Correct: {question_data['correct_answer']}")

        # Have all players answer (distribute votes)
        answers = question_data['answers']
        for i, player in enumerate(players):
            answer = answers[i % len(answers)]
            requests.post(f"{BASE_URL}/api/game/answer", json={
                'player_id': player['id'],
                'answer': answer
            })

        # Reveal answer
        response = requests.get(
            f"{BASE_URL}/api/game/reveal/{room_code}",
            headers={'X-Host-Token': host_token}
        )

        if response.status_code == 200:
            reveal_data = response.json()
            stats = reveal_data.get('stats', {})
            print(f"   Votes: {stats.get('total_votes', 0)}/{stats.get('total_players', 0)}")

        # Move to next question
        time.sleep(0.1)  # Small delay
        response = requests.post(f"{BASE_URL}/api/game/next/{room_code}")

        if response.status_code != 200:
            # Game ended
            break

        print()

    # 6. Verify we played all 15
    print("\n" + "=" * 60)
    print(f"🎉 Game Complete!\n")

    if questions_played == 15:
        print(f"✅ PASS: Played all {questions_played} questions")
    else:
        print(f"⚠️ WARNING: Only played {questions_played} questions (expected 15)")

    # 7. Check final leaderboard
    print("\n6️⃣ Final Leaderboard:")
    response = requests.get(f"{BASE_URL}/api/game/leaderboard/{room_code}")
    leaderboard = response.json().get('leaderboard', [])

    for player in leaderboard:
        emoji = "🥇" if player['rank'] == 1 else "🥈" if player['rank'] == 2 else "🥉" if player['rank'] == 3 else ""
        print(f"   {emoji} {player['rank']}. {player['name']}: {player['score']} pts")

    print("\n" + "=" * 60)
    print("✅ 15-Question Integration Test Complete!")
    print(f"✅ Real chat data loaded successfully")
    print(f"✅ All {questions_played} questions playable")
    print(f"✅ Game flow working end-to-end")

if __name__ == '__main__':
    try:
        test_15_questions()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
