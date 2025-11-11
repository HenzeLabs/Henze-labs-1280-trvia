"""MAXIMUM SAVAGE Question generators - Makes Cards Against Humanity look like Disney+"""

import random
from typing import List, Dict
from abc import ABC, abstractmethod

class QuestionGenerator(ABC):
    """Base class for absolutely brutal question generators."""
    
    @abstractmethod
    def generate_question(self, data: List[Dict]) -> Dict:
        """Generate a question that will destroy friendships."""
        pass

class ReceiptQuestionGenerator(QuestionGenerator):
    """Generates absolutely savage 'who said this?' questions that expose everyone."""
    
    def __init__(self):
        # Savage commentary prefixes for receipts
        self.savage_prefixes = [
            "Which absolute trainwreck said:",
            "Who had the audacity to text:",
            "Which hot mess actually wrote:",
            "Who's the disaster that messaged:",
            "Which chaotic energy sent:",
            "Who's the unhinged bestie that typed:",
            "Which crackhead energy person said:",
            "Who's the walking red flag that texted:",
            "Which feral friend actually wrote:",
            "Who's the main character that sent:"
        ]
    
    def _sanitize_pii(self, text: str) -> str:
        """
        Remove PII (phone numbers, addresses, email) from message text.
        PRIVACY FIX: Prevent exposing sensitive information in receipts.
        """
        import re

        # Remove phone numbers (various formats)
        text = re.sub(r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b', '[PHONE NUMBER]', text)
        text = re.sub(r'\b\(\d{3}\)\s?\d{3}[-.\s]?\d{4}\b', '[PHONE NUMBER]', text)

        # Remove email addresses
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)

        # Remove street addresses (basic pattern)
        text = re.sub(r'\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd|Court|Ct)\b', '[ADDRESS]', text, flags=re.IGNORECASE)

        # Remove zip codes
        text = re.sub(r'\b\d{5}(?:-\d{4})?\b', '[ZIP]', text)

        return text

    def generate_question(self, messages: List[Dict]) -> Dict:
        """Generate a savage 'who said this?' question."""
        if not messages:
            return None

        # Filter out bad messages
        reaction_prefixes = ['Liked ', 'Emphasized ', 'Loved ', 'Laughed at ', 'Questioned ', 'Disliked ']
        filtered_messages = []

        for msg in messages:
            text = msg.get('message_text', '')

            # Skip if it's a reaction
            if any(text.startswith(prefix) for prefix in reaction_prefixes):
                continue

            # Skip if it's a URL-only message
            if text.startswith('http://') or text.startswith('https://'):
                continue

            # Skip if message contains URLs (they're not interesting)
            if 'http://' in text or 'https://' in text:
                continue

            # Skip very short messages (less than 15 chars)
            if len(text) < 15:
                continue

            # PRIVACY FIX: Skip messages that might contain PII after sanitization
            sanitized = self._sanitize_pii(text)
            if '[PHONE NUMBER]' in sanitized or '[EMAIL]' in sanitized or '[ADDRESS]' in sanitized:
                continue  # Skip messages with PII entirely

            filtered_messages.append(msg)

        if not filtered_messages:
            return None

        # Pick a random message - prioritize embarrassing/funny ones
        savage_keywords = ['fuck', 'shit', 'drunk', 'wasted', 'regret', 'mistake', 'embarrass', 'fail', 'wtf', 'omg', 'sorry', 'help']

        # Try to find a spicy message first
        spicy_messages = [msg for msg in filtered_messages if any(keyword in msg['message_text'].lower() for keyword in savage_keywords)]
        message = random.choice(spicy_messages) if spicy_messages else random.choice(filtered_messages)
        
        # Convert "You" to "Lauren" so she can get roasted too!
        correct_sender = message['sender']
        if correct_sender == 'You':
            correct_sender = 'Lauren'
        
        # Truncate long messages for readability but keep the savage parts
        message_text = message['message_text']
        if len(message_text) > 120:
            message_text = message_text[:120] + "..."
        
        # Get other potential senders for wrong answers - INCLUDE LAUREN!
        all_senders = list(set([msg['sender'] if msg['sender'] != 'You' else 'Lauren' for msg in filtered_messages if msg['sender'] != correct_sender]))

        # Ensure we don't include the correct sender
        all_senders = [s for s in all_senders if s != correct_sender]

        wrong_answers = random.sample(all_senders, min(3, len(all_senders)))

        # If we don't have enough wrong answers, add some generic ones
        generic_names = ["Alex", "Jordan", "Taylor", "Casey", "Riley", "Morgan"]
        while len(wrong_answers) < 3:
            name = random.choice(generic_names)
            if name not in wrong_answers and name != correct_sender:
                wrong_answers.append(name)

        # Final safety check: ensure no duplicates and correct answer not in wrong answers
        wrong_answers = list(set(wrong_answers))[:3]
        wrong_answers = [ans for ans in wrong_answers if ans != correct_sender]
        
        # Use savage prefix randomly
        prefix = random.choice(self.savage_prefixes) if random.random() < 0.7 else "Who said:"
        
        question = {
            'category': 'RECEIPTS & REGRETS',
            'question_type': 'who_said_this',
            'question_text': f'{prefix} "{message_text}"?',
            'correct_answer': correct_sender,
            'wrong_answers': wrong_answers[:3],
            'context': f"Exposed from {message.get('chat_name', 'the group chat')}",
            'difficulty': random.randint(2, 4),
            'source_message_id': message.get('id')
        }
        
        return question

class RoastQuestionGenerator(QuestionGenerator):
    """Generates absolutely brutal roast questions that will end friendships."""
    
    def __init__(self):
        # MAXIMUM SAVAGE roast templates
        self.roast_templates = [
            "Which absolute disaster {action}?",
            "Who's the walking trainwreck that {action}?",
            "Which dumbass {action}?",
            "Who's the hot mess that {action}?",
            "Which chaotic energy person {action}?",
            "Who's the unhinged bestie that {action}?",
            "Which crackhead energy individual {action}?",
            "Who's the main character that {action}?",
            "Which feral friend {action}?",
            "Who's the absolute unit that {action}?",
            "Which walking red flag {action}?",
            "Who's the chaos gremlin that {action}?"
        ]
        
        # REAL 1280 WEST SAVAGE ACTIONS - Based on actual friend group dynamics
        self.embarrassing_actions = [
            "sleeps with their ex Taylor who they share 2 dogs with (Benny drama)",
            "gets the ick easily from guys they go on dates with",
            "gets so high they can't function in normal society", 
            "is the messiest person when it comes to dating",
            "had an affair with a coworker and still works with them (Lauren tea)",
            "makes the worst decisions when drunk (looking at you Benny & Lauren)",
            "tries to avoid Tom because he's shit-faced AND kicked a cop",
            "can't commit to plans or communicate if they're actually coming (Gina energy)",
            "gets mad at Gina for her terrible communication about plans",
            "lives across the hall from someone they used to hook up with",
            "pretends they don't see the dog shit everywhere in the building",
            "refuses to pick up dog poop when walking other people's dogs (Lauren)",
            "judges everyone's questionable dates in the group chat",
            "roasts people so hard it should be illegal",
            "is high literally all the time and we're concerned",
            "makes plans but we're never totally sure they'll show up",
            "is the only one without a dog but won't clean up poop when dog sitting",
            "gets stuck in the elevators that never work at 1280",
            "thinks Tom is creepy AND avoids him (everyone does this)",
            "has to see their affair partner at work every single day",
            "drunk texted their ex a 47-message novel at 3am",
            "shit themselves at a party and blamed the dog",
            "threw up in an Uber and didn't tip",
            "got so wasted they woke up in someone else's bed",
            "sent nudes to the wrong person (twice)",
            "got kicked out of their own birthday party",
            "hooked up with someone and immediately regretted it",
            "got rejected by someone half their age",
            "cried during sex",
            "got arrested for public intoxication",
            "puked on their own shoes and kept wearing them",
            "got so drunk they proposed to a stranger",
            "hooked up in a McDonald's bathroom",
            "got catfished and still went on the date",
            "tried to slide into their professor's DMs",
            "got so high they called 911 on themselves",
            "shit-talked someone then accidentally sent it to them",
            "got so drunk they forgot their own address",
            "tried to fight someone twice their size",
            "got dumped via text and responded with 50 messages",
            "hooked up with their roommate's ex",
            "got so wasted they peed themselves in public",
            "sent a dick pic to their mom by accident",
            "got rejected by an AI chatbot",
            "started a fight at a kid's birthday party",
            "got kicked out of a strip club for being too handsy",
            "drunk-ordered $400 worth of food they couldn't afford",
            "got so high they tried to pay with Monopoly money",
            "hooked up with someone just for the Netflix password",
            "got so drunk they woke up married in Vegas",
            "throwing up in public",
            "getting a haircut they immediately regretted",
            "buying something expensive while drunk online shopping"
        ]
    
    def generate_question(self, messages: List[Dict]) -> Dict:
        """Generate a roast question."""
        if not messages:
            return None
        
        # Get unique senders - INCLUDE LAUREN! Convert "You" to "Lauren"
        senders = list(set([msg['sender'] if msg['sender'] != 'You' else 'Lauren' for msg in messages if msg['sender']]))
        
        if len(senders) < 4:
            return None
        
        correct_answer = random.choice(senders)
        wrong_answers = random.sample([s for s in senders if s != correct_answer], 3)
        
        # Pick a random embarrassing action
        action = random.choice(self.embarrassing_actions)
        template = random.choice(self.roast_templates)
        
        question = {
            'category': 'Red Flags', 
            'question_type': 'roast',
            'question_text': template.format(action=action),
            'correct_answer': correct_answer,
            'wrong_answers': wrong_answers,
            'context': "Based on group chat patterns and inside jokes",
            'difficulty': 2
        }
        
        return question

class MostLikelyQuestionGenerator(QuestionGenerator):
    """Generates absolutely savage 'who's most likely to...' questions that expose everyone."""

    def __init__(self):
        self.used_scenarios = []  # Track used scenarios to prevent duplicates

        # Try to load from CSV first (only SCORED scenarios - ones with name callouts)
        try:
            from backend.app.generators.csv_loader import CSVQuestionLoader
            loader = CSVQuestionLoader()
            csv_data = loader.load_most_likely_scenarios()
            if csv_data and csv_data.get('scored'):
                self.most_likely_scenarios = csv_data['scored']
                return
        except Exception as e:
            pass  # Fall back to hardcoded

        # REAL 1280 WEST SAVAGE SCENARIOS - Based on actual friend dynamics
        self.most_likely_scenarios = [
            "get the ick easily from a guy they're dating",
            "sleep with their ex Taylor who they share 2 dogs with (Benny)",
            "not commit to plans or communicate if they're actually coming (Gina)",
            "be too high to function at a normal social event",
            "make the worst decision when drunk tonight",
            "avoid Tom because he's shit-faced AND kicked a cop",
            "refuse to pick up dog poop when walking other people's dogs",
            "get mad at someone for terrible communication about plans",
            "awkwardly run into their former hookup in the 1280 West hallway",
            "pretend they don't see the dog shit everywhere in the building",
            "judge someone's questionable date choice in the group chat",
            "roast someone so hard they need therapy",
            "be high right now while playing this game",
            "say they're coming but we're still not totally sure",
            "live across the hall from someone they used to sleep with",
            "be the only one without a dog but refuse to clean up when dog sitting",
            "get stuck in the 1280 elevators that never work",
            "think Tom is creepy (everyone agrees on this)",
            "be the messiest person when it comes to dating",
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
            "hook up with their roommate's ex for revenge",
            "get so high they order pizza to the wrong address",
            "drunk-call their boss to quit their job",
            "get kicked out of a strip club for being too handsy",
            "hook up with someone at a funeral",
            "get so drunk they wake up married in Vegas",
            "start a fight at a kids birthday party",
            "get rejected by an AI chatbot romantically",
            "accidentally like their ex's Instagram post from 3 years ago",
            "fake an orgasm and get caught",
            "pay for sex and tell everyone about it",
            "get an STD from a one night stand",
            "cry during their first time having sex",
            "sleep with their ex's parent",
            "get pregnant from a one night stand",
            "lie about their body count by 500%",
            "send dick pics to get free food",
            "hook up with someone for their Netflix password",
            "get so desperate they slide into LinkedIn DMs"
        ]
    
    def generate_question(self, messages: List[Dict]) -> Dict:
        """Generate a 'most likely' question."""
        if not messages:
            return None

        # Get unique senders - INCLUDE LAUREN AS A ROAST TARGET!
        senders = list(set([msg['sender'] if msg['sender'] != 'You' else 'Lauren' for msg in messages if msg['sender']]))

        if len(senders) < 4:
            return None

        correct_answer = random.choice(senders)
        wrong_answers = random.sample([s for s in senders if s != correct_answer], 3)

        # Get available scenarios (not yet used)
        available = [s for s in self.most_likely_scenarios if s not in self.used_scenarios]

        # If all used, reset
        if not available:
            self.used_scenarios = []
            available = self.most_likely_scenarios

        scenario = random.choice(available)
        self.used_scenarios.append(scenario)
        
        question = {
            'category': 'Degenerate of the Week',
            'question_type': 'most_likely',
            'question_text': f"Who's most likely to {scenario}?",
            'correct_answer': correct_answer,
            'wrong_answers': wrong_answers,
            'context': "Based on personality analysis from chat patterns",
            'difficulty': 2
        }
        
        return question

class NormalTriviaGenerator(QuestionGenerator):
    """Generates 'normal' trivia questions - except 50% are about sex because we're savage like that."""

    def __init__(self):
        self.used_questions = []  # Track used questions to prevent duplicates

        # Try to load from CSV first
        try:
            from backend.app.generators.csv_loader import CSVQuestionLoader
            loader = CSVQuestionLoader()
            csv_data = loader.load_all()

            # Combine CSV questions if available
            if csv_data['sex_trivia'] or csv_data['regular_trivia']:
                self.trivia_questions = []
                # Add all CSV questions
                for q in csv_data['sex_trivia']:
                    self.trivia_questions.append(q)
                for q in csv_data['regular_trivia']:
                    self.trivia_questions.append(q)

                if self.trivia_questions:
                    return
        except Exception as e:
            pass  # Fall back to hardcoded

        # 50% SEX QUESTIONS disguised as "normal" trivia
        self.trivia_questions = [
            # Sex/Adult Questions (disguised as trivia)
            {
                'question': "What's the average duration of penetrative sex according to studies?",
                'correct': "5.4 minutes",
                'wrong': ["15 minutes", "2 minutes", "30 minutes"]
            },
            {
                'question': "Which dating app is known for being primarily for hookups?",
                'correct': "Tinder", 
                'wrong': ["eHarmony", "Match.com", "Christian Mingle"]
            },
            {
                'question': "What percentage of people have had a one-night stand?",
                'correct': "About 66%",
                'wrong': ["About 25%", "About 90%", "About 10%"]
            },
            {
                'question': "Which country has the highest rate of casual sex?",
                'correct': "Finland",
                'wrong': ["United States", "Brazil", "France"]
            },
            {
                'question': "What's the most common safe word used during kinky activities?",
                'correct': "Red",
                'wrong': ["Stop", "Banana", "Safe"]
            },
            {
                'question': "At what age do most people lose their virginity in the US?",
                'correct': "17",
                'wrong': ["15", "19", "21"]
            },
            {
                'question': "Which sex toy was originally invented to treat 'hysteria' in women?",
                'correct': "Vibrator",
                'wrong': ["Dildo", "Butt plug", "Handcuffs"]
            },
            {
                'question': "What's the most popular porn category globally?",
                'correct': "MILF",
                'wrong': ["Teen", "Big Ass", "Anal"]
            },
            {
                'question': "How many times does the average person masturbate per week?",
                'correct': "4-5 times",
                'wrong': ["Once", "10+ times", "Never"]
            },
            {
                'question': "What's the scientific term for a foot fetish?",
                'correct': "Podophilia",
                'wrong': ["Footosis", "Pedalism", "Toephilia"]
            },
            
            # Savage 'Normal' Questions with attitude
            {
                'question': "What year did your parents probably conceive you? (iPhone release)",
                'correct': "2007",
                'wrong': ["2005", "2008", "2006"]
            },
            {
                'question': "Which planet is as dead as your dating life?",
                'correct': "Mercury", 
                'wrong': ["Venus", "Earth", "Mars"]
            },
            {
                'question': "What does 'DTF' stand for in dating?",
                'correct': "Down To F*ck",
                'wrong': ["Down To Fight", "Down To Flirt", "Date Time Friday"]
            },
            {
                'question': "Which city has the most desperate people on dating apps?",
                'correct': "New York",
                'wrong': ["Los Angeles", "Chicago", "Boston"]
            },
            {
                'question': "Which streaming service has the most Netflix and chill sessions?",
                'correct': "Netflix",
                'wrong': ["Hulu", "Amazon Prime", "HBO Max"]
            },
            {
                'question': "What does 'BBC' mean in a sexual context?",
                'correct': "Big Black C*ck",
                'wrong': ["British Broadcasting Corporation", "Big Beautiful Curves", "Best Bedroom Connection"]
            },
            {
                'question': "Which social media platform is basically for thirst traps now?",
                'correct': "Instagram",
                'wrong': ["Facebook", "Twitter", "LinkedIn"]
            },
            {
                'question': "What's the most common excuse for a bad sexual performance?",
                'correct': "I was drunk",
                'wrong': ["I was tired", "It's my first time", "You're too hot"]
            },
            {
                'question': "Which app is most likely to give you an STD?",
                'correct': "Grindr",
                'wrong': ["Bumble", "Hinge", "Coffee Meets Bagel"]
            },
            {
                'question': "What's the average number of sexual partners people claim to have?",
                'correct': "7",
                'wrong': ["3", "15", "25"]
            },

            # REGULAR TRIVIA (Non-sex questions)
            {
                'question': "What year did the iPhone first launch?",
                'correct': "2007",
                'wrong': ["2005", "2008", "2006"]
            },
            {
                'question': "What is the capital of Australia?",
                'correct': "Canberra",
                'wrong': ["Sydney", "Melbourne", "Brisbane"]
            },
            {
                'question': "How many bones are in the adult human body?",
                'correct': "206",
                'wrong': ["215", "198", "220"]
            },
            {
                'question': "Which planet is closest to the sun?",
                'correct': "Mercury",
                'wrong': ["Venus", "Mars", "Earth"]
            },
            {
                'question': "Who painted the Mona Lisa?",
                'correct': "Leonardo da Vinci",
                'wrong': ["Michelangelo", "Raphael", "Donatello"]
            },
            {
                'question': "What is the longest river in the world?",
                'correct': "The Nile",
                'wrong': ["Amazon", "Yangtze", "Mississippi"]
            },
            {
                'question': "How many Harry Potter books are there?",
                'correct': "7",
                'wrong': ["6", "8", "5"]
            },
            {
                'question': "What year did World War II end?",
                'correct': "1945",
                'wrong': ["1944", "1946", "1943"]
            },
            {
                'question': "What is the smallest country in the world?",
                'correct': "Vatican City",
                'wrong': ["Monaco", "San Marino", "Liechtenstein"]
            },
            {
                'question': "How many continents are there?",
                'correct': "7",
                'wrong': ["6", "8", "5"]
            },
            {
                'question': "What's the most-watched series on Netflix?",
                'correct': "Squid Game",
                'wrong': ["Stranger Things", "Wednesday", "Bridgerton"]
            },
            {
                'question': "What year was Facebook founded?",
                'correct': "2004",
                'wrong': ["2005", "2003", "2006"]
            },
            {
                'question': "How many strings does a standard guitar have?",
                'correct': "6",
                'wrong': ["7", "5", "8"]
            },
            {
                'question': "What is the largest ocean on Earth?",
                'correct': "Pacific Ocean",
                'wrong': ["Atlantic Ocean", "Indian Ocean", "Arctic Ocean"]
            },
            {
                'question': "Who wrote '1984'?",
                'correct': "George Orwell",
                'wrong': ["Aldous Huxley", "Ray Bradbury", "Isaac Asimov"]
            },
            {
                'question': "How many players are on a basketball team on the court?",
                'correct': "5",
                'wrong': ["6", "7", "4"]
            },
            {
                'question': "What is the chemical symbol for gold?",
                'correct': "Au",
                'wrong': ["Go", "Gd", "Ag"]
            },
            {
                'question': "What is the tallest building in the world?",
                'correct': "Burj Khalifa",
                'wrong': ["Shanghai Tower", "One World Trade Center", "Empire State Building"]
            },
            {
                'question': "What year did the Titanic sink?",
                'correct': "1912",
                'wrong': ["1911", "1913", "1910"]
            },
            {
                'question': "How many states are in the United States?",
                'correct': "50",
                'wrong': ["48", "52", "51"]
            }
        ]
    
    def generate_question(self, messages: List[Dict] = None, question_type: str = None) -> Dict:
        """Generate a trivia question - either sex trivia or regular trivia."""

        # Separate sex questions from regular questions
        sex_keywords = ['sex', 'masturbat', 'orgasm', 'dtf', 'bbc', 'penetrative', 'vibrator', 'porn', 'hookup', 'kinky', 'grindr', 'std', 'sexual']

        sex_questions = []
        regular_questions = []

        for trivia in self.trivia_questions:
            # Skip if already used
            if trivia['question'] in self.used_questions:
                continue

            is_sex = any(word in trivia['question'].lower() for word in sex_keywords)
            if is_sex:
                sex_questions.append(trivia)
            else:
                regular_questions.append(trivia)

        # Pick the right pool based on question_type parameter
        if question_type == 'sex':
            if not sex_questions:
                # Fallback if no sex questions available (or all used)
                available = [t for t in self.trivia_questions if t['question'] not in self.used_questions]
                if not available:
                    # Reset if we've used all questions
                    self.used_questions = []
                    available = self.trivia_questions
                trivia = random.choice(available)
            else:
                trivia = random.choice(sex_questions)
            category = "SEXY TIME TRIVIA"
            context = "Educational content for adults"
            difficulty = 3
        elif question_type == 'regular':
            if not regular_questions:
                # Fallback if no regular questions available (or all used)
                available = [t for t in self.trivia_questions if t['question'] not in self.used_questions]
                if not available:
                    # Reset if we've used all questions
                    self.used_questions = []
                    available = self.trivia_questions
                trivia = random.choice(available)
            else:
                trivia = random.choice(regular_questions)
            category = "GENERAL KNOWLEDGE"
            context = "Classic trivia"
            difficulty = 2
        else:
            # Random if not specified
            available = [t for t in self.trivia_questions if t['question'] not in self.used_questions]
            if not available:
                # Reset if we've used all questions
                self.used_questions = []
                available = self.trivia_questions
            trivia = random.choice(available)
            is_sex_question = any(word in trivia['question'].lower() for word in sex_keywords)
            category = "SEXY TIME TRIVIA" if is_sex_question else "GENERAL KNOWLEDGE"
            context = "Educational content for adults" if is_sex_question else "Classic trivia"
            difficulty = 3 if is_sex_question else 2

        # Mark this question as used
        self.used_questions.append(trivia['question'])

        question = {
            'category': category,
            'question_type': 'trivia',
            'question_text': trivia['question'],
            'correct_answer': trivia['correct'],
            'wrong_answers': trivia['wrong'],
            'context': context,
            'difficulty': difficulty
        }

        return question

    def reset_used_questions(self):
        """Reset the used questions list for a new game."""
        self.used_questions = []

class PollQuestionGenerator(QuestionGenerator):
    """Generates poll questions where players vote on who's most likely to do depraved shit."""

    def __init__(self):
        self.used_questions = []  # Track used questions to prevent duplicates

        # Try to load from CSV first
        try:
            from backend.app.generators.csv_loader import CSVQuestionLoader
            loader = CSVQuestionLoader()

            # Load explicit poll questions
            csv_questions = loader.load_poll_questions()

            # Also load generic "most likely" scenarios that should be polls
            most_likely_data = loader.load_most_likely_scenarios()
            poll_scenarios = most_likely_data.get('poll', []) if most_likely_data else []

            # Convert poll scenarios to full questions
            poll_from_scenarios = [f"Who's most likely to {s}?" for s in poll_scenarios]

            # Combine both sources
            if csv_questions or poll_from_scenarios:
                self.poll_questions = csv_questions + poll_from_scenarios
                return
        except Exception as e:
            pass  # Fall back to hardcoded

        # MAXIMUM PERVY & GAY poll scenarios - converted to "Who's most likely to..."
        self.poll_questions = [
            "Who's most likely to eat ass on the first date?",
            "Who's most likely to hook up with their ex's dad?",
            "Who's most likely to have a threesome with two people they hate?",
            "Who's most likely to accidentally send nudes to their entire contact list?",
            "Who's most likely to give a rimjob to a stranger?",
            "Who's most likely to refuse to have sex with the lights on?",
            "Who's most likely to sleep with a celebrity and be disappointed?",
            "Who's most likely to lie about their body count?",
            "Who's most likely to do a nude TikTok dance for clout?",
            "Who's most likely to use Grindr at Thanksgiving dinner?",
            "Who's most likely to bottom for someone with a micropenis?",
            "Who's most likely to have their Pornhub history exposed?",
            "Who's most likely to fuck someone dressed as a furry?",
            "Who's most likely to moan their own name during sex?",
            "Who's most likely to hook up in a McDonald's bathroom?",
            "Who's most likely to want a dick that plays music when hard?",
            "Who's most likely to get caught watching gay porn by their grandma?",
            "Who's most likely to use 'uwu' speak during sex?",
            "Who's most likely to match with their therapist on Tinder?",
            "Who's most likely to wear a butt plug to work?",
            "Who's most likely to get fisted by someone with long nails?",
            "Who's most likely to have their nudes leaked?",
            "Who's most likely to have sex in an Uber?",
            "Who's most likely to cry after sex?",
            "Who's most likely to have kinky shit written on their forehead?"
        ]

    def generate_question(self, messages: List[Dict] = None) -> Dict:
        """Generate a poll question where players vote on who's most likely."""

        # Get available questions (not yet used)
        available = [q for q in self.poll_questions if q not in self.used_questions]

        # If all questions used, reset the list
        if not available:
            self.used_questions = []
            available = self.poll_questions

        question_text = random.choice(available)

        # Mark as used
        self.used_questions.append(question_text)

        # Player names as options (shuffled each game for fairness)
        player_names = ["Benny", "Gina", "Ian", "Lauren"]
        random.shuffle(player_names)

        # For polls, there's no "correct" answer - whoever gets most votes wins
        # But we need to pick one as "correct" for the data structure
        # The game engine will handle scoring based on vote counts instead
        correct = player_names[0]  # Placeholder - actual winner determined by votes
        wrong = player_names[1:]

        question = {
            'category': 'WHO\'S MOST LIKELY',
            'question_type': 'poll',  # Special type for vote-based questions
            'question_text': question_text,
            'correct_answer': correct,
            'wrong_answers': wrong,
            'context': "Vote for who you think is most likely - whoever gets the most votes wins points!",
            'difficulty': 5
        }

        return question

    def reset_used_questions(self):
        """Reset the used questions list for a new game."""
        self.used_questions = []

class QuestionGeneratorManager:
    """Manages all question generators and creates balanced question sets."""

    def __init__(self):
        self.generators = {
            'receipts': ReceiptQuestionGenerator(),
            'roast': RoastQuestionGenerator(),
            'most_likely': MostLikelyQuestionGenerator(),
            'trivia': NormalTriviaGenerator(),
            'poll': PollQuestionGenerator()
        }

        # Try to load personalized generator
        try:
            from backend.app.generators.personalized_generator import PersonalizedQuestionGenerator
            self.generators['personalized'] = PersonalizedQuestionGenerator()
            print("✅ Personalized question generator loaded!")
        except Exception as e:
            print(f"⚠️  Personalized generator not available: {e}")
            self.generators['personalized'] = None
    
    def generate_question_set(self, messages: List[Dict], num_questions: int = 10) -> List[Dict]:
        """Generate balanced question mix that scales with num_questions."""
        questions = []

        # Calculate distribution based on num_questions
        # Base percentages: Receipt 7%, Roast 7%, Most Likely 20%, Sex Trivia 20%, Regular Trivia 33%, Poll 13%
        if num_questions <= 5:
            # For very small games, use simplified distribution
            receipt_count = 1 if num_questions >= 5 else 0
            roast_count = 0
            likely_count = 1 if num_questions >= 3 else 0
            sex_trivia_count = 1 if num_questions >= 4 else 0
            poll_count = 1 if num_questions >= 2 else 0
            regular_trivia_count = max(1, num_questions - (receipt_count + roast_count + likely_count + sex_trivia_count + poll_count))
        else:
            # Normal distribution for larger games
            receipt_count = max(1, int(num_questions * 0.07))
            roast_count = max(1, int(num_questions * 0.07))
            likely_count = max(1, int(num_questions * 0.20))
            sex_trivia_count = max(1, int(num_questions * 0.20))
            poll_count = max(1, int(num_questions * 0.13))

            # Regular trivia fills the rest
            total_so_far = receipt_count + roast_count + likely_count + sex_trivia_count + poll_count
            regular_trivia_count = max(1, num_questions - total_so_far)

        # Calculate personalized question count (if available)
        # CONTENT FIX: Increase personalized questions to 2-3 per game (they're GOLD!)
        personalized_count = 0
        if self.generators.get('personalized') and num_questions >= 8:
            # For games with 8+ questions, include 2-3 personalized questions
            if num_questions >= 15:
                personalized_count = 3  # 3 for long games
            elif num_questions >= 10:
                personalized_count = 2  # 2 for medium games
            else:
                personalized_count = 1  # 1 for short games
            roast_count = max(0, roast_count - personalized_count)

        print(f"🎮 Question Mix ({num_questions} total): {receipt_count} receipt, {roast_count} roast, {personalized_count} personalized, {likely_count} most likely, {sex_trivia_count} sex trivia, {regular_trivia_count} regular trivia, {poll_count} poll")

        # Generate receipt question
        for _ in range(receipt_count):
            try:
                question = self.generators['receipts'].generate_question(messages)
                if question:
                    questions.append(question)
            except Exception as e:
                print(f"Error generating receipt question: {e}")

        # Generate personalized questions (from questionnaire data)
        for _ in range(personalized_count):
            try:
                if self.generators.get('personalized'):
                    question = self.generators['personalized'].generate_question()
                    if question:
                        questions.append(question)
            except Exception as e:
                print(f"Error generating personalized question: {e}")

        # Generate roast question
        for _ in range(roast_count):
            try:
                question = self.generators['roast'].generate_question(messages)
                if question:
                    questions.append(question)
            except Exception as e:
                print(f"Error generating roast question: {e}")

        # Generate most likely questions
        for _ in range(likely_count):
            try:
                question = self.generators['most_likely'].generate_question(messages)
                if question:
                    questions.append(question)
            except Exception as e:
                print(f"Error generating most likely question: {e}")

        # Generate sex trivia questions
        for _ in range(sex_trivia_count):
            try:
                question = self.generators['trivia'].generate_question(question_type='sex')
                if question:
                    questions.append(question)
            except Exception as e:
                print(f"Error generating sex trivia question: {e}")

        # Generate regular trivia questions
        for _ in range(regular_trivia_count):
            try:
                question = self.generators['trivia'].generate_question(question_type='regular')
                if question:
                    questions.append(question)
            except Exception as e:
                print(f"Error generating regular trivia question: {e}")

        # Generate Poll questions
        for _ in range(poll_count):
            try:
                question = self.generators['poll'].generate_question()
                if question:
                    questions.append(question)
            except Exception as e:
                print(f"Error generating poll question: {e}")

        # Shuffle the questions
        random.shuffle(questions)

        return questions
    
    def generate_single_question(self, question_type: str, messages: List[Dict] = None) -> Dict:
        """Generate a single question of a specific type."""
        if question_type not in self.generators:
            raise ValueError(f"Unknown question type: {question_type}")
        
        generator = self.generators[question_type]
        if question_type == 'trivia':
            return generator.generate_question()
        else:
            return generator.generate_question(messages)