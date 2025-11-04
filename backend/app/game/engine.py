"""Game engine for managing trivia game sessions."""

import random
import string
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
    join_time: datetime = field(default_factory=datetime.now)

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
    host_name: str
    status: str = "waiting"  # waiting, playing, finished
    players: Dict[str, Player] = field(default_factory=dict)
    questions: List[Question] = field(default_factory=list)
    current_question_index: int = 0
    current_question_start_time: Optional[datetime] = None
    question_time_limit: int = 30
    created_at: datetime = field(default_factory=datetime.now)

class GameEngine:
    """Core game engine for managing trivia sessions."""
    
    def __init__(self):
        self.active_sessions: Dict[str, GameSession] = {}
        self.player_sessions: Dict[str, str] = {}  # player_id -> room_code
    
    def generate_room_code(self) -> str:
        """Generate a unique room code."""
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            if code not in self.active_sessions:
                return code
    
    def create_session(self, host_name: str, questions: List[Dict]) -> str:
        """Create a new game session."""
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
        
        session = GameSession(
            room_code=room_code,
            host_name=host_name,
            questions=question_objects
        )
        
        self.active_sessions[room_code] = session
        return room_code
    
    def join_session(self, room_code: str, player_name: str) -> Optional[str]:
        """Add a player to a session."""
        if room_code not in self.active_sessions:
            return None
        
        session = self.active_sessions[room_code]
        
        if session.status != "waiting":
            return None  # Can't join a game in progress
        
        # Check if player name is already taken
        if any(p.name.lower() == player_name.lower() for p in session.players.values()):
            return None
        
        # Generate unique player ID
        player_id = f"player_{len(session.players)}_{random.randint(1000, 9999)}"
        
        player = Player(id=player_id, name=player_name)
        session.players[player_id] = player
        self.player_sessions[player_id] = room_code
        
        return player_id
    
    def get_session(self, room_code: str) -> Optional[GameSession]:
        """Get a game session by room code."""
        return self.active_sessions.get(room_code)
    
    def get_player_session(self, player_id: str) -> Optional[GameSession]:
        """Get the session a player is in."""
        room_code = self.player_sessions.get(player_id)
        if room_code:
            return self.active_sessions.get(room_code)
        return None
    
    def start_game(self, room_code: str) -> bool:
        """Start the game for a session."""
        session = self.active_sessions.get(room_code)
        if not session or session.status != "waiting" or len(session.players) == 0:
            return False
        
        session.status = "playing"
        session.current_question_index = 0
        session.current_question_start_time = datetime.now()
        
        # Reset all players' answered status
        for player in session.players.values():
            player.answered_current = False
        
        return True
    
    def get_current_question(self, room_code: str) -> Optional[Dict]:
        """Get the current question for a session."""
        session = self.active_sessions.get(room_code)
        if not session or session.status != "playing":
            return None
        
        if session.current_question_index >= len(session.questions):
            return None
        
        question = session.questions[session.current_question_index]
        
        # Shuffle answer choices
        all_answers = [question.correct_answer] + question.wrong_answers
        random.shuffle(all_answers)
        
        return {
            'id': question.id,
            'category': question.category,
            'question_type': question.question_type,
            'question_text': question.question_text,
            'answers': all_answers,
            'context': question.context,
            'difficulty': question.difficulty,
            'time_remaining': self.get_time_remaining(room_code)
        }
    
    def get_time_remaining(self, room_code: str) -> int:
        """Get time remaining for current question."""
        session = self.active_sessions.get(room_code)
        if not session or not session.current_question_start_time:
            return 0
        
        elapsed = (datetime.now() - session.current_question_start_time).seconds
        remaining = max(0, session.question_time_limit - elapsed)
        return remaining
    
    def submit_answer(self, player_id: str, answer: str) -> Dict:
        """Submit an answer for a player."""
        room_code = self.player_sessions.get(player_id)
        if not room_code:
            return {'success': False, 'message': 'Player not in a session'}
        
        session = self.active_sessions.get(room_code)
        if not session or session.status != "playing":
            return {'success': False, 'message': 'Game not in progress'}
        
        player = session.players.get(player_id)
        if not player:
            return {'success': False, 'message': 'Player not found'}
        
        if player.answered_current:
            return {'success': False, 'message': 'Already answered this question'}
        
        # Check if time is up
        if self.get_time_remaining(room_code) <= 0:
            return {'success': False, 'message': 'Time is up!'}
        
        # Get current question
        current_question = session.questions[session.current_question_index]
        is_correct = answer == current_question.correct_answer
        
        # Calculate points based on speed and correctness
        points = 0
        if is_correct:
            time_remaining = self.get_time_remaining(room_code)
            # Base points + speed bonus
            points = 100 + (time_remaining * 2)
            player.score += points
        
        player.answered_current = True
        
        return {
            'success': True,
            'is_correct': is_correct,
            'correct_answer': current_question.correct_answer,
            'points_earned': points,
            'total_score': player.score
        }
    
    def next_question(self, room_code: str) -> bool:
        """Move to the next question."""
        session = self.active_sessions.get(room_code)
        if not session or session.status != "playing":
            return False
        
        session.current_question_index += 1
        
        # Check if game is finished
        if session.current_question_index >= len(session.questions):
            session.status = "finished"
            return False
        
        # Reset for next question
        session.current_question_start_time = datetime.now()
        for player in session.players.values():
            player.answered_current = False
        
        return True
    
    def get_leaderboard(self, room_code: str) -> List[Dict]:
        """Get current leaderboard for a session."""
        session = self.active_sessions.get(room_code)
        if not session:
            return []
        
        # Sort players by score (descending)
        sorted_players = sorted(session.players.values(), key=lambda p: p.score, reverse=True)
        
        leaderboard = []
        for i, player in enumerate(sorted_players):
            leaderboard.append({
                'rank': i + 1,
                'name': player.name,
                'score': player.score,
                'answered_current': player.answered_current
            })
        
        return leaderboard
    
    def get_game_stats(self, room_code: str) -> Dict:
        """Get overall game statistics."""
        session = self.active_sessions.get(room_code)
        if not session:
            return {}
        
        return {
            'room_code': room_code,
            'host_name': session.host_name,
            'status': session.status,
            'total_players': len(session.players),
            'current_question': session.current_question_index + 1,
            'total_questions': len(session.questions),
            'time_remaining': self.get_time_remaining(room_code) if session.status == "playing" else 0,
            'players_answered': sum(1 for p in session.players.values() if p.answered_current)
        }
    
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
            
            return {
                'winner': winner,
                'total_players': len(leaderboard),
                'total_questions': len(session.questions),
                'average_score': round(avg_score, 1),
                'leaderboard': leaderboard,
                'game_duration': (datetime.now() - session.created_at).seconds // 60,  # in minutes
                'roast_level': 'Savage' if len(session.questions) > 15 else 'Mild'
            }
        
        return {}

# Global game engine instance
game_engine = GameEngine()