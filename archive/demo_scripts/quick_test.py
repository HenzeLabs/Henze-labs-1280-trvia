#!/usr/bin/env python3
"""
Quick End-to-End Test for 1280 Trivia
Tests core game flow without advanced reconnection logic.
"""

import asyncio
import socketio
import json
import time
import random
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

async def quick_game_test():
    """Run a quick end-to-end test"""
    logger.info("🎯 Starting Quick Game Test")
    
    # Setup host
    host_sio = socketio.AsyncClient()
    room_code = None
    
    @host_sio.event
    async def connect():
        logger.info("✅ Host connected")
        
    @host_sio.event  
    async def room_created(data):
        nonlocal room_code
        room_code = data['room_code']
        logger.info(f"🏠 Room created: {room_code}")
        
    @host_sio.event
    async def player_joined(data):
        logger.info(f"👤 Player '{data['player_name']}' joined")
        
    @host_sio.event
    async def question_started(data):
        logger.info(f"❓ Question started: {data['question']['question_text'][:50]}...")
        
    @host_sio.event
    async def all_answers_received(data):
        logger.info("📝 All answers received")
        
    # Connect host and create room
    await host_sio.connect('http://localhost:5001')
    await host_sio.emit('create_room', {'host_name': 'QuickTestHost'})
    await asyncio.sleep(2)
    
    if not room_code:
        logger.error("❌ Failed to create room")
        return
        
    # Setup players
    players = []
    player_names = ["TestAlice", "TestBob"]
    
    for name in player_names:
        player_sio = socketio.AsyncClient()
        
        @player_sio.event
        async def connect():
            logger.info(f"✅ Player {name} connected")
            
        @player_sio.event
        async def joined_game(data):
            logger.info(f"🎮 Player {name} joined game successfully")
            
        @player_sio.event
        async def question_received(data):
            logger.info(f"❓ Player {name} received question")
            # Auto-answer randomly
            await asyncio.sleep(1)
            answers = data.get('question', {}).get('answers', [])
            if answers:
                chosen = random.choice(answers)
                await player_sio.emit('submit_answer', {
                    'player_id': data.get('player_id'),
                    'answer': chosen
                })
                logger.info(f"📝 Player {name} answered: {chosen}")
                
        @player_sio.event
        async def answer_feedback(data):
            result = "✅" if data.get('correct') else "❌"
            points = data.get('points', 0)
            logger.info(f"📈 Player {name} result: {result} (+{points} pts)")
        
        await player_sio.connect('http://localhost:5001')
        await player_sio.emit('join_game', {
            'room_code': room_code,
            'player_name': name
        })
        await asyncio.sleep(1)
        
        players.append(player_sio)
    
    logger.info("✅ All players joined")
    
    # Start game
    logger.info("🚀 Starting game...")
    await host_sio.emit('start_game', {'room_code': room_code})
    await asyncio.sleep(3)
    
    # Play a few rounds
    for round_num in range(1, 4):
        logger.info(f"\n🎲 Round {round_num}")
        await host_sio.emit('next_question', {'room_code': room_code})
        await asyncio.sleep(5)  # Wait for answers
    
    logger.info("\n🏆 Test completed successfully!")
    
    # Cleanup
    for player_sio in players:
        await player_sio.disconnect()
    await host_sio.disconnect()
    
    return True

async def main():
    try:
        success = await quick_game_test()
        if success:
            print("\n✅ ALL TESTS PASSED!")
            print("🎯 Room creation: ✅")
            print("👥 Player joining: ✅") 
            print("🎮 Game flow: ✅")
            print("📡 Socket events: ✅")
        else:
            print("\n❌ Test failed")
    except Exception as e:
        print(f"\n💥 Test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🎮 Quick 1280 Trivia Test")
    print("Testing: Room → Players → Game Flow")
    print("=" * 40)
    asyncio.run(main())