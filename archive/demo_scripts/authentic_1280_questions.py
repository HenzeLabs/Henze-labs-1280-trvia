#!/usr/bin/env python3
"""
REAL 1280 WEST SAVAGE QUESTIONS - HAND-CRAFTED AUTHENTIC EDITION
These are based on actual friend group dynamics and building drama
"""

def get_authentic_1280_questions():
    """Return hand-crafted questions based on real 1280 West dynamics."""
    
    # Real dynamics questions
    authentic_questions = [
        {
            'category': 'RECEIPTS & REGRETS',
            'question_type': 'who_said_this',
            'question_text': 'Which absolute trainwreck said: "Still hooking up with my ex but whatever"?',
            'correct_answer': 'Benny',
            'wrong_answers': ['Lauren', 'Gina', 'Ian'],
            'context': 'Based on real Benny ex situation',
            'savage_level': 6
        },
        {
            'category': 'Red Flags',
            'question_type': 'most_likely',
            'question_text': "Who's most likely to give someone the ick within 24 hours?",
            'correct_answer': 'Benny',
            'wrong_answers': ['Lauren', 'Gina', 'Ian'],
            'context': 'Benny ick master confirmed',
            'savage_level': 5
        },
        {
            'category': 'Red Flags',
            'question_type': 'most_likely',
            'question_text': "Who's most likely to respond to this text message sometime next month?",
            'correct_answer': 'Gina',
            'wrong_answers': ['Lauren', 'Benny', 'Ian'],
            'context': 'Gina texting game is legendary bad',
            'savage_level': 4
        },
        {
            'category': 'Red Flags',
            'question_type': 'most_likely',
            'question_text': "Who do we have to check if their door opens to see if they're actually coming with us?",
            'correct_answer': 'Gina',
            'wrong_answers': ['Lauren', 'Benny', 'Ian'],
            'context': 'The Gina uncertainty principle',
            'savage_level': 3
        },
        {
            'category': '1280 West Building Drama',
            'question_type': 'most_likely',
            'question_text': "Who's most likely to try to avoid Tom in the hallway because he's shit-faced again?",
            'correct_answer': 'All of them',
            'wrong_answers': ['Just Ian', 'Just Lauren', 'Just Benny'],
            'context': 'Tom survival tactics',
            'savage_level': 2
        },
        {
            'category': '1280 West Building Drama',
            'question_type': 'roast',
            'question_text': "Which former hookup duo has to awkwardly live across the hall from each other?",
            'correct_answer': 'Lauren & Gina',
            'wrong_answers': ['Benny & Ian', 'Lauren & Benny', 'Gina & Ian'],
            'context': 'Awkward hallway encounters',
            'savage_level': 4
        },
        {
            'category': '1280 West Building Drama',
            'question_type': 'roast',
            'question_text': "Which former hookup duo ALSO has to awkwardly live in the same building?",
            'correct_answer': 'Benny & Ian',
            'wrong_answers': ['Lauren & Gina', 'Lauren & Benny', 'Gina & Ian'],
            'context': 'Double building awkwardness',
            'savage_level': 4
        },
        {
            'category': 'Degenerate Behavior',
            'question_type': 'most_likely',
            'question_text': "Who's most likely to make the worst decision when drunk tonight?",
            'correct_answer': 'Benny',
            'wrong_answers': ['Lauren', 'Gina', 'Ian'],
            'context': 'Drunk decision hierarchy: 1. Benny 2. Lauren 3. Ian 4. Gina',
            'savage_level': 5
        },
        {
            'category': 'Degenerate Behavior',
            'question_type': 'most_likely',
            'question_text': "Who's the messiest person when it comes to dating?",
            'correct_answer': 'Lauren',
            'wrong_answers': ['Benny', 'Gina', 'Ian'],
            'context': 'Lauren confirmed messiest',
            'savage_level': 5
        },
        {
            'category': 'Degenerate Behavior',
            'question_type': 'most_likely',
            'question_text': "Who's most likely to be too high to function at a normal social event?",
            'correct_answer': 'Benny',
            'wrong_answers': ['Gina', 'Lauren', 'Ian'],
            'context': 'Benny and Gina are high all the time',
            'savage_level': 4
        },
        {
            'category': 'Degenerate Behavior',
            'question_type': 'most_likely',
            'question_text': "Who's most likely to also be too high to function at a normal social event?",
            'correct_answer': 'Gina',
            'wrong_answers': ['Benny', 'Lauren', 'Ian'],
            'context': 'High twins Benny & Gina',
            'savage_level': 4
        },
        {
            'category': 'RECEIPTS & REGRETS',
            'question_type': 'who_said_this',
            'question_text': 'Who got mad and said: "Gina, your texting is literally the worst compared to the rest of us"?',
            'correct_answer': 'Lauren',
            'wrong_answers': ['Benny', 'Ian', 'Gina'],
            'context': 'Lauren has gotten mad at Gina for texting',
            'savage_level': 3
        },
        {
            'category': '1280 West Building Drama',
            'question_type': 'roast',
            'question_text': "Which building resident probably pretends they don't see the dog piss in the elevator?",
            'correct_answer': 'All of them',
            'wrong_answers': ['Just the dog owners', 'Just Tom', 'Just the HOA'],
            'context': 'Elevator piss reality',
            'savage_level': 2
        },
        {
            'category': '1280 West Building Drama',
            'question_type': 'roast',
            'question_text': "Who's the shit-faced neighbor that owes $40K in HOA fees and got arrested this summer?",
            'correct_answer': 'Tom',
            'wrong_answers': ['Some other neighbor', 'The dog owner', 'The HOA president'],
            'context': 'Tom is a building legend',
            'savage_level': 6
        },
        {
            'category': 'Friend Group Dynamics',
            'question_type': 'most_likely',
            'question_text': "Who's most likely to roast someone so hard they need therapy?",
            'correct_answer': 'All of them',
            'wrong_answers': ['Just Lauren', 'Just Benny', 'Just Ian'],
            'context': 'Notorious friend group roasters',
            'savage_level': 5
        }
    ]
    
    return authentic_questions

def test_authentic_questions():
    """Test the hand-crafted authentic questions."""
    print("🏠 REAL 1280 WEST SAVAGE TRIVIA - AUTHENTIC EDITION 🏠")
    print("=" * 70)
    print("These questions are based on REAL friend dynamics and building drama!")
    print()
    
    questions = get_authentic_1280_questions()
    
    categories = {}
    for q in questions:
        cat = q['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(q)
    
    for category, cat_questions in categories.items():
        print(f"📂 {category.upper()}")
        print("-" * 50)
        
        for i, q in enumerate(cat_questions, 1):
            print(f"\n{i}. {q['question_text']}")
            print(f"   ✅ Answer: {q['correct_answer']}")
            print(f"   ❌ Wrong: {', '.join(q['wrong_answers'])}")
            print(f"   💭 Context: {q['context']}")
            
            # Savage level indicator
            savage_stars = "🔥" * q['savage_level']
            print(f"   {savage_stars} Savage Level: {q['savage_level']}/6")
        
        print()
    
    print("🎯 AUTHENTIC SAVAGE ANALYTICS:")
    print("=" * 70)
    total_savage = sum(q['savage_level'] for q in questions)
    avg_savage = total_savage / len(questions)
    print(f"📊 Total Questions: {len(questions)}")
    print(f"🔥 Average Savage Level: {avg_savage:.1f}/6")
    print(f"💀 Maximum Friendship Destruction Potential: CONFIRMED")
    print(f"🏠 1280 West Building Drama Integration: COMPLETE")
    print(f"👥 Real Friend Group Dynamics: AUTHENTICALLY SAVAGE")

if __name__ == "__main__":
    test_authentic_questions()