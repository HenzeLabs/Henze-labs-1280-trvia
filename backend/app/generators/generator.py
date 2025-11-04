"""Question generators for 1280 Trivia.

This module provides simple, modular generators that convert parsed chat
messages into multiple-choice questions. Generators are intentionally
conservative (no cruel or doxxing content) but include roast-style and
"who said this" types as requested. They write questions into the
`Question` model provided by `app.models`.
"""
from random import sample, choice, shuffle
from typing import List, Tuple
from ..models import Question, Message, Database

class QuestionGenerator:
    """Generate questions from messages and other sources.

    Contract:
    - inputs: Database instance (sqlite) or model wrappers
    - outputs: question dicts or inserted DB rows
    - error modes: raises on DB errors
    """

    def __init__(self, db: Database):
        self.db = db
        self.message_model = Message(db)
        self.question_model = Question(db)

    def _make_mcq(self, correct: str, wrongs: List[str]) -> Tuple[str, List[str]]:
        """Return question_text and shuffled options with correct answer included."""
        options = [correct] + (wrongs[:3] if len(wrongs) >= 3 else wrongs)
        shuffle(options)
        return options

    def generate_receipt_question(self, chat_name: str) -> dict:
        """Generate a "Who said this?" question from a random message in a chat.

        Returns the DB row (as dict) of the created question.
        """
        messages = self.message_model.get_messages_by_chat(chat_name, limit=500)
        if not messages:
            raise ValueError("No messages available for chat: %s" % chat_name)

        msg = choice(messages)
        snippet = (msg['message_text'][:200] + '...') if len(msg['message_text']) > 200 else msg['message_text']

        # Select wrong answers (other senders)
        other_msgs = [m for m in messages if m['sender'] != msg['sender']]
        wrong_senders = list({m['sender'] for m in sample(other_msgs, min(len(other_msgs), 10))}) if other_msgs else []
        # Ensure we have at least 3 wrong options (use placeholders if needed)
        while len(wrong_senders) < 3:
            wrong_senders.append("Someone else")

        options = [msg['sender']] + wrong_senders[:3]
        shuffle(options)

        q_text = f"Who said: \"{snippet}\""
        q_id = self.question_model.add_question(
            category='Receipts',
            question_type='who_said_this',
            question_text=q_text,
            correct_answer=msg['sender'],
            wrong_answers=options,
            context=f"chat:{chat_name}",
            source_message_id=None
        )
        return self.question_model.get_question_by_id(q_id)

    def generate_roast_question(self, chat_name: str) -> dict:
        """Generate a roast-style question about an embarrassing moment.

        The generator finds messages matching 'embarrassing' heuristics and
        crafts a mild roast question that doesn't reveal private details.
        """
        # Use the parser heuristics already stored in messages
        messages = self.message_model.get_messages_by_chat(chat_name, limit=2000)
        candidates = [m for m in messages if any(k in m['message_text'].lower() for k in ['drunk','hangover','embarrass','cringe','naked','bathroom','vomit','oops','fail','hookup'])]
        if not candidates:
            # fallback to random funny message
            candidates = messages
        if not candidates:
            raise ValueError("No candidate messages for roast generation")

        msg = choice(candidates)
        sender = msg['sender']

        # Choose other players for wrong options
        all_senders = list({m['sender'] for m in messages})
        wrongs = [s for s in all_senders if s != sender]
        while len(wrongs) < 3:
            wrongs.append("A roommate")
        wrongs = wrongs[:3]

        q_text = f"Who most recently had an embarrassing moment like: '{msg['message_text'][:80]}...' ?"
        q_id = self.question_model.add_question(
            category='Red Flags',
            question_type='roast',
            question_text=q_text,
            correct_answer=sender,
            wrong_answers=wrongs,
            context=f"chat:{chat_name}",
            source_message_id=None
        )
        return self.question_model.get_question_by_id(q_id)

    def generate_most_likely_question(self, chat_name: str) -> dict:
        """Generate a 'Who's most likely to...' question based on simple heuristics.

        Heuristics are intentionally light: frequency of keywords per sender.
        """
        messages = self.message_model.get_messages_by_chat(chat_name, limit=2000)
        if not messages:
            raise ValueError("No messages for chat")

        # Simple scoring: count naughty keywords per sender
        keywords = ['drunk','late','flirt','hookup','complain','curse','party','nap']
        scores = {}
        for m in messages:
            text = m['message_text'].lower()
            sender = m['sender']
            scores.setdefault(sender, 0)
            for k in keywords:
                if k in text:
                    scores[sender] += 1

        if not scores:
            raise ValueError("No scoring data available")

        # Pick winner and wrong options
        sorted_senders = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        winner = sorted_senders[0][0]
        other_senders = [s for s, sc in sorted_senders[1:]]
        while len(other_senders) < 3:
            other_senders.append("Someone else")
        options = [winner] + other_senders[:3]
        shuffle(options)

        q_text = f"Who's most likely to {choice(['end up drunk','start a fight','text an ex at 3am','crash a party','sleep through brunch'])}?"
        q_id = self.question_model.add_question(
            category='Degenerate of the Week',
            question_type='most_likely',
            question_text=q_text,
            correct_answer=winner,
            wrong_answers=options,
            context=f"chat:{chat_name}",
            source_message_id=None
        )
        return self.question_model.get_question_by_id(q_id)

    def generate_random_trivia(self) -> dict:
        """Create a filler trivia question (non-chat) for variety.

        This is a tiny in-memory generator; you can replace it with an API
        or larger dataset later.
        """
        sample_trivia = [
            ("What year did the first iPhone launch?", "2007", ["2005","2006","2008"]),
            ("Which planet is known as the Red Planet?", "Mars", ["Venus","Jupiter","Saturn"]),
            ("What is the capital of France?", "Paris", ["Lyon","Marseille","Nice"]),
        ]
        q_text, correct, wrongs = choice(sample_trivia)
        q_id = self.question_model.add_question(
            category='Random Trivia',
            question_type='general',
            question_text=q_text,
            correct_answer=correct,
            wrong_answers=wrongs,
            context='general',
            source_message_id=None
        )
        return self.question_model.get_question_by_id(q_id)
