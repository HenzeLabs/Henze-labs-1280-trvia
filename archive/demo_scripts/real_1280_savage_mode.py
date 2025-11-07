#!/usr/bin/env python3
"""
REAL 1280 WEST SAVAGE MODE
Testing authentic questions based on actual friend group dynamics
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.generators.question_generator import (
    ReceiptQuestionGenerator, 
    RoastQuestionGenerator, 
    MostLikelyQuestionGenerator
)

def test_real_savage_questions():
    print("🏠 1280 WEST SAVAGE TRIVIA - REAL FRIEND GROUP EDITION 🏠")
    print("=" * 60)
    
    # Mock real friend group data
    real_friends_data = [
        {'sender': 'Benny', 'message_text': 'Still hooking up with my ex lol', 'chat_name': '1280 Squad'},
        {'sender': 'Gina', 'message_text': 'Sorry just saw this from last week', 'chat_name': '1280 Squad'},
        {'sender': 'Ian', 'message_text': 'Avoiding Tom in the hallway again', 'chat_name': '1280 Squad'},
        {'sender': 'Lauren', 'message_text': 'I made the worst decision last night when drunk', 'chat_name': '1280 Squad'},
        {'sender': 'Benny', 'message_text': 'Got the ick from that guy immediately', 'chat_name': '1280 Squad'},
        {'sender': 'Gina', 'message_text': 'I might come tonight... maybe... probably', 'chat_name': '1280 Squad'},
        {'sender': 'Lauren', 'message_text': 'Did you see the dog piss in the elevator AGAIN?', 'chat_name': '1280 Squad'},
        {'sender': 'Ian', 'message_text': 'Tom is shit-faced in the lobby again', 'chat_name': '1280 Squad'},
    ]
    
    # Test generators
    receipt_gen = ReceiptQuestionGenerator()
    roast_gen = RoastQuestionGenerator()
    most_likely_gen = MostLikelyQuestionGenerator()
    
    print("📱 REAL RECEIPTS FROM 1280 WEST:")
    print("-" * 40)
    for i in range(3):
        question = receipt_gen.generate_question(real_friends_data)
        if question:
            print(f"\n{i+1}. {question['question_text']}")
            print(f"   Correct: {question['correct_answer']}")
            print(f"   Wrong: {', '.join(question['wrong_answers'])}")
            print(f"   Context: {question['context']}")
    
    print("\n\n🔥 REAL ROASTS BASED ON ACTUAL DYNAMICS:")
    print("-" * 40)
    for i in range(3):
        question = roast_gen.generate_question(real_friends_data)
        if question:
            print(f"\n{i+1}. {question['question_text']}")
            print(f"   Answer: {question['correct_answer']}")
            if "still sleeps with their ex" in question['question_text']:
                print("   🎯 BENNY CALL-OUT SPECIAL!")
            elif "give someone the ick" in question['question_text']:
                print("   🎯 BENNY'S SUPERPOWER!")
            elif "messiest person when it comes to dating" in question['question_text']:
                print("   🎯 LAUREN ROAST ACTIVATED!")
    
    print("\n\n🤔 MOST LIKELY - 1280 WEST EDITION:")
    print("-" * 40)
    for i in range(5):
        question = most_likely_gen.generate_question(real_friends_data)
        if question:
            print(f"\n{i+1}. Who's most likely to {question['question_text'].replace('Who is most likely to ', '')}?")
            print(f"   Answer: {question['correct_answer']}")
            
            # Special call-outs for real dynamics
            if "respond to this text message sometime next month" in question['question_text']:
                print("   📱 GINA'S TEXTING GAME IS WEAK!")
            elif "give someone the ick within 24 hours" in question['question_text']:
                print("   💔 BENNY'S SPECIALTY!")
            elif "still be sleeping with their ex" in question['question_text']:
                print("   🛏️ BENNY WE ALL KNOW!")
            elif "avoid Tom in the hallway" in question['question_text']:
                print("   🏃 1280 WEST SURVIVAL TACTICS!")
            elif "check if their door opens" in question['question_text']:
                print("   🚪 THE GINA UNCERTAINTY PRINCIPLE!")
            elif "live across the hall from someone they used to sleep with" in question['question_text']:
                print("   🏠 LAUREN & GINA'S AWKWARD REALITY!")
    
    print("\n\n🎯 AUTHENTIC 1280 WEST SAVAGE STATS:")
    print("=" * 60)
    print("🔥 Benny Roast Potential: MAXIMUM (ex situation + ick master)")
    print("📱 Gina Texting Shame: LEGENDARY (we check doors instead)")
    print("🏠 Lauren Mess Level: CONFIRMED (messiest + drunk decisions)")
    print("🏃 Ian Tom Avoidance: PROFESSIONAL LEVEL")
    print("🏢 Building Drama: SHIT SHOW STATUS CONFIRMED")
    print("💀 Friend Group Roast Capability: NUCLEAR LEVEL")

if __name__ == "__main__":
    test_real_savage_questions()