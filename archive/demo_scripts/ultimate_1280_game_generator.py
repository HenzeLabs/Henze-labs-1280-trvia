#!/usr/bin/env python3
"""
🔥 1280 WEST ULTIMATE SAVAGE TRIVIA GAME 🔥
15 Questions Per Game:
- 3 Group Chat Receipts (Lauren, Benny, Ian, Gina texts)
- 4 Dirty Sex Trivia Questions  
- 5 Real Normal Trivia Questions
- 2 Dirty "Most Likely To" Questions
- 1 Would You Rather Question
"""

import random
from typing import List, Dict

class Ultimate1280TriviaGenerator:
    """The complete 1280 West savage trivia experience."""
    
    def __init__(self):
        self.dirty_most_likely_questions = [
            "Who is most likely to have a one-night stand?",
            "Who is most likely to send a risky text and regret it?",
            "Who is most likely to make out with a stranger?",
            "Who is most likely to get caught in the act?",
            "Who is most likely to hook up with their ex?",
            "Who is most likely to have a secret kink?",
            "Who is most likely to have a threesome?",
            "Who is most likely to flirt their way out of a speeding ticket?",
            "Who is most likely to date two people at once?",
            "Who is most likely to get handcuffed (in any context)?",
            "Who is most likely to send a spicy picture to the wrong person?",
            "Who is most likely to sleep with their boss?",
            "Who is most likely to have sex out in public?",
            "Who is most likely to own way too many toys?",
            "Who is most likely to wake up in a stranger's bed?",
            "Who is most likely to get caught skinny dipping?",
            "Who is most likely to make a sex tape?",
            "Who is most likely to hook up with a best friend?",
            "Who is most likely to go to a sex club?",
            "Who is most likely to read spicy romance books?",
            "Who is most likely to use a fake name at a bar?",
            "Who is most likely to have a secret admirer?",
            "Who is most likely to go commando in public?",
            "Who is most likely to try roleplay in the bedroom?",
            "Who is most likely to hook up with someone famous?",
            "Who is most likely to sext while at work?",
            "Who is most likely to have a wild bucket list?",
            "Who is most likely to have a hidden tattoo in a spicy place?",
            "Who is most likely to accidentally call out the wrong name during sex?",
            "Who is most likely to use a dating app for hookups?",
            "Who is most likely to own very revealing lingerie?",
            "Who is most likely to make out with a coworker?",
            "Who is most likely to try a long-distance spicy video call?",
            "Who is most likely to be into public displays of affection?",
            "Who is most likely to send a voice note that's too freaky?",
            "Who is most likely to have a naughty dream about someone in the room?",
            "Who is most likely to take a shower selfie?",
            "Who is most likely to accidentally expose themselves?",
            "Who is most likely to have a secret affair?",
            "Who is most likely to try a new position just for fun?",
            "Who is most likely to make out with someone they just met?",
            "Who is most likely to text something flirty after just one drink?"
        ]
        
        self.dirty_sex_trivia = [
            {
                'question': "What percentage of people have had sex in a public place?",
                'correct_answer': "About 50%",
                'wrong_answers': ["About 25%", "About 75%", "About 10%"],
                'context': "Half of people are freaky like that"
            },
            {
                'question': "What's the most common safe word used during kinky activities?",
                'correct_answer': "Red",
                'wrong_answers': ["Stop", "Banana", "Pineapple"],
                'context': "Traffic light system is popular"
            },
            {
                'question': "What's the average duration of sexual intercourse?",
                'correct_answer': "5-7 minutes",
                'wrong_answers': ["15-20 minutes", "2-3 minutes", "30+ minutes"],
                'context': "Sorry to disappoint everyone"
            },
            {
                'question': "Which body part has the most nerve endings?",
                'correct_answer': "Clitoris (8,000)",
                'wrong_answers': ["Penis tip", "Lips", "Fingertips"],
                'context': "Female anatomy wins this one"
            },
            {
                'question': "What percentage of women need clitoral stimulation to orgasm?",
                'correct_answer': "About 70%",
                'wrong_answers': ["About 30%", "About 90%", "About 50%"],
                'context': "Educational and savage"
            },
            {
                'question': "What's the most purchased item in sex shops?",
                'correct_answer': "Vibrators",
                'wrong_answers': ["Condoms", "Lube", "Handcuffs"],
                'context': "Self-care is important"
            },
            {
                'question': "Which country has the highest rate of sex toy ownership?",
                'correct_answer': "Norway",
                'wrong_answers': ["United States", "Germany", "Japan"],
                'context': "Nordic countries know what's up"
            },
            {
                'question': "What's the most common sexual fantasy?",
                'correct_answer': "Sex with current partner",
                'wrong_answers': ["Threesome", "Public sex", "Celebrity hookup"],
                'context': "Wholesome but boring"
            },
            {
                'question': "How many erogenous zones does the human body have?",
                'correct_answer': "Over 30",
                'wrong_answers': ["About 10", "About 20", "About 50"],
                'context': "Time to explore, people"
            },
            {
                'question': "What percentage of people have sent nudes?",
                'correct_answer': "About 40%",
                'wrong_answers': ["About 20%", "About 60%", "About 80%"],
                'context': "Digital age problems"
            }
        ]
        
        self.normal_trivia = [
            {
                'question': "What's the capital of Australia?",
                'correct_answer': "Canberra",
                'wrong_answers': ["Sydney", "Melbourne", "Perth"],
                'context': "Not Sydney, surprise!"
            },
            {
                'question': "Which planet is closest to the sun?",
                'correct_answer': "Mercury",
                'wrong_answers': ["Venus", "Earth", "Mars"],
                'context': "Basic astronomy"
            },
            {
                'question': "Who painted the Mona Lisa?",
                'correct_answer': "Leonardo da Vinci",
                'wrong_answers': ["Michelangelo", "Picasso", "Van Gogh"],
                'context': "Classic art question"
            },
            {
                'question': "What's the largest ocean on Earth?",
                'correct_answer': "Pacific Ocean",
                'wrong_answers': ["Atlantic Ocean", "Indian Ocean", "Arctic Ocean"],
                'context': "Geography 101"
            },
            {
                'question': "How many bones are in an adult human body?",
                'correct_answer': "206",
                'wrong_answers': ["195", "220", "180"],
                'context': "Human anatomy fact"
            },
            {
                'question': "What year did World War II end?",
                'correct_answer': "1945",
                'wrong_answers': ["1943", "1946", "1944"],
                'context': "History lesson"
            },
            {
                'question': "What's the chemical symbol for gold?",
                'correct_answer': "Au",
                'wrong_answers': ["Go", "Gd", "Ag"],
                'context': "Chemistry knowledge"
            },
            {
                'question': "Which mammal is known to have the most powerful bite?",
                'correct_answer': "Hippopotamus",
                'wrong_answers': ["Lion", "Shark", "Crocodile"],
                'context': "Hippos are terrifying"
            },
            {
                'question': "What's the smallest country in the world?",
                'correct_answer': "Vatican City",
                'wrong_answers': ["Monaco", "San Marino", "Liechtenstein"],
                'context': "Tiny but mighty"
            },
            {
                'question': "How many hearts does an octopus have?",
                'correct_answer': "Three",
                'wrong_answers': ["Two", "Four", "One"],
                'context': "Ocean facts are wild"
            }
        ]
        
        self.would_you_rather = [
            {
                'question': "Would you rather have to tell your biggest secret or hear everyone else's biggest secret?",
                'option_a': "Tell your biggest secret",
                'option_b': "Hear everyone else's secrets",
                'context': "Information is power"
            },
            {
                'question': "Would you rather never be able to lie or never be able to tell the truth?",
                'option_a': "Never lie (always honest)",
                'option_b': "Never tell the truth (always lie)",
                'context': "Philosophical nightmare"
            },
            {
                'question': "Would you rather have your browser history made public or your text messages made public?",
                'option_a': "Browser history public",
                'option_b': "Text messages public",
                'context': "Digital privacy horror"
            },
            {
                'question': "Would you rather be known for being really good in bed or really bad in bed?",
                'option_a': "Really good in bed",
                'option_b': "Really bad in bed",
                'context': "Reputation matters"
            },
            {
                'question': "Would you rather walk in on your parents or have them walk in on you?",
                'option_a': "Walk in on parents",
                'option_b': "Parents walk in on you",
                'context': "Traumatic either way"
            }
        ]
        
        self.group_chat_receipts = [
            {
                'question': "Who said: 'I had an affair with my coworker and I still have to see them every day at work'?",
                'correct_answer': 'Lauren',
                'wrong_answers': ['Benny', 'Gina', 'Ian'],
                'context': 'Lauren coworker tea ☕',
                'savage_level': 6
            },
            {
                'question': "Who said: 'I sleep with Taylor but we share 2 dogs so it\'s complicated'?",
                'correct_answer': 'Benny',
                'wrong_answers': ['Lauren', 'Gina', 'Ian'],
                'context': 'Benny ex situation',
                'savage_level': 5
            },
            {
                'question': "Who said: 'I get the ick so easily from guys I date, it\'s a problem'?",
                'correct_answer': 'Benny',
                'wrong_answers': ['Lauren', 'Gina', 'Ian'],
                'context': 'Benny dating struggles',
                'savage_level': 4
            },
            {
                'question': "Who said: 'I refuse to pick up dog poop when I dog sit because I don\'t have a dog'?",
                'correct_answer': 'Lauren',
                'wrong_answers': ['Benny', 'Gina', 'Ian'],
                'context': 'Lauren dog sitting policy',
                'savage_level': 4
            },
            {
                'question': "Who said: 'Everyone in the building thinks Tom is creepy and we all avoid him'?",
                'correct_answer': 'Ian',
                'wrong_answers': ['Lauren', 'Gina', 'Benny'],
                'context': 'Universal Tom avoidance',
                'savage_level': 3
            },
            {
                'question': "Who said: 'The elevators at 1280 never work and there\'s dog shit everywhere'?",
                'correct_answer': 'Gina',
                'wrong_answers': ['Lauren', 'Benny', 'Ian'],
                'context': 'Building reality check',
                'savage_level': 3
            }
        ]
    
    def generate_complete_game(self):
        """Generate a complete 15-question game."""
        friends = ['Lauren', 'Benny', 'Gina', 'Ian']
        
        game_questions = []
        
        # 3 Group Chat Receipts
        receipts = random.sample(self.group_chat_receipts, 3)
        for receipt in receipts:
            game_questions.append({
                'category': 'GROUP CHAT RECEIPTS',
                'type': 'receipt',
                'question_text': receipt['question'],
                'correct_answer': receipt['correct_answer'],
                'wrong_answers': receipt['wrong_answers'],
                'context': receipt['context'],
                'savage_level': receipt['savage_level']
            })
        
        # 4 Dirty Sex Trivia
        sex_questions = random.sample(self.dirty_sex_trivia, 4)
        for sq in sex_questions:
            game_questions.append({
                'category': 'DIRTY SEX TRIVIA',
                'type': 'trivia',
                'question_text': sq['question'],
                'correct_answer': sq['correct_answer'],
                'wrong_answers': sq['wrong_answers'],
                'context': sq['context'],
                'savage_level': 4
            })
        
        # 5 Normal Trivia
        normal_questions = random.sample(self.normal_trivia, 5)
        for nq in normal_questions:
            game_questions.append({
                'category': 'NORMAL TRIVIA',
                'type': 'trivia',
                'question_text': nq['question'],
                'correct_answer': nq['correct_answer'],
                'wrong_answers': nq['wrong_answers'],
                'context': nq['context'],
                'savage_level': 1
            })
        
        # 2 Dirty Most Likely To - INTERACTIVE VOTING (everyone votes)
        dirty_most_likely = random.sample(self.dirty_most_likely_questions, 2)
        for dml in dirty_most_likely:
            game_questions.append({
                'category': 'DIRTY MOST LIKELY TO',
                'type': 'interactive_voting',
                'question_text': dml,
                'voting_options': friends,  # All friends are options
                'context': 'Everyone votes on who this applies to most',
                'savage_level': 5,
                'interaction_type': 'most_likely_voting'
            })
        
        # 1 Would You Rather - INTERACTIVE DISCUSSION (everyone answers)
        wyr = random.choice(self.would_you_rather)
        game_questions.append({
            'category': 'WOULD YOU RATHER',
            'type': 'interactive_discussion',
            'question_text': wyr['question'],
            'option_a': wyr['option_a'],
            'option_b': wyr['option_b'],
            'context': 'Everyone picks A or B and explains their choice',
            'savage_level': 3,
            'interaction_type': 'would_you_rather_discussion'
        })
        
        # Shuffle the questions
        random.shuffle(game_questions)
        
        return game_questions

def test_ultimate_1280_game():
    """Test the complete 1280 West game experience."""
    print("🎮 1280 WEST ULTIMATE SAVAGE TRIVIA GAME 🎮")
    print("=" * 60)
    print("📊 GAME COMPOSITION:")
    print("   📱 3 Group Chat Receipts (Lauren, Benny, Ian, Gina)")
    print("   🔥 4 Dirty Sex Trivia Questions")
    print("   🧠 5 Normal Trivia Questions")
    print("   �️ 2 Dirty 'Most Likely To' VOTING Questions")
    print("   🗣️ 1 Would You Rather DISCUSSION Question")
    print("   ────────────────────────────")
    print("   📋 TOTAL: 15 Questions Per Game")
    print()
    print("✅ LAUREN COWORKER AFFAIR: INCLUDED")
    print("✅ TOM ROASTING: ENABLED (he'll never play anyway)")
    print("✅ ALL 42 DIRTY MOST LIKELY TO QUESTIONS: LOADED")
    print("🔥 INTERACTIVE VOTING: Most Likely To questions")
    print("💬 INTERACTIVE DISCUSSION: Would You Rather questions")
    print()
    
    try:
        generator = Ultimate1280TriviaGenerator()
        game = generator.generate_complete_game()
        
        print("🎯 SAMPLE GAME ROUND:")
        print("=" * 60)
        
        category_counts = {}
        for q in game:
            cat = q['category']
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        print("📊 QUESTION BREAKDOWN:")
        for cat, count in category_counts.items():
            print(f"   {cat}: {count} questions")
        print()
        
        # Show first 5 questions as sample
        for i, q in enumerate(game[:5], 1):
            print(f"📱 QUESTION {i}/15")
            print(f"Category: {q['category']}")
            print(f"🔥 Savage Level: {q['savage_level']}/6")
            print()
            
            if q['type'] == 'interactive_discussion':
                print(f"🗣️ INTERACTIVE: {q['question_text']}")
                print(f"   A) {q['option_a']}")
                print(f"   B) {q['option_b']}")
                print("   💬 Everyone discusses and picks their choice!")
            elif q['type'] == 'interactive_voting':
                print(f"🗳️ VOTING: {q['question_text']}")
                print("   Voting Options:")
                for j, option in enumerate(q['voting_options'], 1):
                    print(f"   {j}. {option}")
                print("   👥 Everyone votes secretly, then results revealed!")
            else:
                print(f"❓ {q['question_text']}")
                if q['type'] in ['receipt', 'trivia']:
                    all_answers = [q['correct_answer']] + q['wrong_answers']
                    random.shuffle(all_answers)
                    for j, answer in enumerate(all_answers, 1):
                        marker = " ✅" if answer == q['correct_answer'] else ""
                        print(f"   {j}. {answer}{marker}")
            
            print(f"\n💭 Context: {q['context']}")
            if i < 5:
                print("-" * 40)
                print()
        
        print(f"\n... and {len(game) - 5} more questions!")
        
        print("\n🎯 ULTIMATE GAME STATS:")
        print("=" * 60)
        total_savage = sum(q['savage_level'] for q in game)
        avg_savage = total_savage / len(game)
        print(f"📊 Total Questions: {len(game)}")
        print(f"🔥 Average Savage Level: {avg_savage:.1f}/6")
        print(f"💀 Friendship Destruction: GUARANTEED")
        print(f"🏠 1280 West Authenticity: MAXIMUM")
        print(f"🔞 Adult Content Level: SPICY AS REQUESTED")
        print(f"😈 Lauren Coworker Affair Integration: COMPLETE")
        print(f"🎯 Tom Roasting Potential: UNLIMITED")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ultimate_1280_game()