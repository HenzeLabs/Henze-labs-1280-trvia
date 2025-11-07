#!/usr/bin/env python3
"""
Quick test to verify the 2 bug fixes:
1. Bug 1: correct_answer in question response
2. Bug 2: player_id in leaderboard response
"""

import requests
import time

BASE_URL = "http://localhost:5001"

def test_bug_fixes():
    print("🔍 Testing Bug Fixes\n" + "=" * 50)

    # Create game
    print("\n1️⃣ Creating game...")
    response = requests.post(f"{BASE_URL}/api/game/create", json={
        'host_name': 'TestHost',
        'settings': {}
    })
    data = response.json()
    room_code = data['room_code']
    print(f"✅ Game created: {room_code}")

    # Join 2 players
    print("\n2️⃣ Joining players...")
    player_ids = []
    for name in ['Alice', 'Bob']:
        response = requests.post(f"{BASE_URL}/api/game/join", json={
            'room_code': room_code,
            'player_name': name
        })
        player_id = response.json()['player_id']
        player_ids.append(player_id)
        print(f"✅ {name} joined: {player_id}")

    # Start game
    print("\n3️⃣ Starting game...")
    response = requests.post(f"{BASE_URL}/api/game/start/{room_code}")
    print(f"✅ Game started")

    # Test Bug 1: Get question and check for correct_answer
    print("\n4️⃣ Testing Bug 1: correct_answer in question response")
    response = requests.get(f"{BASE_URL}/api/game/question/{room_code}")
    question = response.json()['question']

    if 'correct_answer' in question:
        print(f"✅ BUG 1 FIXED: correct_answer field present")
        print(f"   Question: {question['question_text'][:50]}...")
        print(f"   Correct Answer: {question['correct_answer']}")
    else:
        print(f"❌ BUG 1 NOT FIXED: correct_answer field missing")
        print(f"   Available fields: {list(question.keys())}")

    # Submit answers
    print("\n5️⃣ Submitting answers...")
    for player_id in player_ids:
        answer = question['answers'][0]  # Just pick first answer
        response = requests.post(f"{BASE_URL}/api/game/answer", json={
            'player_id': player_id,
            'answer': answer
        })
        print(f"✅ Answer submitted for {player_id}")

    # Test Bug 2: Get leaderboard and check for player_id
    print("\n6️⃣ Testing Bug 2: player_id in leaderboard response")
    response = requests.get(f"{BASE_URL}/api/game/leaderboard/{room_code}")
    leaderboard = response.json()['leaderboard']

    if leaderboard and 'player_id' in leaderboard[0]:
        print(f"✅ BUG 2 FIXED: player_id field present")
        print(f"\nLeaderboard:")
        for entry in leaderboard:
            print(f"   {entry['rank']}. {entry['name']} (ID: {entry['player_id']}) - {entry['score']} pts")
    else:
        print(f"❌ BUG 2 NOT FIXED: player_id field missing")
        if leaderboard:
            print(f"   Available fields: {list(leaderboard[0].keys())}")

    print("\n" + "=" * 50)
    print("🎉 Test Complete!\n")

if __name__ == '__main__':
    try:
        test_bug_fixes()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
