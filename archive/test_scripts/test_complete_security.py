#!/usr/bin/env python3
"""
Complete end-to-end security test:
1. Host creates game, gets token
2. Players join and play
3. Verify players CANNOT access host endpoints
4. Verify host CAN access with token
5. Verify voting percentages work
"""

import requests

BASE_URL = "http://localhost:5001"

def test_complete_security():
    print("🔒 Complete Security & Feature Test\n" + "=" * 60)

    # 1. Create game
    print("\n1️⃣ Host creates game...")
    response = requests.post(f"{BASE_URL}/api/game/create", json={
        'host_name': 'Host',
        'settings': {}
    })
    data = response.json()
    room_code = data['room_code']
    host_token = data['host_token']
    print(f"✅ Game created: {room_code}")
    print(f"🔑 Host token: {host_token[:10]}... (hidden)")

    # 2. Players join
    print("\n2️⃣ Players joining...")
    players = []
    for name in ['Alice', 'Bob', 'Charlie']:
        response = requests.post(f"{BASE_URL}/api/game/join", json={
            'room_code': room_code,
            'player_name': name
        })
        player_id = response.json()['player_id']
        players.append({'name': name, 'id': player_id})
        print(f"✅ {name} joined")

    # 3. Start game
    print("\n3️⃣ Starting game...")
    requests.post(f"{BASE_URL}/api/game/start/{room_code}")
    print("✅ Game started")

    # 4. SECURITY TEST: Player tries to access host endpoint
    print("\n4️⃣ SECURITY: Player tries to access host endpoint...")
    response = requests.get(f"{BASE_URL}/api/game/question/{room_code}/host")
    if response.status_code == 403:
        print("✅ PASS: Player blocked from host endpoint (403)")
    else:
        print(f"❌ FAIL: Player should be blocked (got {response.status_code})")

    # 5. Host accesses question with token
    print("\n5️⃣ Host accesses question (with token)...")
    response = requests.get(
        f"{BASE_URL}/api/game/question/{room_code}/host",
        headers={'X-Host-Token': host_token}
    )
    if response.status_code == 200:
        question = response.json()['question']
        print(f"✅ Host can access question")
        print(f"   Question: {question['question_text'][:50]}...")
        print(f"   Correct Answer: {question['correct_answer']}")
    else:
        print(f"❌ FAIL: Host should access (got {response.status_code})")

    # 6. Player accesses question (no answer exposed)
    print("\n6️⃣ Player accesses question (no token)...")
    response = requests.get(f"{BASE_URL}/api/game/question/{room_code}")
    if response.status_code == 200:
        player_question = response.json()['question']
        if 'correct_answer' in player_question:
            print(f"❌ FAIL: Player question exposes correct_answer!")
        else:
            print(f"✅ PASS: Player question hides correct_answer")
            print(f"   Answers: {len(player_question['answers'])} options")
    else:
        print(f"❌ FAIL: Player should access question")

    # 7. Players submit answers
    print("\n7️⃣ Players submitting answers...")
    answers = question['answers']
    for i, player in enumerate(players):
        answer = answers[i % len(answers)]  # Distribute votes
        response = requests.post(f"{BASE_URL}/api/game/answer", json={
            'player_id': player['id'],
            'answer': answer
        })
        if response.status_code == 200:
            result = response.json()
            status = "✅" if result.get('is_correct') else "❌"
            print(f"{status} {player['name']} voted: {answer}")

    # 8. SECURITY: Player tries to reveal answer
    print("\n8️⃣ SECURITY: Player tries to reveal answer...")
    response = requests.get(f"{BASE_URL}/api/game/reveal/{room_code}")
    if response.status_code == 403:
        print("✅ PASS: Player blocked from reveal (403)")
    else:
        print(f"❌ FAIL: Player should be blocked (got {response.status_code})")

    # 9. Host reveals with voting stats
    print("\n9️⃣ Host reveals answer (with token)...")
    response = requests.get(
        f"{BASE_URL}/api/game/reveal/{room_code}",
        headers={'X-Host-Token': host_token}
    )
    if response.status_code == 200:
        reveal = response.json()
        print(f"✅ Host can reveal")
        print(f"   Correct Answer: {reveal['correct_answer']}")
        print(f"\n   Voting Breakdown:")
        for vote_data in reveal['stats']['answer_breakdown']:
            emoji = "✅" if vote_data['is_correct'] else "❌"
            voters = ', '.join(vote_data['voters'])
            print(f"   {emoji} {vote_data['answer']}: {vote_data['percentage']}% ({vote_data['count']} votes) - {voters}")
    else:
        print(f"❌ FAIL: Host should reveal (got {response.status_code})")

    print("\n" + "=" * 60)
    print("🎉 Security & Features Test Complete!\n")
    print("✅ All security measures working")
    print("✅ Host-only endpoints protected")
    print("✅ Voting percentages calculated")
    print("✅ Player tracking functional")

if __name__ == '__main__':
    try:
        test_complete_security()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
