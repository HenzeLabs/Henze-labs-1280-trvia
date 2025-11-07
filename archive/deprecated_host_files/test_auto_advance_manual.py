#!/usr/bin/env python3
"""
Quick Manual Test Script for Auto-Advance Functionality

This script demonstrates the auto-advance working in real-time.
Run this while your server is running to see the magic happen!
"""

import requests
import time
import json

BASE_URL = "http://localhost:5001/api/game"

def test_auto_advance():
    print("🎮 Testing Jackbox-Style Auto-Advance Functionality")
    print("=" * 60)
    
    # Step 1: Create game
    print("\n📝 Step 1: Creating game...")
    response = requests.post(f"{BASE_URL}/create", json={
        "host_name": "AutoAdvanceTest",
        "num_questions": 3
    })
    data = response.json()
    room_code = data['room_code']
    host_token = data['host_token']
    print(f"✅ Game created! Room code: {room_code}")
    
    # Step 2: Join players
    print("\n👥 Step 2: Adding 2 players...")
    players = []
    for i, name in enumerate(["Alice", "Bob"], 1):
        response = requests.post(f"{BASE_URL}/join", json={
            "room_code": room_code,
            "player_name": name
        })
        player_data = response.json()
        players.append(player_data['player_id'])
        print(f"  ✓ {name} joined (ID: {player_data['player_id']})")
    
    # Step 3: Start game
    print("\n🚀 Step 3: Starting game...")
    response = requests.post(f"{BASE_URL}/start/{room_code}")
    print("✅ Game started!")
    
    time.sleep(1)
    
    # Step 4: Get current question
    print("\n❓ Step 4: Fetching first question...")
    response = requests.get(f"{BASE_URL}/question/{room_code}")
    question = response.json()['question']
    print(f"📖 Question: {question['question_text'][:60]}...")
    print(f"📋 Answers: {', '.join(question['answers'])}")
    
    # Step 5: Both players answer
    print("\n👆 Step 5: Players answering...")
    for i, player_id in enumerate(players, 1):
        # Just pick the first answer
        answer = question['answers'][0]
        response = requests.post(f"{BASE_URL}/answer", json={
            "player_id": player_id,
            "answer": answer
        })
        result = response.json()
        player_name = "Alice" if i == 1 else "Bob"
        print(f"  ✓ {player_name} answered: '{answer}'")
        
        if i == 1:
            # Delay between answers to simulate real gameplay
            print("    ⏳ Waiting 2 seconds for second player...")
            time.sleep(2)
    
    # Step 6: Wait for auto-advance
    print("\n⏱️  Step 6: WAITING FOR AUTO-ADVANCE (5 seconds)...")
    print("     (This is the magic moment - no manual intervention!)")
    
    # Poll for new question
    original_question = question['question_text']
    start_time = time.time()
    
    for countdown in range(5, 0, -1):
        print(f"     ⏳ {countdown}...")
        time.sleep(1)
    
    print("\n🔍 Step 7: Checking if question changed...")
    time.sleep(2)  # Give it an extra second for network
    
    response = requests.get(f"{BASE_URL}/question/{room_code}")
    new_question = response.json()['question']
    elapsed = time.time() - start_time
    
    if new_question['question_text'] != original_question:
        print("✅ SUCCESS! Auto-advance worked!")
        print(f"⏱️  Elapsed time: {elapsed:.1f} seconds")
        print(f"📖 New question: {new_question['question_text'][:60]}...")
        print("\n🎉 " + "=" * 56)
        print("🎉 AUTO-ADVANCE IS WORKING PERFECTLY LIKE JACKBOX!")
        print("🎉 " + "=" * 56)
    else:
        print("❌ Auto-advance may not have triggered")
        print(f"   Question is still: {new_question['question_text'][:60]}...")
    
    # Get game stats
    print("\n📊 Final Stats:")
    response = requests.get(f"{BASE_URL}/stats/{room_code}")
    stats = response.json()
    print(f"  • Phase: {stats['phase']}")
    print(f"  • Question: {stats['current_question']}/{stats['total_questions']}")
    print(f"  • Players answered: {stats['players_answered']}/{stats['total_players']}")

if __name__ == "__main__":
    try:
        test_auto_advance()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to server")
        print("   Make sure your server is running at http://localhost:5001")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
