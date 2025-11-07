#!/usr/bin/env python3
"""
SAVAGE MODE QUESTION GENERATOR
Creates absolutely ruthless trivia questions that will destroy friendships (in a fun way)
"""

import sys
from pathlib import Path
import random

# Add the backend directory to the Python path
backend_path = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_path))

class SavageQuestionGenerator:
    """Generates absolutely brutal questions that expose everyone's worst moments."""
    
    def __init__(self):
        # SAVAGE roast templates - way more brutal
        self.savage_roast_templates = [
            "Who's the absolute trainwreck that {action}?",
            "Which dumbass thought it was smart to {action}?", 
            "Who's the walking disaster that {action}?",
            "Which hot mess {action}?",
            "Who's the chaotic energy that {action}?",
            "Which absolute unit {action}?",
            "Who's the main character that {action}?",
            "Which crackhead energy person {action}?",
            "Who's got the audacity to {action}?",
            "Which unhinged bestie {action}?",
            "Who's the chaos gremlin that {action}?",
            "Which feral friend {action}?"
        ]
        
        # WAY more savage/dirty actions
        self.savage_actions = [
            "drunk texted their ex at 3am with a novel-length confession",
            "threw up in an Uber and didn't tip the driver",
            "got so wasted they woke up in someone else's bed with no memory",
            "shit themselves at a party and blamed it on the dog",
            "got kicked out of a bar for trying to fight the bouncer",
            "hooked up with someone and immediately regretted it",
            "sent nudes to the wrong person",
            "got so drunk they peed themselves in public",
            "started a fight over the last slice of pizza",
            "cried during sex",
            "got arrested for public intoxication",
            "threw up on their own shoes and kept wearing them",
            "got rejected by someone they thought was way out of their league",
            "slept with their ex's best friend",
            "got so high they called the police on themselves",
            "shit-talked someone then accidentally sent it to them",
            "got catfished and still went on the date",
            "tried to slide into DMs and got left on read",
            "got so drunk they proposed to a stranger",
            "puked and rallied at the same party three times",
            "got kicked out of their own birthday party",
            "hooked up in a public bathroom",
            "got so wasted they lost their keys, wallet, AND dignity",
            "drunk-ordered $300 worth of food they couldn't afford",
            "got rejected by someone they super-liked on Tinder",
            "tried to fight someone twice their size",
            "got so drunk they forgot their own address",
            "hooked up with someone just for the free Netflix password",
            "got so high they tried to pay for food with Monopoly money",
            "got dumped via text and responded with a 47-message rant"
        ]
        
        # Savage "most likely" scenarios
        self.savage_scenarios = [
            "accidentally send a nude to their mom",
            "get kicked out of a wedding for being too drunk",
            "hook up with someone just because they're bored",
            "start an OnlyFans account and tell everyone about it",
            "get arrested for something stupid while drunk",
            "cheat on their partner and immediately confess",
            "get so drunk they tattoo their ex's name on themselves",
            "slide into their professor's DMs",
            "get rejected by someone half their age",
            "shit themselves during a job interview",
            "get catfished by someone using a 10-year-old photo",
            "hook up with their roommate's ex",
            "get so high they order pizza to the wrong address",
            "drunk-call their boss to quit their job",
            "get kicked out of a strip club for being too handsy",
            "hook up with someone at a funeral",
            "get so drunk they wake up married in Vegas",
            "start a fight at a kids birthday party",
            "get rejected by an AI chatbot",
            "accidentally like their ex's Instagram post from 3 years ago"
        ]
        
        # Dirty relationship questions
        self.relationship_savagery = [
            "Who's most likely to fake an orgasm and get caught?",
            "Who definitely gives the worst head in the group?",
            "Who's most likely to cry during their first time?", 
            "Who would 100% cheat if they thought they wouldn't get caught?",
            "Who's most likely to pay for sex?",
            "Who's definitely never made anyone orgasm?",
            "Who's most likely to get an STD from a one night stand?",
            "Who would sleep with their ex's parent?",
            "Who's most likely to get pregnant from a one night stand?",
            "Who definitely lies about their body count?"
        ]
        
        # Financial/lifestyle savagery
        self.lifestyle_savagery = [
            "Who's most likely to be broke by 30 despite making good money?",
            "Who definitely still asks their parents for money?",
            "Who's most likely to live in a studio apartment forever?",
            "Who would sell feet pics for rent money?",
            "Who's most likely to get evicted for being a terrible tenant?",
            "Who definitely has the worst credit score?",
            "Who would steal from the tip jar?",
            "Who's most likely to get fired for showing up drunk?",
            "Who would definitely fail a drug test right now?",
            "Who's most likely to end up on a reality TV show for money?"
        ]

    def generate_savage_roast_question(self, names):
        """Generate a brutal roast question."""
        template = random.choice(self.savage_roast_templates)
        action = random.choice(self.savage_actions)
        
        correct_answer = random.choice(names)
        wrong_answers = random.sample([n for n in names if n != correct_answer], min(3, len(names)-1))
        
        return {
            'category': 'ABSOLUTE SAVAGERY',
            'question_type': 'roast',
            'question_text': template.format(action=action),
            'correct_answer': correct_answer,
            'wrong_answers': wrong_answers,
            'context': 'Based on your chaotic friend group energy',
            'difficulty': 5  # Maximum savage
        }
    
    def generate_savage_most_likely(self, names):
        """Generate a savage 'most likely' question."""
        scenario = random.choice(self.savage_scenarios)
        
        correct_answer = random.choice(names)
        wrong_answers = random.sample([n for n in names if n != correct_answer], min(3, len(names)-1))
        
        return {
            'category': 'DESTROY FRIENDSHIPS',
            'question_type': 'most_likely',
            'question_text': f"Who's most likely to {scenario}?",
            'correct_answer': correct_answer,
            'wrong_answers': wrong_answers,
            'context': 'This will ruin relationships',
            'difficulty': 5
        }
    
    def generate_relationship_savagery(self, names):
        """Generate dirty relationship questions."""
        question = random.choice(self.relationship_savagery)
        
        correct_answer = random.choice(names)
        wrong_answers = random.sample([n for n in names if n != correct_answer], min(3, len(names)-1))
        
        return {
            'category': 'SEXUAL DYSFUNCTION',
            'question_type': 'relationship_roast',
            'question_text': question,
            'correct_answer': correct_answer,
            'wrong_answers': wrong_answers,
            'context': 'TMI but we\'re going there',
            'difficulty': 6  # Beyond savage
        }
    
    def generate_lifestyle_savagery(self, names):
        """Generate questions about financial/lifestyle failures."""
        question = random.choice(self.lifestyle_savagery)
        
        correct_answer = random.choice(names)
        wrong_answers = random.sample([n for n in names if n != correct_answer], min(3, len(names)-1))
        
        return {
            'category': 'LIFE FAILURES',
            'question_type': 'lifestyle_roast',
            'question_text': question,
            'correct_answer': correct_answer,
            'wrong_answers': wrong_answers,
            'context': 'Reality check incoming',
            'difficulty': 6
        }

def main():
    print('💀 SAVAGE MODE 1280 TRIVIA - FRIENDSHIP DESTROYER EDITION')
    print('⚠️  WARNING: THIS WILL RUIN RELATIONSHIPS')
    print('=' * 70)
    
    # Real names from the chats
    real_names = ['Ian', 'Benny', 'Gina', 'Lauren']
    
    savage_gen = SavageQuestionGenerator()
    
    print(f'🎯 Target Victims: {", ".join(real_names)}')
    print('🔥 Generating maximum savage content...\n')
    
    # Generate 10 absolutely brutal questions
    question_types = [
        savage_gen.generate_savage_roast_question,
        savage_gen.generate_savage_most_likely, 
        savage_gen.generate_relationship_savagery,
        savage_gen.generate_lifestyle_savagery
    ]
    
    for i in range(10):
        question_func = random.choice(question_types)
        q = question_func(real_names)
        
        print(f'💀 ROUND {i+1} - {q["category"]}')
        print(f'🔥 {q["question_text"]}')
        print('')
        
        # Shuffle answers
        all_answers = [q['correct_answer']] + q['wrong_answers']
        random.shuffle(all_answers)
        
        for j, answer in enumerate(all_answers, 1):
            marker = '💀' if answer == q['correct_answer'] else '  '
            print(f'{marker} {chr(64+j)}) {answer}')
        
        print('')
        print(f'💬 {q["context"]}')
        print(f'🌶️  Savage Level: {"🔥" * q["difficulty"]}')
        
        if i < 9:
            print('-' * 50)
    
    print('\n' + '=' * 70)
    print('💀 CONGRATULATIONS - YOU\'VE UNLOCKED MAXIMUM SAVAGE MODE')
    print('⚠️  Side effects may include:')
    print('   - Destroyed friendships')
    print('   - Exposed secrets')
    print('   - Relationship drama')
    print('   - Emotional damage')
    print('   - People never speaking to each other again')
    print('\n🎉 ENJOY THE CHAOS! 💀')

if __name__ == "__main__":
    main()