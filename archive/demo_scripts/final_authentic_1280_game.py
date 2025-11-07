#!/usr/bin/env python3
"""
🏠 1280 WEST TRIVIA - FINAL AUTHENTIC SAVAGE MODE 🏠
The ultimate friendship-destroying trivia game with REAL friend dynamics

This combines:
- Real chat messages from your iMessage database
- Authentic friend group dynamics you described
- 1280 West building drama
- Maximum savage content
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.generators.question_generator import (
    ReceiptQuestionGenerator, 
    RoastQuestionGenerator, 
    MostLikelyQuestionGenerator
)

def get_comprehensive_1280_questions():
    """Complete set of authentic 1280 West questions."""
    
    # Real receipt questions from actual messages
    real_receipts = [
        {
            'question_text': 'Who said: "Sweet! Benny and I are hopping on Marta now."?',
            'correct_answer': 'Ian',  # or whoever actually sent this
            'wrong_answers': ['Benny', 'Gina', 'Lauren'],
            'category': 'RECEIPTS & REGRETS',
            'context': 'Real message from group chat',
            'savage_level': 2
        },
        {
            'question_text': 'Who said: "Just got home from walking to the grocery store ~~~ wild Friday night!!"?',
            'correct_answer': 'Gina',  # whoever the boring one is lol
            'wrong_answers': ['Benny', 'Ian', 'Lauren'],
            'category': 'RECEIPTS & REGRETS',
            'context': 'Peak boring behavior exposed',
            'savage_level': 3
        }
    ]
    
    # Authentic friend dynamics questions
    friend_dynamics = [
        {
            'question_text': "Who's most likely to give someone the ick within 24 hours?",
            'correct_answer': 'Benny',
            'wrong_answers': ['Lauren', 'Gina', 'Ian'],
            'category': 'BENNY ICK MASTER',
            'context': 'Everything gives Benny the ick',
            'savage_level': 5
        },
        {
            'question_text': "Who still sleeps with their ex regularly?",
            'correct_answer': 'Benny',
            'wrong_answers': ['Lauren', 'Gina', 'Ian'],
            'category': 'BENNY ICK MASTER',
            'context': 'Benny we all know about your ex situation',
            'savage_level': 6
        },
        {
            'question_text': "Who's most likely to respond to this text message sometime next month?",
            'correct_answer': 'Gina',
            'wrong_answers': ['Lauren', 'Benny', 'Ian'],
            'category': 'GINA TEXTING DISASTERS',
            'context': 'Gina texting game is legendary bad',
            'savage_level': 4
        },
        {
            'question_text': "Who do we have to physically check if their door opens to see if they're actually coming?",
            'correct_answer': 'Gina',
            'wrong_answers': ['Lauren', 'Benny', 'Ian'],
            'category': 'GINA TEXTING DISASTERS',
            'context': 'The Gina uncertainty principle',
            'savage_level': 4
        },
        {
            'question_text': "Who's the messiest person when it comes to dating?",
            'correct_answer': 'Lauren',
            'wrong_answers': ['Benny', 'Gina', 'Ian'],
            'category': 'LAUREN CHAOS ENERGY',
            'context': 'Lauren confirmed messiest',
            'savage_level': 5
        },
        {
            'question_text': "Who makes the worst decisions when drunk? (Hint: #1 on the list)",
            'correct_answer': 'Benny',
            'wrong_answers': ['Lauren', 'Gina', 'Ian'],
            'category': 'DRUNK DECISION RANKINGS',
            'context': 'Drunk hierarchy: 1.Benny 2.Lauren 3.Ian 4.Gina',
            'savage_level': 5
        },
        {
            'question_text': "Who makes the SECOND worst decisions when drunk?",
            'correct_answer': 'Lauren',
            'wrong_answers': ['Benny', 'Gina', 'Ian'],
            'category': 'DRUNK DECISION RANKINGS',
            'context': 'Lauren takes silver in drunk stupidity',
            'savage_level': 4
        }
    ]
    
    # 1280 West building drama
    building_drama = [
        {
            'question_text': "Who's the shit-faced neighbor that owes $40K in HOA fees and got arrested this summer?",
            'correct_answer': 'Tom',
            'wrong_answers': ['The dog owner', 'HOA president', 'Some random neighbor'],
            'category': '1280 WEST BUILDING CHAOS',
            'context': 'Tom is a building legend for all the wrong reasons',
            'savage_level': 6
        },
        {
            'question_text': "Which former hookup duo has to awkwardly live across the hall from each other?",
            'correct_answer': 'Lauren & Gina',
            'wrong_answers': ['Benny & Ian', 'Lauren & Benny', 'Gina & Ian'],
            'category': '1280 WEST HOOKUP AWKWARDNESS',
            'context': 'Hallway encounters must be interesting',
            'savage_level': 4
        },
        {
            'question_text': "Which SECOND former hookup duo also lives in the same building?",
            'correct_answer': 'Benny & Ian',
            'wrong_answers': ['Lauren & Gina', 'Lauren & Benny', 'Gina & Ian'],
            'category': '1280 WEST HOOKUP AWKWARDNESS',
            'context': 'Double the hookup history, double the awkwardness',
            'savage_level': 4
        },
        {
            'question_text': "Who's most likely to pretend they don't see the dog piss in the elevator?",
            'correct_answer': 'All of them',
            'wrong_answers': ['Just the dog owners', 'Just Tom', 'Just the HOA'],
            'category': '1280 WEST BUILDING CHAOS',
            'context': 'Elevator survival tactics',
            'savage_level': 3
        }
    ]
    
    # High behavior questions
    high_behavior = [
        {
            'question_text': "Who's most likely to be too high to function at a normal social event?",
            'correct_answer': 'Benny',
            'wrong_answers': ['Gina', 'Lauren', 'Ian'],
            'category': 'HIGH AS FUCK BEHAVIOR',
            'context': 'Benny is high all the time',
            'savage_level': 4
        },
        {
            'question_text': "Who ELSE is most likely to be too high to function at a normal social event?",
            'correct_answer': 'Gina',
            'wrong_answers': ['Benny', 'Lauren', 'Ian'],
            'category': 'HIGH AS FUCK BEHAVIOR',
            'context': 'Gina is also high all the time',
            'savage_level': 4
        }
    ]
    
    return real_receipts + friend_dynamics + building_drama + high_behavior

def simulate_savage_game_round():
    """Simulate an actual game round with your authentic questions."""
    
    print("🎮 STARTING 1280 WEST SAVAGE TRIVIA ROUND 🎮")
    print("=" * 60)
    print("Players: Lauren (Host), Benny, Gina, Ian")
    print("Location: 1280 West Condos (Building of Chaos)")
    print("Savage Level: MAXIMUM FRIENDSHIP DESTRUCTION")
    print()
    
    questions = get_comprehensive_1280_questions()
    
    # Simulate 5 questions from a real game
    import random
    game_questions = random.sample(questions, 5)
    
    for i, q in enumerate(game_questions, 1):
        print(f"📱 QUESTION {i}/5")
        print(f"Category: {q['category']}")
        print(f"🔥 Savage Level: {q.get('savage_level', 3)}/6")
        print()
        print(f"❓ {q['question_text']}")
        print()
        print("Answer choices:")
        all_answers = [q['correct_answer']] + q['wrong_answers']
        random.shuffle(all_answers)
        
        for j, answer in enumerate(all_answers, 1):
            if answer == q['correct_answer']:
                print(f"   {j}. {answer} ✅ (CORRECT)")
            else:
                print(f"   {j}. {answer}")
        
        print(f"\n💭 Context: {q['context']}")
        print()
        
        if i < 5:  # Don't print separator after last question
            print("-" * 50)
            print()
    
    print("🎯 GAME RESULTS PREDICTION:")
    print("=" * 60)
    print("💀 Friendships Destroyed: ALL OF THEM")
    print("😭 People Who Will Cry: Benny (from the roasting)")
    print("😤 People Who Will Get Mad: Gina (texting call-outs)")
    print("😈 People Who Will Love It: Lauren (created this monster)")
    print("🏃 People Who Will Try to Leave: Ian (Tom avoidance tactics)")
    print("🔥 Overall Savage Success: NUCLEAR LEVEL ACHIEVED")
    print()
    print("🏠 1280 West Building Status: OFFICIALLY A CHAOS ZONE")
    print("👥 Friend Group Status: ROASTED TO PERFECTION")

if __name__ == "__main__":
    simulate_savage_game_round()