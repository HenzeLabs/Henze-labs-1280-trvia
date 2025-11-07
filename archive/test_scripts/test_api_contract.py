#!/usr/bin/env python3
"""
API Contract Validation Test
Tests that the frozen API contract is properly enforced
"""

import sys
import traceback
from backend.app.game.models_v1 import (
    Player, Question, GameSession, APIValidator, 
    CONTRACT_VERSION, BREAKING_CHANGE_WARNING
)
from datetime import datetime


def test_player_validation():
    """Test Player contract validation"""
    print("🧪 Testing Player contract validation...")
    
    # Valid player
    try:
        player = Player(
            id="player_0_1234",
            name="Alice",
            score=100,
            answered_current=True
        )
        print("✅ Valid player created successfully")
    except Exception as e:
        print(f"❌ Valid player failed: {e}")
        return False
    
    # Invalid player ID format
    try:
        Player(id="invalid_id", name="Alice")
        print("❌ Should have failed for invalid ID")
        return False
    except ValueError:
        print("✅ Correctly rejected invalid player ID")
    
    # Invalid name length
    try:
        Player(id="player_0_1234", name="")
        print("❌ Should have failed for empty name")
        return False
    except ValueError:
        print("✅ Correctly rejected empty name")
    
    # Invalid score
    try:
        Player(id="player_0_1234", name="Alice", score=-1)
        print("❌ Should have failed for negative score")
        return False
    except ValueError:
        print("✅ Correctly rejected negative score")
    
    return True


def test_question_validation():
    """Test Question contract validation"""
    print("\n🧪 Testing Question contract validation...")
    
    # Valid question
    try:
        question = Question(
            id=1,
            category="Receipts",
            question_type="receipts",
            question_text="Who said this?",
            correct_answer="Alice",
            wrong_answers=["Bob", "Charlie"],
            difficulty=3
        )
        print("✅ Valid question created successfully")
    except Exception as e:
        print(f"❌ Valid question failed: {e}")
        return False
    
    # Invalid category
    try:
        Question(
            id=1,
            category="InvalidCategory",
            question_type="receipts",
            question_text="Test?",
            correct_answer="Alice",
            wrong_answers=["Bob", "Charlie"]
        )
        print("❌ Should have failed for invalid category")
        return False
    except ValueError:
        print("✅ Correctly rejected invalid category")
    
    # Invalid wrong answers count
    try:
        Question(
            id=1,
            category="Receipts",
            question_type="receipts", 
            question_text="Test?",
            correct_answer="Alice",
            wrong_answers=["Bob"]  # Only 1 wrong answer
        )
        print("❌ Should have failed for insufficient wrong answers")
        return False
    except ValueError:
        print("✅ Correctly rejected insufficient wrong answers")
    
    return True


def test_game_session_validation():
    """Test GameSession contract validation"""
    print("\n🧪 Testing GameSession contract validation...")
    
    # Valid session
    try:
        session = GameSession(
            room_code="ABC123",
            host_name="Host",
            status="waiting"
        )
        print("✅ Valid session created successfully")
    except Exception as e:
        print(f"❌ Valid session failed: {e}")
        return False
    
    # Invalid room code format
    try:
        GameSession(room_code="invalid", host_name="Host")
        print("❌ Should have failed for invalid room code")
        return False
    except ValueError:
        print("✅ Correctly rejected invalid room code")
    
    # Invalid status
    try:
        GameSession(room_code="ABC123", host_name="Host", status="invalid")
        print("❌ Should have failed for invalid status")
        return False
    except ValueError:
        print("✅ Correctly rejected invalid status")
    
    return True


def test_api_validator():
    """Test APIValidator utility functions"""
    print("\n🧪 Testing APIValidator utilities...")
    
    # Room code validation
    try:
        normalized = APIValidator.validate_room_code("abc123")
        assert normalized == "ABC123", f"Expected ABC123, got {normalized}"
        print("✅ Room code normalization works")
    except Exception as e:
        print(f"❌ Room code validation failed: {e}")
        return False
    
    # Player ID validation
    try:
        APIValidator.validate_player_id("player_0_1234")
        print("✅ Player ID validation works")
    except Exception as e:
        print(f"❌ Player ID validation failed: {e}")
        return False
    
    # Host name validation with default
    try:
        default_name = APIValidator.validate_host_name(None)
        assert default_name == "Anonymous Host", f"Expected Anonymous Host, got {default_name}"
        print("✅ Host name default works")
    except Exception as e:
        print(f"❌ Host name validation failed: {e}")
        return False
    
    return True


def test_immutability():
    """Test that models are truly immutable"""
    print("\n🧪 Testing model immutability...")
    
    try:
        player = Player(id="player_0_1234", name="Alice", score=100)
        
        # Try to modify immutable field
        try:
            player.score = 200
            print("❌ Should not be able to modify frozen dataclass")
            return False
        except Exception:
            print("✅ Field assignment blocked on frozen dataclass")
        
        # Try to add new attributes
        try:
            player.new_field = "test"
            print("❌ Should not be able to add new fields")
            return False
        except Exception:
            print("✅ New field assignment blocked")
        
        print("✅ Dataclass immutability is enforced")
        
    except Exception as e:
        print(f"❌ Immutability test failed: {e}")
        return False
    
    return True


def main():
    """Run all contract validation tests"""
    print("🔒 API Contract Validation Test Suite")
    print("=" * 50)
    print(f"Contract Version: {CONTRACT_VERSION}")
    print(f"Status: FROZEN 🔒")
    print()
    
    tests = [
        ("Player Validation", test_player_validation),
        ("Question Validation", test_question_validation),
        ("GameSession Validation", test_game_session_validation),
        ("APIValidator Utilities", test_api_validator),
        ("Model Immutability", test_immutability)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                failed += 1
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            failed += 1
            print(f"💥 {test_name}: ERROR - {e}")
            traceback.print_exc()
    
    print("\n" + "=" * 50)
    print(f"📊 Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All API contract validations PASSED!")
        print("🔒 Contract enforcement is working correctly")
        return True
    else:
        print("❌ Some contract validations FAILED!")
        print("⚠️ Contract enforcement needs attention")
        return False


if __name__ == "__main__":
    success = main()
    if not success:
        print("\n" + BREAKING_CHANGE_WARNING)
    sys.exit(0 if success else 1)