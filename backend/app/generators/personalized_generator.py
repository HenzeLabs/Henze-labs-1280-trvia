"""
Personalized Question Generator
Uses friend group questionnaire data to create savage, ultra-personalized questions.
"""

import csv
import random
from typing import Dict, List, Optional
from pathlib import Path

class PersonalizedQuestionGenerator:
    """Generates questions from friend group questionnaire data."""

    def __init__(self, csv_path: str = "friend_group_data.csv"):
        self.data = self._load_data(csv_path)
        self.players = ["Benny", "Gina", "Ian", "Lauren"]
        self.used_questions = set()

    def _load_data(self, csv_path: str) -> Dict:
        """Load questionnaire data from CSV."""
        data = {}

        csv_file = Path(csv_path)
        if not csv_file.exists():
            # Try relative to project root
            csv_file = Path(__file__).parent.parent.parent.parent / csv_path

        if not csv_file.exists():
            print(f"⚠️  Questionnaire data not found at {csv_path}")
            return data

        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                player_name = row.get('playerName', '').strip()
                if player_name:
                    data[player_name] = row

        print(f"✅ Loaded questionnaire data for {len(data)} players")
        return data

    def generate_roast_question(self) -> Optional[Dict]:
        """Generate a roast question based on submitted roasts."""
        roast_fields = [
            ('bennysRedFlag', 'Benny'),
            ('ginasRoastableQuality', 'Gina'),
            ('iansBadDecision', 'Ian'),
            ('laurenWarningLabel', 'Lauren')
        ]

        available = [(field, name) for field, name in roast_fields
                     if (field, name) not in self.used_questions]

        if not available:
            self.used_questions.clear()  # Reset if all used
            available = roast_fields

        field, correct_name = random.choice(available)
        self.used_questions.add((field, correct_name))

        # Get the actual roast text
        roast_text = None
        for player_data in self.data.values():
            if player_data.get(field):
                roast_text = player_data[field]
                break

        if not roast_text:
            return None

        # Create question
        other_players = [p for p in self.players if p != correct_name]
        random.shuffle(other_players)

        prompts = [
            f"Who got called out for: \"{roast_text}\"?",
            f"Which friend got roasted with: \"{roast_text}\"?",
            f"Who deserves this read: \"{roast_text}\"?",
            f"Whose red flag is: \"{roast_text}\"?"
        ]

        return {
            'category': 'Personal Receipts',
            'question_type': 'personalized_roast',
            'question_text': random.choice(prompts),
            'correct_answer': correct_name,
            'wrong_answers': other_players[:3],
            'context': 'Straight from the questionnaire!',
            'difficulty': 10
        }

    def generate_ranking_question(self) -> Optional[Dict]:
        """Generate a question based on 'most likely to' rankings."""
        ranking_questions = [
            ('hookupWithEx', 'hook up with their ex again'),
            ('kickedOutBar', 'get kicked out of a bar'),
            ('winDrunkArgument', 'win a drunk argument'),
            ('fallInLoveSituationship', 'fall in love with a situationship'),
            ('overshareStranger', 'overshare to a stranger'),
            ('biggestGossip', 'be the biggest gossip'),
            ('exposeSecretAccidentally', 'accidentally expose a secret')
        ]

        question_id, action = random.choice(ranking_questions)

        # Get rankings from the data (1 = most likely, 4 = least likely)
        rankings = {}
        for player_name in self.players:
            field = f'rank{question_id.capitalize()}_{player_name}'
            for player_data in self.data.values():
                rank_str = player_data.get(field, '4')
                try:
                    rankings[player_name] = int(rank_str)
                except (ValueError, TypeError):
                    rankings[player_name] = 4

        # Find who was ranked #1 (most likely)
        correct_name = min(rankings, key=rankings.get)

        other_players = [p for p in self.players if p != correct_name]
        random.shuffle(other_players)

        return {
            'category': 'Group Consensus',
            'question_type': 'personalized_ranking',
            'question_text': f"According to the group rankings, who's MOST likely to {action}?",
            'correct_answer': correct_name,
            'wrong_answers': other_players[:3],
            'context': 'Based on your submitted rankings!',
            'difficulty': 7
        }

    def generate_evidence_question(self) -> Optional[Dict]:
        """Generate questions using specific evidence/stories submitted."""
        evidence_questions = [
            ('embarrassingDrunkMoment', 'embarrassing drunk moment'),
            ('dumbestThingForLove', 'dumbest thing they did for love'),
            ('worstDatingAppExperience', 'worst dating app experience'),
            ('chaotic1280Story', 'most chaotic 1280 story'),
            ('thirstiestPersonEvidence', 'evidence of being the thirstiest person')
        ]

        field, description = random.choice(evidence_questions)

        # Get all evidence for this field
        evidence = {}
        for player_name, player_data in self.data.items():
            story = player_data.get(field, '').strip()
            if story and story.lower() not in ['no', 'n/a', 'none', '']:
                evidence[player_name] = story

        if not evidence:
            return None

        # Pick a random person's evidence
        correct_name = random.choice(list(evidence.keys()))
        story = evidence[correct_name]

        # Truncate if too long
        if len(story) > 100:
            story = story[:97] + "..."

        other_players = [p for p in self.players if p != correct_name]
        random.shuffle(other_players)

        return {
            'category': 'True Confessions',
            'question_type': 'personalized_story',
            'question_text': f"Who admitted: \"{story}\"?",
            'correct_answer': correct_name,
            'wrong_answers': other_players[:3],
            'context': f'From their {description} submission',
            'difficulty': 8
        }

    def generate_score_question(self) -> Optional[Dict]:
        """Generate questions based on 1-10 scores."""
        score_fields = [
            ('likelyToCry', 'most likely to cry at a party'),
            ('likelyToGhost', 'most likely to ghost someone'),
            ('likelyToDrunkTextEx', 'most likely to drunk text their ex'),
            ('likelyToForgetBirthday', 'most likely to forget your birthday'),
            ('likelyToGetKickedOut', 'most likely to get kicked out'),
            ('likelyToFallAsleepSex', 'most likely to fall asleep during sex'),
            ('likelyToCheatTrivia', 'most likely to cheat at trivia'),
            ('likelyToPretendSick', 'most likely to pretend to be sick')
        ]

        field, description = random.choice(score_fields)

        # Get scores for all players
        scores = {}
        for player_name in self.players:
            for player_data in self.data.values():
                # The person who filled out the form rated everyone
                score_str = player_data.get(field, '5')
                try:
                    # For simplicity, use Lauren's ratings (the submitter)
                    if player_data.get('playerName') == 'Lauren':
                        # This is a self-rating, need to infer from context
                        # Use the score as-is for now
                        scores[player_name] = int(score_str)
                except (ValueError, TypeError):
                    scores[player_name] = 5

        # Find highest scorer
        if not scores:
            return None

        correct_name = max(scores, key=scores.get)
        correct_score = scores[correct_name]

        other_players = [p for p in self.players if p != correct_name]
        random.shuffle(other_players)

        return {
            'category': 'Likelihood Rankings',
            'question_type': 'personalized_score',
            'question_text': f"Who scored HIGHEST (most likely) to {description}?",
            'correct_answer': correct_name,
            'wrong_answers': other_players[:3],
            'context': f'They scored {correct_score}/10',
            'difficulty': 6
        }

    def generate_would_you_rather(self) -> Optional[Dict]:
        """Generate Would You Rather questions from submissions."""
        for player_data in self.data.values():
            wyr = player_data.get('uncomfortableWouldYouRather', '').strip()
            if wyr and len(wyr) > 10:
                return {
                    'category': 'Would You Rather',
                    'question_type': 'personalized_wyr',
                    'question_text': wyr,
                    'correct_answer': 'Option A',
                    'wrong_answers': ['Option B', 'Neither', 'Both'],
                    'context': 'Submitted by the group',
                    'difficulty': 9
                }

        return None

    def generate_custom_trivia(self) -> Optional[Dict]:
        """Generate custom trivia from submissions."""
        for player_data in self.data.values():
            question = player_data.get('brutalTriviaQuestion', '').strip()
            correct = player_data.get('brutalTriviaCorrectAnswer', '').strip()
            wrong_str = player_data.get('brutalTriviaWrongAnswers', '').strip()

            if question and correct and wrong_str:
                # Parse wrong answers
                wrong_answers = [w.strip() for w in wrong_str.split(',')]

                return {
                    'category': 'Custom Trivia',
                    'question_type': 'personalized_trivia',
                    'question_text': question,
                    'correct_answer': correct,
                    'wrong_answers': wrong_answers,
                    'context': 'Group-submitted savage trivia',
                    'difficulty': 10
                }

        return None

    def generate_question(self) -> Optional[Dict]:
        """Generate a random personalized question."""
        if not self.data:
            return None

        generators = [
            self.generate_roast_question,
            self.generate_ranking_question,
            self.generate_evidence_question,
            self.generate_score_question,
            self.generate_custom_trivia,
            self.generate_would_you_rather
        ]

        # Try each generator in random order
        random.shuffle(generators)
        for generator in generators:
            try:
                question = generator()
                if question:
                    return question
            except Exception as e:
                print(f"Error in personalized generator: {e}")
                continue

        return None
