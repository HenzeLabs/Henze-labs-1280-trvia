#!/usr/bin/env python3
"""
WebSocket Communication Validator
Tests real-time communication between host and players
"""

import socketio
import time
import threading
import json
import requests
from typing import Dict, List

class WebSocketTester:
    def __init__(self, base_url: str = "http://localhost:5001"):
        self.base_url = base_url
        self.host_socket = None
        self.player_sockets = []
        self.player_ids = {}  # Store actual player IDs from join responses
        self.events_received = {
            'host': [],
            'players': [[] for _ in range(3)]  # Track for 3 players
        }
        
    def create_host_socket(self):
        """Create and configure host socket"""
        self.host_socket = socketio.Client()
        
        @self.host_socket.event
        def connect():
            print("🏠 Host connected to WebSocket")
            
        @self.host_socket.event
        def player_list_updated(data):
            print(f"🏠 Host received player_list_updated: {len(data.get('players', []))} players")
            self.events_received['host'].append(('player_list_updated', data))
            
        @self.host_socket.event
        def player_answered(data):
            print(f"🏠 Host received player_answered: {data}")
            self.events_received['host'].append(('player_answered', data))
        
        try:
            self.host_socket.connect(self.base_url)
            time.sleep(0.1)  # Give time for connection to establish
            return True
        except Exception as e:
            print(f"❌ Host socket connection failed: {e}")
            return False
    
    def create_player_socket(self, player_index: int, player_name: str):
        """Create and configure player socket"""
        player_socket = socketio.Client()
        
        @player_socket.event
        def connect():
            print(f"👤 {player_name} connected to WebSocket")
            
        @player_socket.event  
        def game_started():
            print(f"👤 {player_name} received game_started")
            self.events_received['players'][player_index].append(('game_started', {}))
            
        @player_socket.event
        def new_question(data):
            question_text = data.get('question', {}).get('question_text', 'Unknown')
            print(f"👤 {player_name} received new_question: {question_text[:30]}...")
            self.events_received['players'][player_index].append(('new_question', data))
            
        @player_socket.event
        def game_finished(data):
            print(f"👤 {player_name} received game_finished")
            self.events_received['players'][player_index].append(('game_finished', data))
            
        @player_socket.event
        def player_list_updated(data):
            print(f"👤 {player_name} received player_list_updated: {len(data.get('players', []))} players")
            self.events_received['players'][player_index].append(('player_list_updated', data))
        
        try:
            player_socket.connect(self.base_url)
            time.sleep(0.1)  # Give time for connection to establish
            self.player_sockets.append((player_socket, player_name))
            return player_socket
        except Exception as e:
            print(f"❌ {player_name} socket connection failed: {e}")
            return None
    
    def test_room_joining(self, room_code: str):
        """Test WebSocket room joining"""
        print(f"\n🔗 Testing WebSocket Room Joining")
        print("-" * 40)
        
        # Host joins room
        self.host_socket.emit('join_room', {
            'room_code': room_code,
            'player_id': 'host'
        })
        print(f"🏠 Host joined room {room_code}")
        
        # Players join room
        for i, (socket, name) in enumerate(self.player_sockets):
            socket.emit('join_room', {
                'room_code': room_code, 
                'player_id': f'player_{i+1}'
            })
            print(f"👤 {name} joined room {room_code}")
            time.sleep(0.5)  # Small delay to see events
        
        # Wait for events to propagate
        time.sleep(2)
        
        # Check if host received player updates
        host_events = [e for e in self.events_received['host'] if e[0] == 'player_list_updated']
        print(f"✅ Host received {len(host_events)} player list updates")
        
        return len(host_events) > 0
    
    def test_game_start_broadcast(self, room_code: str):
        """Test game start event broadcasting"""
        print(f"\n🚀 Testing Game Start Broadcasting")
        print("-" * 40)
        
        # Simulate game start via HTTP (would trigger WebSocket broadcast)
        import requests
        try:
            response = requests.post(f"{self.base_url}/api/game/start/{room_code}")
            if response.status_code == 200:
                print("✅ Game start HTTP request successful")
            else:
                print(f"❌ Game start failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Game start request failed: {e}")
            return False
        
        # Wait for WebSocket events
        time.sleep(3)
        
        # Check if all players received game_started
        players_got_start = 0
        players_got_question = 0
        
        for i, events in enumerate(self.events_received['players']):
            start_events = [e for e in events if e[0] == 'game_started']
            question_events = [e for e in events if e[0] == 'new_question']
            
            if start_events:
                players_got_start += 1
            if question_events:
                players_got_question += 1
                
        print(f"✅ {players_got_start}/{len(self.player_sockets)} players got game_started")
        print(f"✅ {players_got_question}/{len(self.player_sockets)} players got new_question")
        
        return players_got_start == len(self.player_sockets) and players_got_question == len(self.player_sockets)
    
    def test_answer_submission_events(self, room_code: str):
        """Test answer submission event flow"""
        print(f"\n📝 Testing Answer Submission Events")
        print("-" * 40)
        
        # Get current question to know what to answer
        import requests
        try:
            response = requests.get(f"{self.base_url}/api/game/question/{room_code}")
            if response.status_code == 200:
                question_data = response.json()
                question = question_data.get('question')
                if not question:
                    print("❌ No question available")
                    return False
                    
                available_answers = question['answers']
                print(f"✅ Got question for testing with {len(available_answers)} answer choices")
            else:
                print(f"❌ Failed to get question: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Question request failed: {e}")
            return False
        
        # Submit answers for each player
        for i, (socket, name) in enumerate(self.player_sockets):
            # Each player picks a different answer
            answer = available_answers[i % len(available_answers)]
            
            # Get the actual player ID from our stored IDs
            player_id = self.player_ids.get(name, f'player_{i+1}')
            
            try:
                payload = {
                    'player_id': player_id,
                    'answer': answer
                }
                response = requests.post(f"{self.base_url}/api/game/answer", json=payload)
                if response.status_code == 200:
                    print(f"✅ {name} submitted answer: {answer}")
                else:
                    print(f"❌ {name} answer submission failed")
            except Exception as e:
                print(f"❌ {name} answer request failed: {e}")
        
        # Wait for events
        time.sleep(2)
        
        # Check if host received answer events
        host_answer_events = [e for e in self.events_received['host'] if e[0] == 'player_answered']
        print(f"✅ Host received {len(host_answer_events)} player answer events")
        
        return len(host_answer_events) > 0
    
    def test_connection_resilience(self):
        """Test connection resilience and reconnection"""
        print(f"\n🔄 Testing Connection Resilience")
        print("-" * 40)
        
        if not self.player_sockets:
            print("❌ No player sockets to test")
            return False
            
        # Disconnect and reconnect first player
        first_socket, first_name = self.player_sockets[0]
        
        print(f"🔌 Disconnecting {first_name}")
        first_socket.disconnect()
        time.sleep(1)
        
        print(f"🔌 Reconnecting {first_name}")
        try:
            first_socket.connect(self.base_url)
            print(f"✅ {first_name} reconnected successfully")
            return True
        except Exception as e:
            print(f"❌ {first_name} reconnection failed: {e}")
            return False
    
    def run_websocket_tests(self):
        """Run comprehensive WebSocket tests"""
        print("🔌 WebSocket Communication Validator")
        print("=" * 50)
        
        # Setup sockets
        if not self.create_host_socket():
            return False
            
        player_names = ["Alice", "Bob", "Charlie"]
        for i, name in enumerate(player_names):
            if not self.create_player_socket(i, name):
                print(f"❌ Failed to create socket for {name}")
                return False
        
        print(f"✅ Created {len(self.player_sockets)} player sockets")
        
        # Create a game session for testing
        try:
            response = requests.post(f"{self.base_url}/api/game/create", 
                                   json={"host_name": "TestHost"})
            if response.status_code == 200:
                data = response.json()
                room_code = data['room_code']  # Updated API response format
                print(f"✅ Test game created: {room_code}")
            else:
                print(f"❌ Failed to create test game: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Game creation failed: {e}")
            return False
        
        # Add players to the game session via HTTP
        for i, name in enumerate(player_names):
            try:
                payload = {"room_code": room_code, "player_name": name}
                response = requests.post(f"{self.base_url}/api/game/join", json=payload)
                if response.status_code == 200:
                    data = response.json()
                    player_id = data.get('player_id')
                    self.player_ids[name] = player_id  # Store actual player ID
                    print(f"✅ {name} joined game session (ID: {player_id})")
                else:
                    print(f"❌ {name} failed to join game")
            except Exception as e:
                print(f"❌ {name} join request failed: {e}")
        
        # Run tests
        tests = [
            ("Room Joining", lambda: self.test_room_joining(room_code)),
            ("Game Start Broadcasting", lambda: self.test_game_start_broadcast(room_code)),
            ("Answer Submission Events", lambda: self.test_answer_submission_events(room_code)),
            ("Connection Resilience", self.test_connection_resilience)
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
                status = "✅" if result else "❌"
                print(f"{status} {test_name}: {'PASSED' if result else 'FAILED'}")
            except Exception as e:
                results.append((test_name, False))
                print(f"❌ {test_name}: EXCEPTION - {e}")
        
        # Cleanup
        try:
            if self.host_socket:
                self.host_socket.disconnect()
            for socket, name in self.player_sockets:
                socket.disconnect()
        except:
            pass
        
        # Summary
        passed = sum(1 for _, result in results if result)
        total = len(results)
        print(f"\n📊 WebSocket Tests: {passed}/{total} passed")
        
        return passed == total

def main():
    # Check if server is running
    import requests
    try:
        response = requests.get("http://localhost:5001")
        if response.status_code != 200:
            print("❌ Server not accessible at http://localhost:5001")
            return
    except:
        print("❌ Server not running at http://localhost:5001")
        return
    
    tester = WebSocketTester()
    success = tester.run_websocket_tests()
    
    if success:
        print("\n🎉 All WebSocket tests passed!")
    else:
        print("\n🚨 Some WebSocket tests failed")

if __name__ == "__main__":
    main()