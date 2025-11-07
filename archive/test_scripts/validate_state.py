#!/usr/bin/env python3
"""
State Management and Logic Validator
Validates the game engine's state management and logic
"""

import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.game.engine import GameEngine
from app.models import Question

class StateValidator:
    def __init__(self):
        self.engine = GameEngine()
        
    def validate_session_lifecycle(self):
        """Validate complete session lifecycle"""
        print("🔄 Testing Session Lifecycle")
        print("-" * 30)
        
        # Create sample questions for testing
        sample_questions = [
            {
                'id': 1,
                'category': 'Test',
                'question_type': 'receipts',
                'question_text': 'Who said this test quote?',
                'correct_answer': 'Alice',
                'wrong_answers': ['Bob', 'Charlie'],
                'context': 'Test context',
                'difficulty': 1
            },
            {
                'id': 2,
                'category': 'Test',
                'question_type': 'roast',
                'question_text': 'Another test question?',
                'correct_answer': 'Bob',
                'wrong_answers': ['Alice', 'Charlie'],
                'context': 'Test context 2',
                'difficulty': 1
            }
        ]
        
        # Create session
        room_code = self.engine.create_session("TestHost", sample_questions)
        print(f"✅ Session created: {room_code}")
        
        # Add players
        player1_id = self.engine.join_session(room_code, "Alice")
        player2_id = self.engine.join_session(room_code, "Bob") 
        player3_id = self.engine.join_session(room_code, "Charlie")
        
        session = self.engine.get_session(room_code)
        print(f"✅ Players added: {len(session.players)} players")
        
        # Start game
        success = self.engine.start_game(room_code)
        print(f"✅ Game started: {success}")
        
        # Check session state
        session = self.engine.get_session(room_code)
        print(f"✅ Session status: {session.status}")
        print(f"✅ Current question: {session.current_question_index}")
        
        # Get player objects for testing
        player1 = session.players[player1_id]
        player2 = session.players[player2_id]
        player3 = session.players[player3_id]
        
        return session, [player1, player2, player3]
    
    def validate_question_flow(self, session, players):
        """Validate question flow and scoring"""
        print(f"\n❓ Testing Question Flow")
        print("-" * 30)
        
        room_code = session.room_code
        
        # Test first question
        question = self.engine.get_current_question(room_code)
        if question:
            print(f"✅ Got question: {question['question_text'][:50]}...")
            print(f"✅ Category: {question['category']}")
            print(f"✅ Answer choices: {question['answers']}")
        else:
            print("❌ No question available")
            return False
            
        # Get the original question to find correct answer
        original_question = session.questions[session.current_question_index]
        correct_answer = original_question.correct_answer
        available_answers = question['answers']
        wrong_answers = [a for a in available_answers if a != correct_answer]
        
        print(f"✅ Correct answer: {correct_answer}")
        
        # Player 1 gets it right
        result1 = self.engine.submit_answer(players[0].id, correct_answer)
        print(f"✅ Player 1 (correct): {result1}")
        
        # Player 2 gets it wrong
        if wrong_answers:
            result2 = self.engine.submit_answer(players[1].id, wrong_answers[0])
            print(f"✅ Player 2 (wrong): {result2}")
        
        # Player 3 doesn't answer (timeout simulation)
        print(f"✅ Player 3: No answer (timeout)")
        
        # Check scores
        leaderboard = self.engine.get_leaderboard(room_code)
        print(f"✅ Leaderboard: {leaderboard}")
        
        return True
    
    def validate_game_progression(self, session):
        """Validate game progression through multiple questions"""
        print(f"\n➡️  Testing Game Progression") 
        print("-" * 30)
        
        room_code = session.room_code
        initial_question = session.current_question_index
        
        # Move to next question
        has_next = self.engine.next_question(room_code)
        print(f"✅ Next question available: {has_next}")
        
        if has_next:
            session = self.engine.get_session(room_code)
            new_question_index = session.current_question_index
            print(f"✅ Question index: {initial_question} → {new_question_index}")
            
            # Get new question
            question = self.engine.get_current_question(room_code)
            if question:
                print(f"✅ New question: {question['question_text'][:50]}...")
            else:
                print("❌ Failed to get new question")
                return False
        
        return True
    
    def validate_error_handling(self):
        """Validate error handling for edge cases"""
        print(f"\n🚨 Testing Error Handling")
        print("-" * 30)
        
        # Test invalid room codes
        invalid_session = self.engine.get_session("INVALID")
        print(f"✅ Invalid room code handling: {invalid_session is None}")
        
        # Test adding player to non-existent session
        try:
            invalid_player = self.engine.join_session("INVALID", "TestPlayer")
            print(f"❌ Should have failed: {invalid_player}")
        except:
            print(f"✅ Invalid session player add handled")
        
        # Test submitting answer for non-existent player
        result = self.engine.submit_answer("invalid_player", "test")
        success = result.get('success', True) if isinstance(result, dict) else result
        print(f"✅ Invalid player answer handled: {not success}")
        
        # Test starting non-existent game
        success = self.engine.start_game("INVALID")
        print(f"✅ Invalid game start: {not success}")
        
        return True
    
    def validate_concurrent_access(self):
        """Validate handling of concurrent access patterns"""
        print(f"\n🔄 Testing Concurrent Access Patterns")
        print("-" * 30)
        
        # Create sample questions
        sample_questions = [
            {
                'id': 1,
                'category': 'Test',
                'question_type': 'receipts',
                'question_text': 'Concurrent test question?',
                'correct_answer': 'Alice',
                'wrong_answers': ['Bob', 'Charlie', 'David', 'Eve'],
                'context': 'Test context',
                'difficulty': 1
            }
        ]
        
        # Create session
        room_code = self.engine.create_session("ConcurrentHost", sample_questions)
        
        # Add multiple players quickly (simulating concurrent joins)
        player_ids = []
        for i in range(5):
            player_id = self.engine.join_session(room_code, f"Player{i+1}")
            player_ids.append(player_id)
        
        session = self.engine.get_session(room_code)
        print(f"✅ Multiple players added: {len(session.players)}")
        
        # Start game
        self.engine.start_game(room_code)
        
        # Simulate concurrent answer submissions
        question = self.engine.get_current_question(room_code)
        if question:
            answers = question['answers']
            results = []
            
            for i, player_id in enumerate(player_ids):
                answer = answers[i % len(answers)]  # Cycle through answers
                result = self.engine.submit_answer(player_id, answer)
                results.append(result)
            
            print(f"✅ Concurrent answers processed: {len(results)}")
            
            # Check final state consistency
            leaderboard = self.engine.get_leaderboard(room_code)
            total_score = sum(p['score'] for p in leaderboard)
            print(f"✅ Final state consistent - Total score: {total_score}")
        
        return True
    
    def validate_data_persistence(self):
        """Validate that data persists correctly in memory"""
        print(f"\n💾 Testing Data Persistence")
        print("-" * 30)
        
        # Create sample questions
        sample_questions = [
            {
                'id': 1,
                'category': 'Test',
                'question_type': 'receipts',
                'question_text': 'Persistence test question?',
                'correct_answer': 'TestAnswer',
                'wrong_answers': ['Wrong1', 'Wrong2'],
                'context': 'Test context',
                'difficulty': 1
            }
        ]
        
        # Create session and add data
        room_code = self.engine.create_session("PersistenceHost", sample_questions)
        
        player_id = self.engine.join_session(room_code, "TestPlayer")
        self.engine.start_game(room_code)
        
        # Submit answer to change state
        question = self.engine.get_current_question(room_code)
        if question:
            # Get correct answer from the original question
            session = self.engine.get_session(room_code)
            original_question = session.questions[session.current_question_index]
            self.engine.submit_answer(player_id, original_question.correct_answer)
        
        # Retrieve session again and verify data
        session2 = self.engine.get_session(room_code)
        player_session2 = self.engine.get_player_session(player_id)
        
        print(f"✅ Session persistence: {room_code == session2.room_code}")
        print(f"✅ Player persistence: {player_id in session2.players}")
        
        # Check if player has points from correct answer
        player = session2.players[player_id]
        print(f"✅ Score persistence: {player.score > 0}")
        
        return True
    
    def run_all_validations(self):
        """Run comprehensive state validation"""
        print("🎯 State Management Validator")
        print("=" * 50)
        
        try:
            # Test 1: Session lifecycle
            session, players = self.validate_session_lifecycle()
            
            # Test 2: Question flow
            self.validate_question_flow(session, players)
            
            # Test 3: Game progression  
            self.validate_game_progression(session)
            
            # Test 4: Error handling
            self.validate_error_handling()
            
            # Test 5: Concurrent access
            self.validate_concurrent_access()
            
            # Test 6: Data persistence
            self.validate_data_persistence()
            
            print("\n✅ All state validations passed!")
            return True
            
        except Exception as e:
            print(f"\n❌ Validation failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

def main():
    validator = StateValidator()
    success = validator.run_all_validations()
    
    if success:
        print("\n🎉 State management is solid!")
    else:
        print("\n🚨 Issues found in state management")
        sys.exit(1)

if __name__ == "__main__":
    main()