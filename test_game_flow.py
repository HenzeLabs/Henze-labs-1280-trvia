#!/usr/bin/env python3
"""
Comprehensive Game Flow Test
Tests the entire trivia game flow end-to-end
"""

import requests
import json
import time
import threading
from typing import Dict, List

class GameFlowTester:
    def __init__(self, base_url: str = "http://localhost:5001"):
        self.base_url = base_url
        self.session = requests.Session()
        self.game_session = None
        self.players = []
        
    def test_route_accessibility(self) -> Dict[str, bool]:
        """Test all main routes are accessible"""
        routes_to_test = [
            "/",
            "/host", 
            "/join",
            "/admin"
        ]
        
        results = {}
        print("🔍 Testing route accessibility...")
        
        for route in routes_to_test:
            try:
                response = self.session.get(f"{self.base_url}{route}")
                results[route] = response.status_code == 200
                status = "✅" if results[route] else "❌"
                print(f"  {status} {route}: {response.status_code}")
            except Exception as e:
                results[route] = False
                print(f"  ❌ {route}: {str(e)}")
                
        return results
    
    def test_game_creation(self) -> Dict[str, any]:
        """Test game session creation"""
        print("\n🎮 Testing game creation...")
        
        try:
            payload = {"host_name": "TestHost"}
            response = self.session.post(f"{self.base_url}/api/game/create", json=payload)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    room_code = data.get('room_code')
                    print(f"  ✅ Game created successfully - Room: {room_code}")
                    return {"success": True, "room_code": room_code}
                else:
                    print(f"  ❌ Game creation failed: {data.get('message')}")
                    return {"success": False, "error": data.get('message')}
            else:
                print(f"  ❌ HTTP {response.status_code}: {response.text}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            print(f"  ❌ Exception: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def test_player_join(self, room_code: str, player_name: str) -> Dict[str, any]:
        """Test player joining a game"""
        print(f"\n👤 Testing player join: {player_name}")
        
        try:
            payload = {
                "room_code": room_code,
                "player_name": player_name
            }
            response = self.session.post(f"{self.base_url}/api/game/join", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    player_id = data.get('player_id')  # Fixed: was looking for player.id
                    self.players.append({
                        'id': player_id,
                        'name': player_name,
                        'room_code': room_code
                    })
                    print(f"  ✅ {player_name} joined - ID: {player_id}")
                    return {"success": True, "player_id": player_id}
                else:
                    print(f"  ❌ Join failed: {data.get('message')}")
                    return {"success": False, "error": data.get('message')}
            else:
                print(f"  ❌ HTTP {response.status_code}: {response.text}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            print(f"  ❌ Exception: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def test_game_start(self, room_code: str) -> Dict[str, any]:
        """Test starting the game"""
        print(f"\n🚀 Testing game start...")
        
        try:
            response = self.session.post(f"{self.base_url}/api/game/start/{room_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"  ✅ Game started successfully")
                    return {"success": True}
                else:
                    print(f"  ❌ Start failed: {data.get('message')}")
                    return {"success": False, "error": data.get('message')}
            else:
                print(f"  ❌ HTTP {response.status_code}: {response.text}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            print(f"  ❌ Exception: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def test_get_question(self, room_code: str) -> Dict[str, any]:
        """Test getting current question"""
        print(f"\n❓ Testing question retrieval...")
        
        try:
            response = self.session.get(f"{self.base_url}/api/game/question/{room_code}")
            
            if response.status_code == 200:
                data = response.json()
                question = data.get('question')
                if question:
                    print(f"  ✅ Question retrieved: {question.get('question_text', '')[:50]}...")
                    return {"success": True, "question": question}
                else:
                    print(f"  ❌ No question found")
                    return {"success": False, "error": "No question"}
            else:
                print(f"  ❌ HTTP {response.status_code}: {response.text}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            print(f"  ❌ Exception: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def test_submit_answer(self, player_id: str, answer: str) -> Dict[str, any]:
        """Test submitting an answer"""
        print(f"  📝 Testing answer submission for player {player_id}...")
        
        try:
            payload = {
                "player_id": player_id,
                "answer": answer
            }
            response = self.session.post(f"{self.base_url}/api/game/answer", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                is_correct = data.get('is_correct', False)
                points = data.get('points_earned', 0)
                status = "✅ Correct" if is_correct else "❌ Wrong"
                print(f"    {status} - Points: {points}")
                return {"success": True, "correct": is_correct, "points": points}
            else:
                print(f"    ❌ HTTP {response.status_code}: {response.text}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            print(f"    ❌ Exception: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def test_leaderboard(self, room_code: str) -> Dict[str, any]:
        """Test leaderboard retrieval"""
        print(f"\n🏆 Testing leaderboard...")
        
        try:
            response = self.session.get(f"{self.base_url}/api/game/leaderboard/{room_code}")
            
            if response.status_code == 200:
                data = response.json()
                leaderboard = data.get('leaderboard', [])
                print(f"  ✅ Leaderboard retrieved ({len(leaderboard)} players)")
                for i, player in enumerate(leaderboard[:3]):
                    print(f"    {i+1}. {player.get('name')} - {player.get('score')} pts")
                return {"success": True, "leaderboard": leaderboard}
            else:
                print(f"  ❌ HTTP {response.status_code}: {response.text}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            print(f"  ❌ Exception: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def test_next_question(self, room_code: str) -> Dict[str, any]:
        """Test moving to next question"""
        print(f"\n➡️  Testing next question...")
        
        try:
            response = self.session.post(f"{self.base_url}/api/game/next/{room_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    if data.get('game_finished'):
                        print(f"  ✅ Game finished")
                        return {"success": True, "finished": True}
                    else:
                        print(f"  ✅ Next question loaded")
                        return {"success": True, "finished": False}
                else:
                    print(f"  ❌ Next question failed: {data.get('message')}")
                    return {"success": False, "error": data.get('message')}
            else:
                print(f"  ❌ HTTP {response.status_code}: {response.text}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            print(f"  ❌ Exception: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def run_full_game_simulation(self):
        """Run a complete game simulation"""
        print("🎯 Starting Full Game Flow Test\n" + "="*50)
        
        # Test 1: Route accessibility
        route_results = self.test_route_accessibility()
        if not all(route_results.values()):
            print("❌ Some routes failed - stopping test")
            return
        
        # Test 2: Game creation
        create_result = self.test_game_creation()
        if not create_result['success']:
            print("❌ Game creation failed - stopping test")
            return
            
        room_code = create_result['room_code']
        
        # Test 3: Player joins
        test_players = ["Alice", "Bob", "Charlie"]
        for player_name in test_players:
            join_result = self.test_player_join(room_code, player_name)
            if not join_result['success']:
                print(f"❌ {player_name} failed to join - continuing with fewer players")
        
        if not self.players:
            print("❌ No players joined - stopping test")
            return
        
        # Test 4: Start game
        start_result = self.test_game_start(room_code)
        if not start_result['success']:
            print("❌ Game start failed - stopping test")
            return
        
        # Test 5: Play a few rounds
        for round_num in range(1, 4):  # Play 3 rounds
            print(f"\n🎮 ROUND {round_num}")
            
            # Get question
            question_result = self.test_get_question(room_code)
            if not question_result['success']:
                print(f"❌ Failed to get question for round {round_num}")
                break
                
            question = question_result['question']
            available_answers = question.get('answers', [])
            
            if not available_answers:
                print(f"❌ No answers available for round {round_num}")
                break
            
            # Each player submits a different answer (some will be correct, some wrong)
            for i, player in enumerate(self.players):
                # Cycle through available answers
                answer = available_answers[i % len(available_answers)]
                self.test_submit_answer(player['id'], answer)
            
            # Check leaderboard
            self.test_leaderboard(room_code)
            
            # Move to next question
            next_result = self.test_next_question(room_code)
            if next_result.get('finished'):
                print("🏁 Game finished!")
                break
        
        # Final leaderboard
        print("\n🏆 FINAL RESULTS")
        self.test_leaderboard(room_code)
        
        print("\n✅ Game flow test completed!")

def main():
    print("🎯 1280 Trivia Game Flow Validator")
    print("="*50)
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:5001")
        if response.status_code != 200:
            print("❌ Server not accessible at http://localhost:5001")
            print("Please start the server with: python3 run_server.py")
            return
    except:
        print("❌ Server not running at http://localhost:5001")
        print("Please start the server with: python3 run_server.py")
        return
    
    print("✅ Server is running, starting tests...\n")
    
    tester = GameFlowTester()
    tester.run_full_game_simulation()

if __name__ == "__main__":
    main()