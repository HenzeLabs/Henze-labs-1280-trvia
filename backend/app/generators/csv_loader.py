"""
CSV Question Loader
Loads questions from CSV files to make it easy to add/edit questions without touching code.
"""

import csv
from pathlib import Path
from typing import List, Dict, Optional

class CSVQuestionLoader:
    """Loads questions from CSV files."""

    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        # Try project root if relative path doesn't work
        if not self.base_path.exists():
            self.base_path = Path(__file__).parent.parent.parent.parent

    def load_sex_trivia(self) -> List[Dict]:
        """Load sex trivia questions from CSV."""
        csv_path = self.base_path / "sex_trivia_questions.csv"
        questions = []

        if not csv_path.exists():
            print(f"⚠️  Sex trivia CSV not found at {csv_path}")
            return questions

        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    questions.append({
                        'question': row['question'].strip(),
                        'correct': row['correct_answer'].strip(),
                        'wrong': [
                            row['wrong_answer_1'].strip(),
                            row['wrong_answer_2'].strip(),
                            row['wrong_answer_3'].strip()
                        ],
                        'difficulty': int(row.get('difficulty', 3))
                    })

            print(f"✅ Loaded {len(questions)} sex trivia questions from CSV")
        except Exception as e:
            print(f"⚠️  Error loading sex trivia CSV: {e}")

        return questions

    def load_regular_trivia(self) -> List[Dict]:
        """Load regular trivia questions from CSV."""
        csv_path = self.base_path / "regular_trivia_questions.csv"
        questions = []

        if not csv_path.exists():
            print(f"⚠️  Regular trivia CSV not found at {csv_path}")
            return questions

        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    questions.append({
                        'question': row['question'].strip(),
                        'correct': row['correct_answer'].strip(),
                        'wrong': [
                            row['wrong_answer_1'].strip(),
                            row['wrong_answer_2'].strip(),
                            row['wrong_answer_3'].strip()
                        ],
                        'difficulty': int(row.get('difficulty', 3)),
                        'category': row.get('category', 'GENERAL KNOWLEDGE').strip()
                    })

            print(f"✅ Loaded {len(questions)} regular trivia questions from CSV")
        except Exception as e:
            print(f"⚠️  Error loading regular trivia CSV: {e}")

        return questions

    def load_poll_questions(self) -> List[str]:
        """Load poll questions from CSV."""
        csv_path = self.base_path / "poll_questions.csv"
        questions = []

        if not csv_path.exists():
            print(f"⚠️  Poll questions CSV not found at {csv_path}")
            return questions

        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    questions.append(row['question'].strip())

            print(f"✅ Loaded {len(questions)} poll questions from CSV")
        except Exception as e:
            print(f"⚠️  Error loading poll questions CSV: {e}")

        return questions

    def load_most_likely_scenarios(self) -> Dict:
        """Load 'most likely' scenarios from CSV, separated by type."""
        csv_path = self.base_path / "most_likely_questions.csv"
        scored_scenarios = []  # Specific callouts with predetermined answers
        poll_scenarios = []     # Generic scenarios for voting

        if not csv_path.exists():
            print(f"⚠️  Most likely CSV not found at {csv_path}")
            return {'scored': scored_scenarios, 'poll': poll_scenarios}

        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    scenario_raw = row.get('scenario', '')
                    if not scenario_raw:
                        continue  # Skip empty rows
                    scenario = scenario_raw.strip()

                    # Auto-detect: Check if scenario has specific name callouts
                    has_name_callout = (
                        '(Benny)' in scenario or
                        '(Gina)' in scenario or
                        '(Ian)' in scenario or
                        '(Lauren)' in scenario or
                        'Tom' in scenario  # Tom is always a specific reference
                    )

                    # Check for explicit question_type column if it exists
                    explicit_type_raw = row.get('question_type', '')
                    explicit_type = explicit_type_raw.strip().lower() if explicit_type_raw else ''

                    if explicit_type == 'scored' or (not explicit_type and has_name_callout):
                        scored_scenarios.append(scenario)
                    else:
                        poll_scenarios.append(scenario)

            print(f"✅ Loaded most likely scenarios: {len(scored_scenarios)} scored, {len(poll_scenarios)} poll")
        except Exception as e:
            print(f"⚠️  Error loading most likely CSV: {e}")

        return {'scored': scored_scenarios, 'poll': poll_scenarios}

    def load_all(self) -> Dict:
        """Load all question types from CSV files."""
        return {
            'sex_trivia': self.load_sex_trivia(),
            'regular_trivia': self.load_regular_trivia(),
            'poll_questions': self.load_poll_questions(),
            'most_likely_scenarios': self.load_most_likely_scenarios()
        }
