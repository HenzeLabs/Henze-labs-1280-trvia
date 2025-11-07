#!/usr/bin/env python3
"""
🏠 1280 WEST TRIVIA - CORRECTED AUTHENTIC EDITION 🏠
Updated with accurate friend dynamics and building drama
"""

def get_corrected_authentic_questions():
    """Corrected authentic 1280 West questions with accurate details."""
    
    authentic_questions = [
        # Benny Questions - Corrected
        {
            'category': 'BENNY DATING DISASTERS',
            'question_type': 'most_likely',
            'question_text': "Who's most likely to get the ick easily from guys they go on dates with?",
            'correct_answer': 'Benny',
            'wrong_answers': ['Lauren', 'Gina', 'Ian'],
            'context': 'Benny gets the ick from dating, not from everyone',
            'savage_level': 5
        },
        {
            'category': 'BENNY DATING DISASTERS',
            'question_type': 'roast',
            'question_text': "Who sleeps with their ex Taylor who they share 2 dogs with?",
            'correct_answer': 'Benny',
            'wrong_answers': ['Lauren', 'Gina', 'Ian'],
            'context': 'Benny and Taylor have shared custody... of dogs',
            'savage_level': 6
        },
        
        # Gina Questions - Corrected
        {
            'category': 'GINA COMMUNICATION FAILS',
            'question_type': 'most_likely',
            'question_text': "Who's most likely to not commit to plans or communicate if they're actually coming?",
            'correct_answer': 'Gina',
            'wrong_answers': ['Lauren', 'Benny', 'Ian'],
            'context': 'Gina commitment and communication issues',
            'savage_level': 4
        },
        {
            'category': 'GINA COMMUNICATION FAILS',
            'question_type': 'roast',
            'question_text': "Who makes everyone unsure if they're actually showing up even when they say yes?",
            'correct_answer': 'Gina',
            'wrong_answers': ['Lauren', 'Benny', 'Ian'],
            'context': 'The Gina uncertainty principle is real',
            'savage_level': 4
        },
        
        # Lauren Questions
        {
            'category': 'LAUREN CHAOS ENERGY',
            'question_type': 'most_likely',
            'question_text': "Who's the messiest person when it comes to dating?",
            'correct_answer': 'Lauren',
            'wrong_answers': ['Benny', 'Gina', 'Ian'],
            'context': 'Lauren confirmed messiest',
            'savage_level': 5
        },
        {
            'category': 'LAUREN DOG DRAMA',
            'question_type': 'roast',
            'question_text': "Who's the only one without a dog but refuses to pick up poop when walking other people's dogs?",
            'correct_answer': 'Lauren',
            'wrong_answers': ['Benny', 'Gina', 'Ian'],
            'context': 'Lauren dog sitting poop policy',
            'savage_level': 4
        },
        {
            'category': 'LAUREN DOG DRAMA',
            'question_type': 'roast',
            'question_text': "Who refuses to clean up dog poop when dog sitting for friends?",
            'correct_answer': 'Lauren',
            'wrong_answers': ['Benny', 'Gina', 'Ian'],
            'context': 'Lauren has standards... apparently',
            'savage_level': 4
        },
        
        # Tom Questions - Updated
        {
            'category': '1280 WEST TOM DRAMA',
            'question_type': 'roast',
            'question_text': "Who's the neighbor that's shit-faced, creepy, AND kicked a cop?",
            'correct_answer': 'Tom',
            'wrong_answers': ['Some other neighbor', 'The dog owner', 'HOA president'],
            'context': 'Tom is a triple threat of problems',
            'savage_level': 6
        },
        {
            'category': '1280 WEST TOM DRAMA',
            'question_type': 'most_likely',
            'question_text': "Who does EVERYONE in the building avoid?",
            'correct_answer': 'Tom',
            'wrong_answers': ['The loud neighbor', 'The dog owners', 'The HOA'],
            'context': 'Universal Tom avoidance strategy',
            'savage_level': 3
        },
        {
            'category': '1280 WEST TOM DRAMA',
            'question_type': 'most_likely',
            'question_text': "Who thinks Tom is creepy? (Hint: it's unanimous)",
            'correct_answer': 'Everyone',
            'wrong_answers': ['Just the women', 'Just Lauren', 'Just the neighbors'],
            'context': 'Tom creepiness is universally acknowledged',
            'savage_level': 3
        },
        
        # Building Drama - Updated
        {
            'category': '1280 WEST BUILDING CHAOS',
            'question_type': 'roast',
            'question_text': "What never works at 1280 West and leaves people trapped?",
            'correct_answer': 'The elevators',
            'wrong_answers': ['The heating', 'The internet', 'The security'],
            'context': '1280 elevator reliability is a joke',
            'savage_level': 2
        },
        {
            'category': '1280 WEST BUILDING CHAOS',
            'question_type': 'roast',
            'question_text': "What's everywhere in the building that everyone pretends not to see?",
            'correct_answer': 'Dog shit',
            'wrong_answers': ['Dog piss', 'Trash', 'Tom'],
            'context': 'Building-wide dog shit denial',
            'savage_level': 3
        },
        
        # Updated Hookup Questions
        {
            'category': '1280 WEST HOOKUP AWKWARDNESS',
            'question_type': 'roast',
            'question_text': "Which former hookup duo has to live across the hall from each other?",
            'correct_answer': 'Lauren & Gina',
            'wrong_answers': ['Benny & Ian', 'Lauren & Ian', 'Gina & Benny'],
            'context': 'Hallway encounters must be interesting',
            'savage_level': 4
        },
        {
            'category': '1280 WEST HOOKUP AWKWARDNESS', 
            'question_type': 'roast',
            'question_text': "Which other former hookup duo also lives in the same building?",
            'correct_answer': 'Benny & Ian',
            'wrong_answers': ['Lauren & Gina', 'Lauren & Ian', 'Gina & Benny'],
            'context': 'Everyone is cool now, but still... awkward building',
            'savage_level': 4
        },
        
        # High Behavior
        {
            'category': 'HIGH AS FUCK BEHAVIOR',
            'question_type': 'most_likely',
            'question_text': "Who's most likely to be too high to function at a normal social event?",
            'correct_answer': 'Benny',
            'wrong_answers': ['Gina', 'Lauren', 'Ian'],
            'context': 'Benny is perpetually stoned',
            'savage_level': 4
        },
        {
            'category': 'HIGH AS FUCK BEHAVIOR',
            'question_type': 'most_likely', 
            'question_text': "Who ELSE is most likely to be too high to function at a normal social event?",
            'correct_answer': 'Gina',
            'wrong_answers': ['Benny', 'Lauren', 'Ian'],
            'context': 'Gina is also perpetually stoned',
            'savage_level': 4
        }
    ]
    
    return authentic_questions

def test_corrected_questions():
    """Test the corrected authentic questions."""
    print("🏠 1280 WEST CORRECTED SAVAGE TRIVIA 🏠")
    print("=" * 60)
    print("✅ Updated with accurate friend dynamics")
    print("✅ Corrected building drama details")
    print("✅ Fixed Tom situation (creepy + cop kicker)")
    print("✅ Updated Benny ick context (dating only)")
    print("✅ Fixed Gina communication issues (not door checking)")
    print("✅ Added Lauren dog poop drama")
    print()
    
    questions = get_corrected_authentic_questions()
    
    categories = {}
    for q in questions:
        cat = q['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(q)
    
    for category, cat_questions in categories.items():
        print(f"📂 {category}")
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
    
    print("🎯 CORRECTED SAVAGE ANALYTICS:")
    print("=" * 60)
    total_savage = sum(q['savage_level'] for q in questions)
    avg_savage = total_savage / len(questions)
    print(f"📊 Total Questions: {len(questions)}")
    print(f"🔥 Average Savage Level: {avg_savage:.1f}/6")
    print(f"✅ Accuracy Level: MAXIMUM (all details corrected)")
    print(f"💀 Friendship Destruction Potential: STILL NUCLEAR")
    print(f"🏠 1280 West Authenticity: 100% ACCURATE")

if __name__ == "__main__":
    test_corrected_questions()