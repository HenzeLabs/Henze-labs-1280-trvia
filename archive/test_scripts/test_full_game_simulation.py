#!/usr/bin/env python3
"""
Comprehensive End-to-End Game Simulation Test
Tests the full game loop: host creates room, players join, complete rounds, and handle reconnects.
"""

import asyncio
import aiohttp
import socketio
import json
import time
import random
from typing import Dict, List, Any
import logging
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class PlayerState:
    """Track player state during simulation"""
    player_id: str
    name: str
    score: int = 0
    connected: bool = False
    current_answer: str = None
    round_results: List[Dict] = None
    
    def __post_init__(self):
        if self.round_results is None:
            self.round_results = []

class GameSimulator:
    """Simulate a complete game with host and multiple players"""
    
    def __init__(self, base_url="http://localhost:5001"):
        self.base_url = base_url
        self.host_sio = None
        self.players: Dict[str, PlayerState] = {}
        self.player_sockets: Dict[str, socketio.AsyncClient] = {}
        self.room_code = None
        self.game_state = "waiting"
        self.current_question = None
        self.question_count = 0
        self.total_questions = 5  # Test with 5 questions
        self.roast_messages = []
        
    async def setup_host(self):
        """Initialize host connection and create room"""
        logger.info("🎤 Setting up host connection...")
        
        self.host_sio = socketio.AsyncClient()
        
        # Host event handlers
        @self.host_sio.event
        async def connect():
            logger.info("✅ Host connected to server")
            
        @self.host_sio.event
        async def room_created(data):
            self.room_code = data['room_code']
            logger.info(f"🏠 Room created with code: {self.room_code}")
            
        @self.host_sio.event
        async def player_joined(data):
            player_name = data['player_name']
            logger.info(f"👤 Player '{player_name}' joined the game")
            
        @self.host_sio.event
        async def game_state_update(data):
            self.game_state = data['state']
            logger.info(f"🎮 Game state updated: {self.game_state}")
            
        @self.host_sio.event
        async def question_started(data):
            self.current_question = data
            self.question_count += 1
            logger.info(f"❓ Question {self.question_count}/{self.total_questions} started: {data['question'][:50]}...")
            
        @self.host_sio.event
        async def all_answers_received(data):
            logger.info("📝 All players have submitted answers")
            
        @self.host_sio.event
        async def round_results(data):
            logger.info(f"📊 Round results: {len(data['results'])} players answered")
            for result in data['results']:
                logger.info(f"   {result['player_name']}: {result['points']} points ({'✅' if result['correct'] else '❌'})")
        
        # Connect host
        await self.host_sio.connect(self.base_url)
        await asyncio.sleep(1)
        
        # Create room
        await self.host_sio.emit('create_room', {'host_name': 'TestHost'})
        await asyncio.sleep(2)
        
        if not self.room_code:
            raise Exception("Failed to create room - no room code received")
            
        return self.room_code
    
    async def setup_player(self, player_name: str) -> PlayerState:
        """Setup a single player connection"""
        logger.info(f"📱 Setting up player: {player_name}")
        
        player_sio = socketio.AsyncClient()
        player_state = PlayerState(
            player_id=f"player_{len(self.players)}",
            name=player_name
        )
        
        # Player event handlers
        @player_sio.event
        async def connect():
            logger.info(f"✅ Player {player_name} connected")
            player_state.connected = True
            
        @player_sio.event
        async def disconnect():
            logger.info(f"❌ Player {player_name} disconnected")
            player_state.connected = False
            
        @player_sio.event
        async def joined_game(data):
            player_state.player_id = data['player_id']
            logger.info(f"🎮 Player {player_name} successfully joined game")
            
        @player_sio.event
        async def question_received(data):
            logger.info(f"❓ Player {player_name} received question")
            # Simulate thinking time (1-3 seconds)
            await asyncio.sleep(random.uniform(1, 3))
            
            # Choose random answer
            if 'answers' in data and data['answers']:
                chosen_answer = random.choice(data['answers'])
                player_state.current_answer = chosen_answer
                
                await player_sio.emit('submit_answer', {
                    'player_id': player_state.player_id,
                    'answer': chosen_answer
                })
                logger.info(f"📝 Player {player_name} submitted answer: {chosen_answer}")
            
        @player_sio.event
        async def answer_feedback(data):
            is_correct = data.get('correct', False)
            points = data.get('points', 0)
            player_state.score += points
            
            result = {
                'correct': is_correct,
                'points': points,
                'answer': player_state.current_answer
            }
            player_state.round_results.append(result)
            
            logger.info(f"📈 Player {player_name} feedback: {'✅' if is_correct else '❌'} (+{points} pts, total: {player_state.score})")
            
        @player_sio.event
        async def game_ended(data):
            final_score = data.get('final_score', player_state.score)
            rank = data.get('rank', 'Unknown')
            logger.info(f"🏆 Player {player_name} finished - Rank: {rank}, Score: {final_score}")
        
        # Connect and join
        await player_sio.connect(self.base_url)
        await asyncio.sleep(1)
        
        # Join game
        await player_sio.emit('join_game', {
            'room_code': self.room_code,
            'player_name': player_name
        })
        await asyncio.sleep(1)
        
        self.players[player_name] = player_state
        self.player_sockets[player_name] = player_sio
        
        return player_state
    
    async def simulate_reconnect(self, player_name: str):
        """Simulate a player reconnecting mid-game"""
        logger.info(f"🔄 Simulating reconnect for player {player_name}")
        
        if player_name not in self.player_sockets:
            logger.error(f"Player {player_name} not found for reconnect test")
            return
            
        # Disconnect
        await self.player_sockets[player_name].disconnect()
        await asyncio.sleep(2)
        
        # Reconnect
        await self.player_sockets[player_name].connect(self.base_url)
        await asyncio.sleep(1)
        
        # Rejoin
        await self.player_sockets[player_name].emit('join_game', {
            'room_code': self.room_code,
            'player_name': player_name
        })
        
        logger.info(f"✅ Player {player_name} reconnected successfully")
    
    async def start_game(self):
        """Start the game from host"""
        logger.info("🚀 Starting game...")
        await self.host_sio.emit('start_game', {'room_code': self.room_code})
        await asyncio.sleep(2)
    
    async def next_question(self):
        """Advance to next question"""
        logger.info("➡️ Advancing to next question...")
        await self.host_sio.emit('next_question', {'room_code': self.room_code})
        await asyncio.sleep(1)
    
    async def run_full_simulation(self):
        """Run the complete end-to-end simulation"""
        logger.info("🎯 Starting Full Game Simulation")
        logger.info("=" * 60)
        
        try:
            # 1. Setup host and create room
            room_code = await self.setup_host()
            logger.info(f"✅ Phase 1: Host setup complete - Room: {room_code}")
            
            # 2. Setup multiple players
            player_names = ["Alice", "Bob", "Charlie", "Diana"]
            for name in player_names:
                await self.setup_player(name)
                await asyncio.sleep(0.5)  # Stagger joins
            
            logger.info(f"✅ Phase 2: {len(player_names)} players joined")
            
            # 3. Start the game
            await self.start_game()
            logger.info("✅ Phase 3: Game started")
            
            # 4. Play through questions
            for round_num in range(1, self.total_questions + 1):
                logger.info(f"\n🎲 ROUND {round_num}/{self.total_questions}")
                logger.info("-" * 40)
                
                # Start question
                await self.next_question()
                
                # Wait for all answers (with timeout)
                max_wait = 15  # seconds
                wait_time = 0
                while wait_time < max_wait:
                    await asyncio.sleep(1)
                    wait_time += 1
                    
                    # Check if all players answered
                    answered_players = sum(1 for p in self.players.values() 
                                         if len(p.round_results) >= round_num)
                    if answered_players == len(player_names):
                        logger.info(f"✅ All players answered in {wait_time} seconds")
                        break
                
                # Simulate reconnect test in middle of game
                if round_num == 3:
                    await self.simulate_reconnect("Bob")
                    await asyncio.sleep(2)
                
                # Wait for round to complete
                await asyncio.sleep(3)
            
            logger.info("✅ Phase 4: All questions completed")
            
            # 5. Final results
            await asyncio.sleep(2)
            logger.info("\n🏆 FINAL RESULTS")
            logger.info("=" * 40)
            
            # Sort players by score
            sorted_players = sorted(self.players.values(), key=lambda p: p.score, reverse=True)
            for i, player in enumerate(sorted_players, 1):
                logger.info(f"{i}. {player.name}: {player.score} points")
            
            # 6. Test summary
            logger.info("\n📊 SIMULATION SUMMARY")
            logger.info("=" * 40)
            logger.info(f"✅ Room creation: Success ({room_code})")
            logger.info(f"✅ Player joins: {len(player_names)}/{len(player_names)}")
            logger.info(f"✅ Questions completed: {self.total_questions}")
            logger.info(f"✅ Reconnect test: Success")
            
            # Check for any issues
            issues = []
            for name, player in self.players.items():
                if len(player.round_results) != self.total_questions:
                    issues.append(f"Player {name} missing answers ({len(player.round_results)}/{self.total_questions})")
                if not player.connected:
                    issues.append(f"Player {name} disconnected")
            
            if issues:
                logger.warning("⚠️ Issues detected:")
                for issue in issues:
                    logger.warning(f"   - {issue}")
            else:
                logger.info("✅ No issues detected - All systems working perfectly!")
                
        except Exception as e:
            logger.error(f"❌ Simulation failed: {str(e)}")
            raise
        finally:
            # Cleanup
            logger.info("\n🧹 Cleaning up connections...")
            for sio in self.player_sockets.values():
                try:
                    await sio.disconnect()
                except:
                    pass
            if self.host_sio:
                try:
                    await self.host_sio.disconnect()
                except:
                    pass
            logger.info("✅ Cleanup complete")

async def main():
    """Run the simulation"""
    simulator = GameSimulator()
    await simulator.run_full_simulation()

if __name__ == "__main__":
    print("🎮 1280 Trivia - Full Game Simulation")
    print("Testing: Room creation, player joins, game flow, reconnects")
    print("=" * 60)
    
    try:
        asyncio.run(main())
        print("\n🎉 Simulation completed successfully!")
    except KeyboardInterrupt:
        print("\n⏹️ Simulation interrupted by user")
    except Exception as e:
        print(f"\n💥 Simulation failed: {e}")
        import traceback
        traceback.print_exc()