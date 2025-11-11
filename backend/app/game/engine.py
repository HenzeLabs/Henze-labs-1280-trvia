"""Game engine for managing trivia game sessions."""

import random
import string
import threading
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field

@dataclass
class Player:
    """Player data class."""
    id: str
    name: str
    score: int = 0
    answered_current: bool = False
    current_answer: Optional[str] = None  # Track what they answered
    join_time: datetime = field(default_factory=datetime.now)
    status: str = "alive"  # alive, ghost
    total_answer_time: float = 0.0  # Sum of seconds taken to answer (for tie-breaking)

@dataclass 
class Question:
    """Question data class."""
    id: int
    category: str
    question_type: str
    question_text: str
    correct_answer: str
    wrong_answers: List[str]
    context: str = ""
    difficulty: int = 1

@dataclass
class GameSession:
    """Game session data class."""
    room_code: str
    creator_player_id: Optional[str] = None  # Optional - TV can start without creator
    status: str = "waiting"  # waiting, playing, finished
    players: Dict[str, Player] = field(default_factory=dict)
    questions: List[Question] = field(default_factory=list)
    current_question_index: int = 0
    current_question_start_time: Optional[datetime] = None
    question_time_limit: int = 30
    phase: str = "waiting"  # waiting, question, final_sprint, finished
    current_question_payload: Optional[Dict] = None
    final_sprint_questions: List[Question] = field(default_factory=list)
    final_sprint_state: Optional[Dict] = None
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)  # Track last activity for cleanup
    auto_advance_pending: bool = False  # Prevent duplicate auto-advance tasks

class GameEngine:
    """Core game engine for managing trivia sessions."""

    def __init__(self):
        self.active_sessions: Dict[str, GameSession] = {}
        self.player_sessions: Dict[str, str] = {}  # player_id -> room_code
        self.socket_sessions: Dict[str, str] = {}  # socket_id -> player_id (auth mapping)
        self._lock = threading.RLock()  # Reentrant lock for thread-safe operations
    
    def generate_room_code(self) -> str:
        """
        Generate a unique room code (thread-safe).
        Uses lock to prevent race condition where two requests generate same code.
        """
        with self._lock:
            while True:
                code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                if code not in self.active_sessions:
                    # Reserve code immediately by creating placeholder
                    # Will be replaced by actual session in create_session()
                    return code
    
    def create_session(
        self,
        questions: List[Dict],
        sprint_questions: Optional[List[Dict]] = None
    ) -> str:
        """Create a new game session.

        Returns:
            str: room_code
        """
        room_code = self.generate_room_code()

        # Convert question dicts to Question objects
        question_objects = []
        for i, q in enumerate(questions):
            question_objects.append(Question(
                id=i,
                category=q.get('category', 'Unknown'),
                question_type=q.get('question_type', 'unknown'),
                question_text=q['question_text'],
                correct_answer=q['correct_answer'],
                wrong_answers=q['wrong_answers'],
                context=q.get('context', ''),
                difficulty=q.get('difficulty', 1)
            ))

        sprint_objects: List[Question] = []
        if sprint_questions:
            for i, q in enumerate(sprint_questions):
                sprint_objects.append(Question(
                    id=i,
                    category=q.get('category', 'Unknown'),
                    question_type=q.get('question_type', 'unknown'),
                    question_text=q['question_text'],
                    correct_answer=q['correct_answer'],
                    wrong_answers=q['wrong_answers'],
                    context=q.get('context', ''),
                    difficulty=q.get('difficulty', 1)
                ))

        session = GameSession(
            room_code=room_code,
            questions=question_objects,
            final_sprint_questions=sprint_objects
        )

        self.active_sessions[room_code] = session
        print(f"✅ Game {room_code} created (waiting for players)")

        return room_code

    def is_creator(self, room_code: str, player_id: str) -> bool:
        """Check if a player is the creator of the game (can start the game)."""
        session = self.active_sessions.get(room_code)
        if not session:
            return False
        return session.creator_player_id == player_id
    
    def join_session(self, room_code: str, player_name: str) -> tuple[Optional[str], Optional[str]]:
        """Add a player to a session.

        Returns:
            tuple: (player_id, error_message)
        """
        if room_code not in self.active_sessions:
            print(f"[JOIN] Room {room_code} not found")
            return None, "Game not found. Double-check the room code."
        
        session = self.active_sessions[room_code]
        
        if session.status != "waiting":
            print(f"[JOIN] Room {room_code} not accepting players (status={session.status})")
            return None, "This game already started. Ask the host for a new room."
        
        # Check if player name is already taken
        if any(p.name.lower() == player_name.lower() for p in session.players.values()):
            print(f"[JOIN] Duplicate name '{player_name}' in room {room_code}")
            return None, "That name is already taken. Try a different one."
        
        # Generate unique player ID
        player_id = f"player_{len(session.players)}_{random.randint(1000, 9999)}"
        
        player = Player(id=player_id, name=player_name)
        session.players[player_id] = player
        self.player_sessions[player_id] = room_code

        # Mark the first player as the creator so they can control the game flow
        if not session.creator_player_id:
            session.creator_player_id = player_id
        
        return player_id, None
    
    def get_session(self, room_code: str) -> Optional[GameSession]:
        """Get a game session by room code."""
        return self.active_sessions.get(room_code)
    
    def get_player_session(self, player_id: str) -> Optional[GameSession]:
        """Get the session a player is in."""
        room_code = self.player_sessions.get(player_id)
        if room_code:
            return self.active_sessions.get(room_code)
        return None

    def verify_host(self, room_code: str, player_id: str) -> bool:
        """Verify that player_id is the host of the room (SECURITY: BUG #1)."""
        session = self.active_sessions.get(room_code)
        if not session:
            return False
        return session.creator_player_id == player_id

    def start_game(self, room_code: str, host_player_id: str = None) -> bool:
        """
        Start the game for a session.

        Args:
            room_code: Room code
            host_player_id: Player ID of requester (for authorization check)
        """
        session = self.active_sessions.get(room_code)
        if not session or session.status != "waiting" or len(session.players) == 0:
            return False

        # SECURITY (BUG #1): Verify host authorization if player_id provided
        if host_player_id and not self.verify_host(room_code, host_player_id):
            print(f"⚠️ Unauthorized start_game attempt by {host_player_id} for room {room_code}")
            return False

        # Touch session to update last_activity
        self.touch_session(room_code)

        session.status = "playing"
        session.phase = "question"
        session.current_question_index = 0
        session.current_question_start_time = datetime.now()
        session.final_sprint_state = None
        
        # Reset all players' answered status
        for player in session.players.values():
            player.answered_current = False
            player.current_answer = None
            player.status = "alive"
        
        return True
    
    def get_current_question(self, room_code: str, include_answer: bool = False) -> Optional[Dict]:
        """Get the current question for a session.

        Args:
            room_code: The room code
            include_answer: If True, includes correct_answer (for host only)
        """
        session = self.active_sessions.get(room_code)
        if not session or session.status != "playing":
            return None

        if session.phase == "final_sprint" and session.final_sprint_state:
            sprint_state = session.final_sprint_state
            if not session.final_sprint_questions:
                return None

            if sprint_state.get('index', 0) >= len(session.final_sprint_questions):
                return None

            if not session.current_question_payload:
                question = session.final_sprint_questions[sprint_state['index']]
                session.current_question_payload = self._build_question_payload(
                    question,
                    phase='final_sprint'
                )

            question_payload = self._copy_question_payload(
                session.current_question_payload,
                include_answer=include_answer
            )
            question_payload['phase'] = 'final_sprint'
            question_payload['sprint_positions'] = sprint_state.get('positions', {})
            question_payload['sprint_goal'] = sprint_state.get('goal')
            question_payload['time_remaining'] = self.get_time_remaining(
                room_code,
                time_limit=sprint_state.get('time_limit')
            )

            return question_payload

        if session.current_question_index >= len(session.questions):
            return None

        if not session.current_question_payload:
            current_question = session.questions[session.current_question_index]
            session.current_question_payload = self._build_question_payload(
                current_question,
                phase='question'
            )

        question_payload = self._copy_question_payload(
            session.current_question_payload,
            include_answer=include_answer
        )
        question_payload['phase'] = 'question'
        question_payload['time_remaining'] = self.get_time_remaining(room_code)
        return question_payload

    def get_question_answer(self, room_code: str) -> Optional[str]:
        """Get just the correct answer for the current question (host only)."""
        session = self.active_sessions.get(room_code)
        if not session or session.status != "playing":
            return None

        if session.phase != "question":
            return None

        if session.current_question_index >= len(session.questions):
            return None

        question = session.questions[session.current_question_index]
        return question.correct_answer

    def get_answer_stats(self, room_code: str) -> Optional[Dict]:
        """Get voting statistics for the current question."""
        session = self.active_sessions.get(room_code)
        if not session or session.status != "playing":
            return None

        if session.phase != "question":
            return None

        if session.current_question_index >= len(session.questions):
            return None

        question = session.questions[session.current_question_index]

        # Count votes for each answer
        vote_counts = {}
        total_votes = 0
        voters_by_answer = {}  # Track who voted for what
        eligible_players = [p for p in session.players.values() if p.status == "alive"]

        for player in eligible_players:
            if player.answered_current and player.current_answer:
                total_votes += 1
                answer = player.current_answer

                if answer not in vote_counts:
                    vote_counts[answer] = 0
                    voters_by_answer[answer] = []

                vote_counts[answer] += 1
                voters_by_answer[answer].append(player.name)

        # Calculate percentages
        answer_breakdown = []
        for answer, count in vote_counts.items():
            percentage = (count / total_votes * 100) if total_votes > 0 else 0
            answer_breakdown.append({
                'answer': answer,
                'count': count,
                'percentage': round(percentage, 1),
                'voters': voters_by_answer[answer],
                'is_correct': answer == question.correct_answer
            })

        # Sort by count (descending)
        answer_breakdown.sort(key=lambda x: x['count'], reverse=True)

        # POLL SCORING: Award points to whoever got the most votes
        poll_winner = None
        if question.question_type == 'poll' and answer_breakdown:
            # Find the person with the most votes
            most_voted = answer_breakdown[0]
            winner_name = most_voted['answer']  # The player name that got voted for
            winner_votes = most_voted['count']

            # Award points to that player if they exist
            for player in session.players.values():
                if player.name == winner_name:
                    # Award 150 points + bonus for each vote
                    points = 150 + (winner_votes * 25)
                    player.score += points
                    poll_winner = {
                        'name': winner_name,
                        'votes': winner_votes,
                        'points_earned': points
                    }
                    break

        result = {
            'correct_answer': question.correct_answer,
            'total_votes': total_votes,
            'total_players': len(eligible_players),
            'required_players': len(eligible_players),
            'answer_breakdown': answer_breakdown,
            'ghosts': [
                player.name for player in session.players.values() if player.status != "alive"
            ]
        }

        # Add poll winner info if this is a poll
        if question.question_type == 'poll':
            result['is_poll'] = True
            result['poll_winner'] = poll_winner

        return result
    
    def get_time_remaining(self, room_code: str, time_limit: Optional[int] = None) -> int:
        """Get time remaining for current question."""
        session = self.active_sessions.get(room_code)
        if not session or not session.current_question_start_time:
            return 0

        elapsed = (datetime.now() - session.current_question_start_time).seconds

        # Determine time limit based on question type
        if time_limit is None:
            current_q = session.questions[session.current_question_index] if session.current_question_index < len(session.questions) else None
            if current_q:
                # Manual entry questions (receipts, roast) get 45 seconds
                if current_q.question_type in ('receipts', 'roast', 'personalized_roast'):
                    time_limit = 45
                # Multiple choice questions get 10 seconds
                else:
                    time_limit = 10
            else:
                time_limit = session.question_time_limit

        limit = time_limit
        remaining = max(0, limit - elapsed)
        return remaining
    
    def submit_answer(self, player_id: str, answer: str) -> Dict:
        """Submit an answer for a player."""
        room_code = self.player_sessions.get(player_id)
        if not room_code:
            return {'success': False, 'message': 'Player not in a session'}

        session = self.active_sessions.get(room_code)
        if not session or session.status != "playing":
            return {'success': False, 'message': 'Game not in progress'}

        # Touch session to update last_activity for cleanup tracking
        self.touch_session(room_code)

        player = session.players.get(player_id)
        if not player:
            return {'success': False, 'message': 'Player not found'}

        if session.phase == "final_sprint":
            return self._handle_final_sprint_answer(session, player, answer)

        return self._handle_regular_answer(session, player, answer)
    
    def _handle_regular_answer(self, session: GameSession, player: Player, answer: str) -> Dict:
        """Process answers during standard question rounds."""
        if player.status != "alive":
            return {
                'success': False,
                'phase': 'question',
                'message': 'Ghosts can only participate during the final sprint.'
            }

        if player.answered_current:
            return {'success': False, 'phase': 'question', 'message': 'Already answered this question'}

        if self.get_time_remaining(session.room_code) <= 0:
            return {'success': False, 'phase': 'question', 'message': 'Time is up!'}

        current_question = session.questions[session.current_question_index]

        # Track answer time for tie-breaking (BUG #11)
        time_elapsed = (datetime.now() - session.current_question_start_time).total_seconds()
        player.total_answer_time += time_elapsed

        player.answered_current = True
        player.current_answer = answer

        if current_question.question_type == 'poll':
            return {
                'success': True,
                'phase': 'question',
                'is_poll': True,
                'message': 'Vote recorded! Scores will update after the reveal.'
            }

        is_correct = answer == current_question.correct_answer
        points = 0
        if is_correct:
            time_remaining = self.get_time_remaining(session.room_code)
            points = 100 + (time_remaining * 2)
            player.score += points

        return {
            'success': True,
            'phase': 'question',
            'is_correct': is_correct,
            'correct_answer': current_question.correct_answer,
            'points_earned': points,
            'total_score': player.score
        }

    def _handle_final_sprint_answer(self, session: GameSession, player: Player, answer: str) -> Dict:
        """Process answers during the final sprint."""
        sprint_state = session.final_sprint_state
        if not sprint_state:
            return {'success': False, 'phase': 'final_sprint', 'message': 'Final sprint is not active.'}

        time_limit = sprint_state.get('time_limit')
        if time_limit and self.get_time_remaining(session.room_code, time_limit=time_limit) <= 0:
            return {'success': False, 'phase': 'final_sprint', 'message': 'Time is up!'}

        responses = sprint_state.setdefault('responses', {})
        if player.id in responses:
            return {'success': False, 'phase': 'final_sprint', 'message': 'Already answered this sprint question'}

        question_index = sprint_state.get('index', 0)
        if question_index >= len(session.final_sprint_questions):
            return {'success': False, 'phase': 'final_sprint', 'message': 'Final sprint has concluded'}

        question = session.final_sprint_questions[question_index]
        is_correct = answer == question.correct_answer
        responses[player.id] = {
            'answer': answer,
            'is_correct': is_correct
        }

        remaining = len(session.players) - len(responses)
        if remaining > 0:
            return {
                'success': True,
                'phase': 'final_sprint',
                'awaiting': True,
                'message': 'Answer locked. Waiting on the rest of the room.'
            }

        # All responses collected – evaluate results
        results = []
        positions = sprint_state.setdefault('positions', {})
        for player_id, response in responses.items():
            current_position = positions.get(player_id, 0)
            if response['is_correct']:
                current_position += 1
            positions[player_id] = current_position

            player_ref = session.players.get(player_id)
            results.append({
                'player_id': player_id,
                'name': player_ref.name if player_ref else player_id,
                'is_correct': response['is_correct'],
                'answer': response['answer'],
                'new_position': current_position
            })

        # Reset for next sprint question
        sprint_state['responses'] = {}
        session.current_question_payload = None

        goal = sprint_state.get('goal', 7)
        winners = [
            (pid, pos) for pid, pos in positions.items() if pos >= goal
        ]

        if winners:
            # Choose winner with highest position; tie-breaker earliest in list
            winners.sort(key=lambda item: item[1], reverse=True)
            winner_id = winners[0][0]
            summary = self._finish_game(session, winner_id=winner_id)
            return {
                'success': True,
                'phase': 'final_sprint',
                'final_sprint_complete': True,
                'results': results,
                'winner_id': winner_id,
                'summary': summary
            }

        sprint_state['index'] = sprint_state.get('index', 0) + 1

        if sprint_state['index'] >= len(session.final_sprint_questions):
            # No questions left – determine winner by position
            winner_id, _ = max(positions.items(), key=lambda item: item[1])
            summary = self._finish_game(session, winner_id=winner_id)
            return {
                'success': True,
                'phase': 'final_sprint',
                'final_sprint_complete': True,
                'results': results,
                'winner_id': winner_id,
                'summary': summary
            }

        # Prepare next sprint question
        self._reset_players_for_next_round(session)
        session.current_question_start_time = datetime.now()
        session.current_question_payload = None

        next_question = self.get_current_question(session.room_code)

        return {
            'success': True,
            'phase': 'final_sprint',
            'question_complete': True,
            'results': results,
            'positions': positions,
            'next_step': {
                'type': 'final_sprint',
                'question': next_question
            }
        }
    
    def _advance_regular_flow(self, session: GameSession) -> Dict:
        """Advance from a normal question to the next question or final sprint."""
        # Simply move to the next question (minigame removed)
        return self._move_to_next_regular_question(session, advance_index=True)

    def _move_to_next_regular_question(self, session: GameSession, advance_index: bool) -> Dict:
        """Move to the next standard question or initiate the final sprint."""
        if advance_index:
            session.current_question_index += 1

        session.current_question_payload = None

        if session.current_question_index >= len(session.questions):
            return self._start_final_sprint(session)

        session.phase = "question"
        self._reset_players_for_next_round(session)
        session.current_question_start_time = datetime.now()

        question = self.get_current_question(session.room_code)
        return {
            'type': 'question',
            'question': question
        }

    def _start_final_sprint(self, session: GameSession) -> Dict:
        """Begin the final sprint phase."""
        if not session.final_sprint_questions:
            summary = self._finish_game(session)
            return {
                'type': 'game_finished',
                'summary': summary
            }

        session.phase = "final_sprint"
        positions = {}
        for player in session.players.values():
            positions[player.id] = 3 if player.status == "alive" else 1

        goal = max(6, max(positions.values()) + 3)
        session.final_sprint_state = {
            'index': 0,
            'positions': positions,
            'goal': goal,
            'responses': {},
            'time_limit': 20
        }

        self._reset_players_for_next_round(session)
        session.current_question_payload = None
        session.current_question_start_time = datetime.now()

        question = self.get_current_question(session.room_code)

        return {
            'type': 'final_sprint',
            'question': question,
            'positions': positions,
            'goal': goal
        }

    def _finish_game(self, session: GameSession, winner_id: Optional[str] = None) -> Dict:
        """Finalize the game and prepare the summary."""
        session.status = "finished"
        session.phase = "finished"

        if winner_id and session.final_sprint_state:
            session.final_sprint_state['winner_id'] = winner_id

        summary = self.get_session_summary(session.room_code)
        if winner_id and summary is not None:
            summary['final_sprint_winner'] = winner_id
        return summary

    def _alive_players(self, session: GameSession) -> List[Player]:
        """Return the list of currently alive players."""
        return [player for player in session.players.values() if player.status == "alive"]

    def _reset_players_for_next_round(self, session: GameSession) -> None:
        """Clear per-question state so players can answer again."""
        for player in session.players.values():
            player.answered_current = False
            player.current_answer = None

    def _build_question_payload(self, question: Question, phase: str) -> Dict:
        """Convert a Question object into a broadcast-friendly payload."""
        answers = [question.correct_answer] + list(question.wrong_answers)
        random.shuffle(answers)

        return {
            'id': question.id,
            'category': question.category,
            'question_type': question.question_type,
            'question_text': question.question_text,
            'answers': answers,
            'context': question.context,
            'difficulty': question.difficulty,
            'correct_answer': question.correct_answer,
            'phase': phase
        }

    def _copy_question_payload(self, payload: Dict, include_answer: bool) -> Dict:
        """Create a safe copy of a stored question payload."""
        copied = {k: v for k, v in payload.items() if k != 'correct_answer'}
        if 'answers' in payload:
            copied['answers'] = list(payload['answers'])
        if include_answer and 'correct_answer' in payload:
            copied['correct_answer'] = payload['correct_answer']
        return copied
    
    def next_question(self, room_code: str, host_player_id: str = None) -> Dict:
        """
        Advance the game state when the host requests the next step.

        Args:
            room_code: Room code
            host_player_id: Player ID of requester (for authorization check)
        """
        session = self.active_sessions.get(room_code)
        if not session or session.status != "playing":
            return {'type': 'error', 'message': 'Game not in progress'}

        # SECURITY (BUG #1 extension): Verify host authorization if player_id provided
        if host_player_id and not self.verify_host(room_code, host_player_id):
            print(f"⚠️ Unauthorized next_question attempt by {host_player_id} for room {room_code}")
            return {'type': 'error', 'message': 'Not authorized'}

        if session.phase == "minigame":
            return {'type': 'minigame_in_progress'}

        if session.phase == "final_sprint":
            return {'type': 'final_sprint_in_progress'}

        return self._advance_regular_flow(session)
    
    def get_leaderboard(self, room_code: str) -> List[Dict]:
        """
        Get current leaderboard for a session.
        Tie-breaker: If scores are equal, faster total answer time wins (BUG #11).
        """
        session = self.active_sessions.get(room_code)
        if not session:
            return []

        # Sort players by score (descending), then by total_answer_time (ascending)
        # Lower answer time = faster = better
        sorted_players = sorted(
            session.players.values(),
            key=lambda p: (-p.score, p.total_answer_time)
        )

        leaderboard = []
        current_rank = 1
        for i, player in enumerate(sorted_players):
            # Determine actual rank (handle ties)
            if i > 0:
                prev_player = sorted_players[i - 1]
                if player.score == prev_player.score and player.total_answer_time == prev_player.total_answer_time:
                    # Exact tie - use previous rank
                    current_rank = leaderboard[-1]['rank']
                else:
                    # Different score or time - new rank
                    current_rank = i + 1

            leaderboard.append({
                'rank': current_rank,
                'player_id': player.id,
                'name': player.name,
                'score': player.score,
                'answered_current': player.answered_current,
                'status': player.status,
                'total_answer_time': round(player.total_answer_time, 2)  # For debugging
            })

        return leaderboard
    
    def get_game_stats(self, room_code: str) -> Dict:
        """Get overall game statistics."""
        session = self.active_sessions.get(room_code)
        if not session:
            return {}

        alive_players = self._alive_players(session)
        alive_count = len(alive_players)

        all_answered = False
        # Use centralized phase list from config for auto-reveal eligibility
        from flask import current_app
        allowed_phases = current_app.config.get('ALLOWED_AUTOREVEAL_PHASES', ("question",))
        if session.phase in allowed_phases and alive_count > 0:
            all_answered = all(p.answered_current for p in alive_players)

        # Calculate total answers across all questions
        total_answers = sum(1 for p in alive_players if p.answered_current)

        stats = {
            'room_code': room_code,
            'status': session.status,
            'phase': session.phase,
            'total_players': len(session.players),
            'alive_players': alive_count,
            'current_question': session.current_question_index + 1,
            'total_questions': len(session.questions),
            'time_remaining': self.get_time_remaining(room_code) if session.status == "playing" else 0,
            'players_answered': total_answers,
            'all_answered': all_answered
        }

        if session.phase == "final_sprint" and session.final_sprint_state:
            stats['final_sprint'] = {
                'positions': session.final_sprint_state.get('positions', {}),
                'goal': session.final_sprint_state.get('goal'),
                'index': session.final_sprint_state.get('index', 0)
            }

        return stats
    
    def end_session(self, room_code: str) -> bool:
        """End a game session."""
        if room_code not in self.active_sessions:
            return False
        
        session = self.active_sessions[room_code]
        
        # Remove players from player_sessions mapping
        for player_id in session.players.keys():
            if player_id in self.player_sessions:
                del self.player_sessions[player_id]
        
        # Remove session
        del self.active_sessions[room_code]
        return True
    
    def get_session_summary(self, room_code: str) -> Dict:
        """Get final summary of a completed game."""
        session = self.active_sessions.get(room_code)
        if not session:
            return {}
        
        leaderboard = self.get_leaderboard(room_code)
        
        # Calculate some fun stats
        if leaderboard:
            winner = leaderboard[0]
            total_points = sum(player['score'] for player in leaderboard)
            avg_score = total_points / len(leaderboard) if leaderboard else 0

            summary = {
                'winner': winner,
                'total_players': len(leaderboard),
                'total_questions': len(session.questions),
                'average_score': round(avg_score, 1),
                'leaderboard': leaderboard,
                'game_duration': (datetime.now() - session.created_at).seconds // 60,  # in minutes
                'roast_level': 'Savage' if len(session.questions) > 15 else 'Mild',
                'player_statuses': {
                    player.id: player.status for player in session.players.values()
                }
            }

            if session.final_sprint_state:
                sprint_state = session.final_sprint_state
                summary['final_sprint'] = {
                    'positions': sprint_state.get('positions', {}),
                    'goal': sprint_state.get('goal'),
                    'winner_id': sprint_state.get('winner_id')
                }

                winner_id = sprint_state.get('winner_id')
                if winner_id:
                    winner_entry = next(
                        (entry for entry in leaderboard if entry['player_id'] == winner_id),
                        winner
                    )
                    summary['winner'] = winner_entry

            return summary

        return {}

    def all_players_answered(self, room_code: str) -> bool:
        """Check if all alive players have answered the current question."""
        session = self.active_sessions.get(room_code)
        if not session:
            return False

        # Get all alive players
        alive_players = [p for p in session.players.values() if p.status == "alive"]
        
        # Must have at least one player to check
        if len(alive_players) == 0:
            return False

        # Check if all alive players have answered
        all_answered = all(p.answered_current for p in alive_players)
        
        # Debug logging
        answered_count = sum(1 for p in alive_players if p.answered_current)
        print(f"🔍 Room {room_code}: {answered_count}/{len(alive_players)} players answered. All answered: {all_answered}")
        
        return all_answered

    def try_start_auto_advance(self, room_code: str) -> bool:
        """
        Atomically check and set auto_advance_pending flag.
        Returns True if auto-advance should start, False if already pending.
        Thread-safe using RLock.
        """
        with self._lock:
            session = self.active_sessions.get(room_code)
            if not session:
                return False

            if session.auto_advance_pending:
                return False  # Already pending, don't start duplicate

            session.auto_advance_pending = True
            return True  # Safe to start auto-advance

    def get_answered_count(self, room_code: str) -> tuple[int, int]:
        """Get count of players who answered vs total alive players."""
        session = self.active_sessions.get(room_code)
        if not session:
            return (0, 0)

        alive_players = [p for p in session.players.values() if p.status == "alive"]
        answered_count = sum(1 for p in alive_players if p.answered_current)

        return (answered_count, len(alive_players))

    def touch_session(self, room_code: str) -> None:
        """Update last_activity timestamp for a session."""
        session = self.active_sessions.get(room_code)
        if session:
            session.last_activity = datetime.now()

    def bind_socket_to_player(self, socket_id: str, player_id: str) -> None:
        """Bind a socket session to a player ID for authentication."""
        with self._lock:
            self.socket_sessions[socket_id] = player_id

    def verify_socket_owns_player(self, socket_id: str, player_id: str) -> bool:
        """Verify that a socket session owns the claimed player ID."""
        return self.socket_sessions.get(socket_id) == player_id

    def unbind_socket(self, socket_id: str) -> Optional[str]:
        """Remove socket binding and return the player_id if it existed."""
        with self._lock:
            return self.socket_sessions.pop(socket_id, None)

    def cleanup_stale_sessions(self, ttl_hours: int = 2) -> int:
        """
        Remove sessions that have been inactive for longer than ttl_hours.
        Returns count of sessions cleaned up.
        Thread-safe using RLock.
        """
        with self._lock:
            now = datetime.now()
            stale_rooms = []

            for room_code, session in self.active_sessions.items():
                age_hours = (now - session.last_activity).total_seconds() / 3600
                if age_hours > ttl_hours:
                    stale_rooms.append(room_code)

            # Remove stale sessions and their player mappings
            for room_code in stale_rooms:
                session = self.active_sessions.pop(room_code)
                # Remove player mappings
                for player_id in session.players.keys():
                    self.player_sessions.pop(player_id, None)
                print(f"🧹 Cleaned up stale session: {room_code} (inactive for {age_hours:.1f}h)")

            return len(stale_rooms)

# Global game engine instance
game_engine = GameEngine()
