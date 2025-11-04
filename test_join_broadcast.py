#!/usr/bin/env python3
"""
Join Event → Host Broadcast Integration Test
Tests that a player join event triggers a broadcast to the host dashboard
"""

import socketio
import time
import requests
import json
import threading
from typing import Dict, Any


class JoinBroadcastTester:
    def __init__(self, base_url: str = "http://localhost:5001"):
        self.base_url = base_url
        self.host_socket = None
        self.player_socket = None
        self.host_events = []
        self.player_events = []
        self.room_code = None
        
    def create_host_socket(self):
        """Create host socket and event handlers"""
        self.host_socket = socketio.Client()
        
        @self.host_socket.event
        def connect():
            print("🏠 Host connected to WebSocket")
            
        @self.host_socket.event
        def player_list_updated(data):
            print(f"🏠 Host received player_list_updated: {data}")
            self.host_events.append(('player_list_updated', data))
            
        @self.host_socket.event
        def disconnect():
            print("🏠 Host disconnected")
        
        try:
            self.host_socket.connect(self.base_url)
            time.sleep(0.2)  # Give time for connection
            return True
        except Exception as e:
            print(f"❌ Host socket failed: {e}")
            return False
    
    def create_player_socket(self, player_name: str):
        """Create player socket and event handlers"""
        self.player_socket = socketio.Client()
        
        @self.player_socket.event
        def connect():
            print(f"👤 {player_name} connected to WebSocket")
            
        @self.player_socket.event
        def player_list_updated(data):
            print(f"👤 {player_name} received player_list_updated: {data}")
            self.player_events.append(('player_list_updated', data))
            
        @self.player_socket.event
        def disconnect():
            print(f"👤 {player_name} disconnected")
        
        try:
            self.player_socket.connect(self.base_url)
            time.sleep(0.2)  # Give time for connection
            return True
        except Exception as e:
            print(f"❌ {player_name} socket failed: {e}")
            return False
    
    def create_game_session(self):
        """Create a game session via HTTP API"""
        try:
            response = requests.post(f"{self.base_url}/api/game/create", 
                                   json={"host_name": "TestHost"})
            if response.status_code == 200:
                data = response.json()
                self.room_code = data['room_code']
                print(f"✅ Game session created: {self.room_code}")
                return True
            else:
                print(f"❌ Game creation failed: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Game creation error: {e}")
            return False
    
    def join_host_to_room(self):
        """Have host join the room to receive broadcasts"""
        if not self.host_socket or not self.room_code:
            return False
            
        try:
            # Host joins the room to receive broadcasts
            self.host_socket.emit('join_room', {
                'room_code': self.room_code,
                'player_id': 'host_dashboard'
            })
            print(f"🏠 Host joined room {self.room_code}")
            time.sleep(0.2)  # Give time for join to process
            return True
        except Exception as e:
            print(f"❌ Host join room failed: {e}")
            return False
        """Have player join room via WebSocket event"""
        if not self.player_socket or not self.room_code:
            return False
            
        try:
            # Emit join_room event
            self.player_socket.emit('join_room', {
                'room_code': self.room_code,
                'player_id': f'test_{player_name}'
            })
            print(f"👤 {player_name} emitted join_room event")
            return True
        except Exception as e:
            print(f"❌ Join room emit failed: {e}")
            return False
    
    def join_game_via_http(self, player_name: str):
        """Have player join game via HTTP API"""
        if not self.room_code:
            return False
            
        try:
            response = requests.post(f"{self.base_url}/api/game/join", 
                                   json={
                                       "room_code": self.room_code,
                                       "player_name": player_name
                                   })
            if response.status_code == 200:
                print(f"✅ {player_name} joined via HTTP")
                return True
            else:
                print(f"❌ HTTP join failed: {response.text}")
                return False
        except Exception as e:
            print(f"❌ HTTP join error: {e}")
            return False
    
    def run_integration_test(self):
        """Run the complete integration test"""
        print("🔌 Join Event → Host Broadcast Integration Test")
        print("=" * 55)
        
        # Step 1: Create sockets
        print("\n📋 Step 1: Setting up WebSocket connections...")
        if not self.create_host_socket():
            return False
            
        if not self.create_player_socket("TestPlayer"):
            return False
            
        # Step 2: Create game session
        print("\n📋 Step 2: Creating game session...")
        if not self.create_game_session():
            return False
            
        # Step 2.5: Host joins the room to receive broadcasts
        print("\n📋 Step 2.5: Host joining room for broadcasts...")
        if not self.join_host_to_room():
            return False
            
        # Step 3: Clear any initial events
        self.host_events.clear()
        self.player_events.clear()
        
        # Step 4: Join game via HTTP (this should trigger broadcast)
        print("\n📋 Step 3: Player joins game via HTTP...")
        if not self.join_game_via_http("TestPlayer"):
            return False
            
        # Step 5: Wait for events to propagate
        print("\n📋 Step 4: Waiting for broadcast events...")
        time.sleep(1.0)  # Give time for events to propagate
        
        # Step 6: Verify host received player_list_updated
        print("\n📋 Step 5: Verifying host received broadcast...")
        host_broadcasts = [event for event in self.host_events if event[0] == 'player_list_updated']
        
        if len(host_broadcasts) > 0:
            print("✅ SUCCESS: Host received player_list_updated broadcast!")
            broadcast_data = host_broadcasts[-1][1]  # Get latest broadcast
            players = broadcast_data.get('players', [])
            total_players = broadcast_data.get('total_players', 0)
            
            print(f"   📊 Broadcast data: {total_players} players")
            for player in players:
                print(f"   👤 Player: {player.get('name', 'Unknown')} (ID: {player.get('id', 'Unknown')})")
                
            # Verify player data is correct
            if total_players > 0 and any(p.get('name') == 'TestPlayer' for p in players):
                print("✅ Player data correctly included in broadcast")
                return True
            else:
                print("❌ Player data missing or incorrect in broadcast")
                return False
        else:
            print("❌ FAILURE: Host did not receive player_list_updated broadcast")
            print(f"   Host events received: {[e[0] for e in self.host_events]}")
            return False
    
    def cleanup(self):
        """Clean up socket connections"""
        try:
            if self.host_socket and self.host_socket.connected:
                self.host_socket.disconnect()
            if self.player_socket and self.player_socket.connected:
                self.player_socket.disconnect()
        except:
            pass


def main():
    tester = JoinBroadcastTester()
    
    try:
        success = tester.run_integration_test()
        
        if success:
            print("\n🎉 JOIN BROADCAST INTEGRATION TEST PASSED!")
            print("   ✅ Player join triggers host broadcast")
            print("   ✅ Broadcast contains correct player data") 
            print("   ✅ Real-time communication working")
        else:
            print("\n❌ JOIN BROADCAST INTEGRATION TEST FAILED!")
            print("   Check server logs for WebSocket errors")
            
        return success
        
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        return False
    except Exception as e:
        print(f"\n💥 Test failed with exception: {e}")
        return False
    finally:
        tester.cleanup()


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)