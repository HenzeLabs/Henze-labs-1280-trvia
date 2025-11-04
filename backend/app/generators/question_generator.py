"""Question generators for different types of trivia questions."""

import random
from typing import List, Dict
from abc import ABC, abstractmethod

class QuestionGenerator(ABC):
    """Base class for question generators."""
    
    @abstractmethod
    def generate_question(self, data: List[Dict]) -> Dict:
        """Generate a question from the provided data."""
        pass

class ReceiptQuestionGenerator(QuestionGenerator):
    """Generates 'who said this?' questions from chat messages."""
    
    def generate_question(self, messages: List[Dict]) -> Dict:
        """Generate a 'who said this?' question."""
        if not messages:
            return None
        
        # Pick a random message
        message = random.choice(messages)
        correct_sender = message['sender']
        
        # Truncate long messages for readability
        message_text = message['message_text']
        if len(message_text) > 150:
            message_text = message_text[:150] + "..."
        
        # Get other potential senders for wrong answers
        all_senders = list(set([msg['sender'] for msg in messages if msg['sender'] != correct_sender]))
        wrong_answers = random.sample(all_senders, min(3, len(all_senders)))
        
        # If we don't have enough wrong answers, add some generic ones
        generic_names = ["Alex", "Jordan", "Taylor", "Casey", "Riley", "Morgan"]
        while len(wrong_answers) < 3:
            name = random.choice(generic_names)
            if name not in wrong_answers and name != correct_sender:
                wrong_answers.append(name)
        
        question = {
            'category': 'Receipts',
            'question_type': 'who_said_this',
            'question_text': f'Who said: "{message_text}"?',
            'correct_answer': correct_sender,
            'wrong_answers': wrong_answers[:3],
            'context': f"From {message['chat_name']}",
            'difficulty': 1,
            'source_message_id': message.get('id')
        }
        
        return question

class RoastQuestionGenerator(QuestionGenerator):
    """Generates roast-style questions about embarrassing moments."""
    
    def __init__(self):
        self.roast_templates = [
            "Who was caught {action}?",
            "Who embarrassed themselves by {action}?", 
            "Who had the brilliant idea to {action}?",
            "Who thought it was a good idea to {action}?",
            "Who was the genius that decided to {action}?",
            "Who pulled a classic move and {action}?",
            "Who lived up to their reputation by {action}?",
        ]
        
        self.embarrassing_actions = [
            "drunk texting their ex",
            "falling asleep in an Uber",
            "getting locked out in their underwear", 
            "crying at a rom-com",
            "eating an entire pizza by themselves",
            "getting too drunk at brunch",
            "sliding into the wrong person's DMs",
            "wearing the same outfit two days in a row",
            "forgetting to mute themselves on a work call",
            "ordering food to the wrong address",
            "leaving their phone in an Uber",
            "getting kicked out of a bar",
            "throwing up in public",
            "getting a haircut they immediately regretted",
            "buying something expensive while drunk online shopping"
        ]
    
    def generate_question(self, messages: List[Dict]) -> Dict:
        """Generate a roast question."""
        if not messages:
            return None
        
        # Get unique senders
        senders = list(set([msg['sender'] for msg in messages if msg['sender'] != 'You']))
        
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
    """Generates 'who's most likely to...' questions."""
    
    def __init__(self):
        self.most_likely_scenarios = [
            "skip work to binge-watch Netflix",
            "accidentally like an ex's Instagram post from 2 years ago", 
            "eat cereal for dinner three nights in a row",
            "get lost in their own neighborhood",
            "buy something they don't need because it was on sale",
            "forget someone's name immediately after being introduced",
            "order way too much food for delivery",
            "fall asleep during a movie in theaters",
            "text the wrong person something embarrassing",
            "get distracted by their phone and walk into something",
            "impulse buy a pet without telling anyone",
            "start a new hobby and abandon it within a week",
            "accidentally reveal a surprise party",
            "get into an argument with a customer service chatbot",
            "spend an entire day in pajamas",
            "order food while already eating food",
            "pretend to understand a reference they don't get",
            "get emotional over a commercial",
            "lose their keys inside their own apartment",
            "stay up until 3am watching conspiracy theory videos"
        ]
    
    def generate_question(self, messages: List[Dict]) -> Dict:
        """Generate a 'most likely' question."""
        if not messages:
            return None
        
        # Get unique senders
        senders = list(set([msg['sender'] for msg in messages if msg['sender'] != 'You']))
        
        if len(senders) < 4:
            return None
        
        correct_answer = random.choice(senders)
        wrong_answers = random.sample([s for s in senders if s != correct_answer], 3)
        
        scenario = random.choice(self.most_likely_scenarios)
        
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
    """Generates normal trivia questions for variety."""
    
    def __init__(self):
        self.trivia_questions = [
            {
                'question': "What year was the iPhone first released?",
                'correct': "2007",
                'wrong': ["2005", "2008", "2006"]
            },
            {
                'question': "Which planet is closest to the Sun?",
                'correct': "Mercury", 
                'wrong': ["Venus", "Earth", "Mars"]
            },
            {
                'question': "What does 'HTTP' stand for?",
                'correct': "HyperText Transfer Protocol",
                'wrong': ["Home Tool Transfer Protocol", "HyperText Transport Process", "High Transfer Text Protocol"]
            },
            {
                'question': "Which city is known as 'The Big Apple'?",
                'correct': "New York",
                'wrong': ["Los Angeles", "Chicago", "Boston"]
            },
            {
                'question': "What is the capital of Australia?",
                'correct': "Canberra",
                'wrong': ["Sydney", "Melbourne", "Perth"]
            },
            {
                'question': "Which streaming service produced 'Stranger Things'?", 
                'correct': "Netflix",
                'wrong': ["Hulu", "Amazon Prime", "HBO Max"]
            },
            {
                'question': "What does 'CPU' stand for?",
                'correct': "Central Processing Unit",
                'wrong': ["Computer Processing Unit", "Central Program Unit", "Core Processing Unit"]
            },
            {
                'question': "Which social media platform was originally called 'The Facebook'?",
                'correct': "Facebook",
                'wrong': ["Instagram", "Twitter", "Snapchat"]
            },
            {
                'question': "What is the most abundant gas in Earth's atmosphere?",
                'correct': "Nitrogen",
                'wrong': ["Oxygen", "Carbon Dioxide", "Argon"]
            },
            {
                'question': "Which company owns YouTube?",
                'correct': "Google",
                'wrong': ["Facebook", "Microsoft", "Apple"]
            }
        ]
    
    def generate_question(self, messages: List[Dict] = None) -> Dict:
        """Generate a normal trivia question."""
        trivia = random.choice(self.trivia_questions)
        
        question = {
            'category': 'Random Trivia',
            'question_type': 'trivia',
            'question_text': trivia['question'],
            'correct_answer': trivia['correct'],
            'wrong_answers': trivia['wrong'],
            'context': "General knowledge trivia",
            'difficulty': 1
        }
        
        return question

class QuestionGeneratorManager:
    """Manages all question generators and creates balanced question sets."""
    
    def __init__(self):
        self.generators = {
            'receipts': ReceiptQuestionGenerator(),
            'roast': RoastQuestionGenerator(), 
            'most_likely': MostLikelyQuestionGenerator(),
            'trivia': NormalTriviaGenerator()
        }
    
    def generate_question_set(self, messages: List[Dict], num_questions: int = 10) -> List[Dict]:
        """Generate a balanced set of questions."""
        questions = []
        
        # Calculate distribution based on config ratios
        receipt_count = int(num_questions * 0.3)  # 30% receipt questions
        roast_count = int(num_questions * 0.2)    # 20% roast questions  
        likely_count = int(num_questions * 0.2)   # 20% most likely questions
        trivia_count = num_questions - receipt_count - roast_count - likely_count  # remaining normal trivia
        
        # Generate receipt questions
        for _ in range(receipt_count):
            try:
                question = self.generators['receipts'].generate_question(messages)
                if question:
                    questions.append(question)
            except Exception as e:
                print(f"Error generating receipt question: {e}")
        
        # Generate roast questions
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
        
        # Generate normal trivia questions
        for _ in range(trivia_count):
            try:
                question = self.generators['trivia'].generate_question()
                if question:
                    questions.append(question)
            except Exception as e:
                print(f"Error generating trivia question: {e}")
        
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