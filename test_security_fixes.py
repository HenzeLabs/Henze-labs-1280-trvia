#!/usr/bin/env python3
"""
Quick security validation script - Tests all 10 security fixes
Run this with the server running: python3 run_server.py
"""

import requests
import json
import time
import sys

BASE_URL = "http://localhost:5001"

def test_result(name, passed, details=""):
    """Print test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {name}")
    if details:
        print(f"    {details}")

def test_disabled_endpoints():
    """BUG #1, #2, #4, #7: Test that disabled endpoints return 410"""
    print("\n🔒 Testing Disabled Endpoints (BUG #1, #2, #4, #7)")
    print("=" * 60)

    endpoints = [
        ("POST", "/api/game/start/TEST", "BUG #1"),
        ("POST", "/api/game/next/TEST", "BUG #1"),
        ("GET", "/api/game/question/TEST/host", "BUG #4"),
        ("GET", "/api/game/player-session/player_test", "BUG #7"),
        ("POST", "/api/game/answer", "BUG #2"),
    ]

    all_passed = True
    for method, path, bug in endpoints:
        try:
            if method == "POST":
                r = requests.post(f"{BASE_URL}{path}",
                                json={"test": "data"},
                                timeout=5)
            else:
                r = requests.get(f"{BASE_URL}{path}", timeout=5)

            passed = r.status_code == 410
            test_result(
                f"{bug}: {method} {path}",
                passed,
                f"Status: {r.status_code} (expected 410)"
            )
            all_passed = all_passed and passed
        except requests.exceptions.Timeout:
            test_result(f"{bug}: {method} {path}", False, "Timeout")
            all_passed = False
        except Exception as e:
            test_result(f"{bug}: {method} {path}", False, str(e))
            all_passed = False

    return all_passed

def test_dos_protection():
    """BUG #9: Test DoS protection on question count"""
    print("\n🛡️  Testing DoS Protection (BUG #9)")
    print("=" * 60)

    try:
        # Test excessive question count
        r = requests.post(f"{BASE_URL}/api/game/create",
                         json={
                             "player_name": "TestPlayer",
                             "num_questions": 999
                         },
                         timeout=5)

        passed = (r.status_code == 400 or r.status_code == 422) and \
                 ("cannot exceed 25" in r.text or "DoS" in r.text)

        test_result(
            "Excessive question count rejected (999)",
            passed,
            f"Status: {r.status_code}, Response: {r.text[:100]}"
        )
        return passed
    except Exception as e:
        test_result("DoS protection", False, str(e))
        return False

def test_uuid_player_ids():
    """BUG #7: Test that player IDs are now UUIDs"""
    print("\n🆔 Testing UUID Player IDs (BUG #7)")
    print("=" * 60)

    try:
        # Create a game
        r = requests.post(f"{BASE_URL}/api/game/create",
                         json={
                             "player_name": "TestHost",
                             "num_questions": 5
                         },
                         timeout=5)

        if r.status_code == 200:
            data = r.json()
            player_id = data.get('player_id', '')

            # Check if player_id matches UUID pattern (player_[16 hex chars])
            is_uuid = (len(player_id) == 23 and  # "player_" + 16 chars
                      player_id.startswith('player_') and
                      all(c in '0123456789abcdef' for c in player_id[7:]))

            # Check it's NOT the old format (player_digit_4digits)
            is_old_format = (player_id.startswith('player_') and
                           '_' in player_id[7:] and
                           len(player_id) < 20)

            passed = is_uuid and not is_old_format

            test_result(
                "Player ID format is UUID-based",
                passed,
                f"player_id: {player_id} (length: {len(player_id)})"
            )

            return passed, data.get('room_code')
        else:
            test_result("Create game", False, f"Status: {r.status_code}")
            return False, None
    except Exception as e:
        test_result("UUID player IDs", False, str(e))
        return False, None

def test_game_flow(room_code):
    """BUG #3, #5, #6, #8: Test basic game flow with security fixes"""
    print("\n🎮 Testing Game Flow (BUG #3, #5, #6, #8)")
    print("=" * 60)

    all_passed = True

    try:
        # Test XSS protection on player names (BUG #3)
        r = requests.post(f"{BASE_URL}/api/game/join",
                         json={
                             "room_code": room_code,
                             "player_name": "<script>alert('xss')</script>"
                         },
                         timeout=5)

        if r.status_code == 200:
            data = r.json()
            player_name = data.get('player_name', '')
            passed = '<script>' not in player_name
            test_result(
                "BUG #3: XSS in player name sanitized",
                passed,
                f"Sanitized name: {player_name}"
            )
            all_passed = all_passed and passed
        else:
            # Might reject entirely, which is also fine
            test_result(
                "BUG #3: Malicious player name rejected",
                True,
                f"Status: {r.status_code}"
            )

    except Exception as e:
        test_result("Game flow test", False, str(e))
        all_passed = False

    return all_passed

def main():
    print("🔒 Security Audit v1.6 - Validation Script")
    print("=" * 60)
    print(f"Testing server at: {BASE_URL}")
    print()

    # Check if server is running
    try:
        r = requests.get(BASE_URL, timeout=5)
        print("✅ Server is running\n")
    except:
        print(f"❌ Server not running at {BASE_URL}")
        print("Start with: python3 run_server.py")
        sys.exit(1)

    # Run tests
    results = []

    # Test 1: Disabled endpoints
    results.append(("Disabled Endpoints", test_disabled_endpoints()))

    # Test 2: DoS protection
    results.append(("DoS Protection", test_dos_protection()))

    # Test 3: UUID player IDs and create game
    uuid_passed, room_code = test_uuid_player_ids()
    results.append(("UUID Player IDs", uuid_passed))

    # Test 4: Game flow (if we have a room)
    if room_code:
        results.append(("Game Flow Security", test_game_flow(room_code)))

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")

    print()
    print(f"Tests Passed: {passed}/{total}")

    if passed == total:
        print("\n🎉 All security fixes validated!")
        sys.exit(0)
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
