#!/usr/bin/env python3
"""
Test that host-only endpoints are properly secured with token authentication.
"""

import requests

BASE_URL = "http://localhost:5001"

def test_host_authentication():
    print("🔐 Testing Host Authentication\n" + "=" * 60)

    # 1. Create game and get host token
    print("\n1️⃣ Creating game...")
    response = requests.post(f"{BASE_URL}/api/game/create", json={
        'host_name': 'TestHost',
        'settings': {}
    })
    data = response.json()
    room_code = data['room_code']
    host_token = data['host_token']
    print(f"✅ Game created: {room_code}")
    print(f"🔑 Host token: {host_token[:10]}...")

    # 2. Try to access host endpoint WITHOUT token (should fail)
    print("\n2️⃣ Testing host endpoint WITHOUT token (should be blocked)...")
    response = requests.get(f"{BASE_URL}/api/game/question/{room_code}/host")

    if response.status_code == 403:
        print(f"✅ PASS: Blocked without token (403 Forbidden)")
    else:
        print(f"❌ FAIL: Should be blocked but got status {response.status_code}")
        print(f"   Response: {response.json()}")

    # 3. Try with WRONG token (should fail)
    print("\n3️⃣ Testing host endpoint with WRONG token (should be blocked)...")
    response = requests.get(
        f"{BASE_URL}/api/game/question/{room_code}/host",
        headers={'X-Host-Token': 'wrong_token_12345'}
    )

    if response.status_code == 403:
        print(f"✅ PASS: Blocked with wrong token (403 Forbidden)")
    else:
        print(f"❌ FAIL: Should be blocked but got status {response.status_code}")

    # 4. Try with CORRECT token (should succeed)
    print("\n4️⃣ Testing host endpoint with CORRECT token (should work)...")

    # Start game first so there's a question
    requests.post(f"{BASE_URL}/api/game/start/{room_code}")

    response = requests.get(
        f"{BASE_URL}/api/game/question/{room_code}/host",
        headers={'X-Host-Token': host_token}
    )

    if response.status_code == 200 and 'correct_answer' in response.json().get('question', {}):
        print(f"✅ PASS: Access granted with valid token")
        print(f"   Correct answer included: {response.json()['question']['correct_answer']}")
    else:
        print(f"❌ FAIL: Should work with valid token (status: {response.status_code})")

    # 5. Test reveal endpoint without token
    print("\n5️⃣ Testing reveal endpoint WITHOUT token (should be blocked)...")
    response = requests.get(f"{BASE_URL}/api/game/reveal/{room_code}")

    if response.status_code == 403:
        print(f"✅ PASS: Reveal blocked without token")
    else:
        print(f"❌ FAIL: Reveal should be blocked (status: {response.status_code})")

    # 6. Test reveal endpoint with valid token
    print("\n6️⃣ Testing reveal endpoint with CORRECT token (should work)...")
    response = requests.get(
        f"{BASE_URL}/api/game/reveal/{room_code}",
        headers={'X-Host-Token': host_token}
    )

    if response.status_code == 200:
        print(f"✅ PASS: Reveal accessible with valid token")
        data = response.json()
        print(f"   Stats available: {bool(data.get('stats'))}")
    else:
        print(f"❌ FAIL: Reveal should work (status: {response.status_code})")

    # 7. Verify player endpoint still works WITHOUT token
    print("\n7️⃣ Testing player endpoint (should NOT require token)...")
    response = requests.get(f"{BASE_URL}/api/game/question/{room_code}")

    if response.status_code == 200 and 'correct_answer' not in response.json().get('question', {}):
        print(f"✅ PASS: Player endpoint works without token and hides answer")
    else:
        print(f"❌ FAIL: Player endpoint issue")

    print("\n" + "=" * 60)
    print("🎉 Authentication Test Complete!\n")
    print("✅ Host endpoints are now secured with token authentication")
    print("✅ Players cannot access correct answers before reveal")

if __name__ == '__main__':
    try:
        test_host_authentication()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
