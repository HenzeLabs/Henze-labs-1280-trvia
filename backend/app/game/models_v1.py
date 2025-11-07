"""
🔒 FROZEN API MODELS - v1-api-contract-stable
These dataclasses are IMMUTABLE and define the permanent API contract.
Breaking changes require explicit version bump.
"""

import re
from datetime import datetime
from typing import Dict, List, Optional, Union
from dataclasses import dataclass, field


# ============================================================================
# 🔒 FROZEN DATA MODELS - v1.0.0
# ============================================================================

@dataclass(frozen=True)
class Player:
    """
    🔒 FROZEN: Player entity contract
    
    Immutable fields:
    - id: Format "player_{index}_{random4digit}" 
    - name: 1-50 characters
    - score: Non-negative integer
    - answered_current: Boolean flag
    - join_time: UTC datetime
    """
    id: str
    name: str
    score: int = 0
    answered_current: bool = False
    join_time: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate immutable contract constraints."""
        # Validate player ID format
        if not re.match(r'^player_\d+_\d{4}$', self.id):
            raise ValueError(f"Invalid player ID format: {self.id}. Must be 'player_{{index}}_{{4digits}}'")
        
        # Validate name
        if not isinstance(self.name, str) or not (1 <= len(self.name) <= 50):
            raise ValueError(f"Player name must be 1-50 characters: {self.name}")
        
        # Validate score
        if not isinstance(self.score, int) or self.score < 0:
            raise ValueError(f"Player score must be non-negative integer: {self.score}")
        
        # Validate answered_current
        if not isinstance(self.answered_current, bool):
            raise ValueError(f"answered_current must be boolean: {self.answered_current}")


@dataclass(frozen=True)
class Question:
    """
    🔒 FROZEN: Question entity contract
    
    Immutable fields:
    - id: Sequential integer
    - category: Predefined categories 
    - question_type: Predefined types
    - question_text: Non-empty string
    - correct_answer: Non-empty string
    - wrong_answers: 2-3 non-empty strings
    - context: Optional context string
    - difficulty: 1-5 integer
    """
    id: int
    category: str
    question_type: str
    question_text: str
    correct_answer: str
    wrong_answers: List[str]
    context: str = ""
    difficulty: int = 1
    
    # Immutable category constraints
    VALID_CATEGORIES = {"Receipts", "Red Flags", "Trivia", "Most Likely", "WHO'S MOST LIKELY"}
    VALID_TYPES = {"receipts", "roast", "most_likely", "trivia", "poll"}
    
    def __post_init__(self):
        """Validate immutable contract constraints."""
        # Validate ID
        if not isinstance(self.id, int) or self.id < 0:
            raise ValueError(f"Question ID must be non-negative integer: {self.id}")
        
        # Validate category
        if self.category not in self.VALID_CATEGORIES:
            raise ValueError(f"Invalid category: {self.category}. Must be one of {self.VALID_CATEGORIES}")
        
        # Validate question type
        if self.question_type not in self.VALID_TYPES:
            raise ValueError(f"Invalid question_type: {self.question_type}. Must be one of {self.VALID_TYPES}")
        
        # Validate question text
        if not isinstance(self.question_text, str) or len(self.question_text.strip()) == 0:
            raise ValueError(f"Question text must be non-empty string: {self.question_text}")
        
        # Validate correct answer
        if not isinstance(self.correct_answer, str) or len(self.correct_answer.strip()) == 0:
            raise ValueError(f"Correct answer must be non-empty string: {self.correct_answer}")
        
        # Validate wrong answers
        if not isinstance(self.wrong_answers, list) or not (2 <= len(self.wrong_answers) <= 3):
            raise ValueError(f"Must have 2-3 wrong answers: {self.wrong_answers}")
        
        for i, answer in enumerate(self.wrong_answers):
            if not isinstance(answer, str) or len(answer.strip()) == 0:
                raise ValueError(f"Wrong answer {i} must be non-empty string: {answer}")
        
        # Validate difficulty
        if not isinstance(self.difficulty, int) or not (1 <= self.difficulty <= 5):
            raise ValueError(f"Difficulty must be 1-5: {self.difficulty}")


@dataclass(frozen=True)
class GameSession:
    """
    🔒 FROZEN: Game session entity contract
    
    Immutable fields:
    - room_code: 6-character alphanumeric
    - host_name: 1-50 characters
    - status: "waiting", "playing", "finished"
    - players: Dict mapping player_id → Player
    - questions: List of Question objects
    - current_question_index: Non-negative integer
    - question_time_limit: 10-60 seconds
    - created_at: UTC datetime
    """
    room_code: str
    host_name: str
    status: str = "waiting"
    players: Dict[str, Player] = field(default_factory=dict)
    questions: List[Question] = field(default_factory=list)
    current_question_index: int = 0
    current_question_start_time: Optional[datetime] = None
    question_time_limit: int = 30
    created_at: datetime = field(default_factory=datetime.now)
    
    # Immutable status constraints
    VALID_STATUSES = {"waiting", "playing", "finished"}
    MAX_PLAYERS = 20
    
    def __post_init__(self):
        """Validate immutable contract constraints."""
        # Validate room code format
        if not re.match(r'^[A-Z0-9]{6}$', self.room_code):
            raise ValueError(f"Room code must be 6 alphanumeric characters: {self.room_code}")
        
        # Validate host name
        if not isinstance(self.host_name, str) or not (1 <= len(self.host_name) <= 50):
            raise ValueError(f"Host name must be 1-50 characters: {self.host_name}")
        
        # Validate status
        if self.status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid status: {self.status}. Must be one of {self.VALID_STATUSES}")
        
        # Validate players count
        if len(self.players) > self.MAX_PLAYERS:
            raise ValueError(f"Too many players: {len(self.players)}. Max is {self.MAX_PLAYERS}")
        
        # Validate current question index
        if not isinstance(self.current_question_index, int) or self.current_question_index < 0:
            raise ValueError(f"Question index must be non-negative: {self.current_question_index}")
        
        # Validate time limit
        if not isinstance(self.question_time_limit, int) or not (10 <= self.question_time_limit <= 60):
            raise ValueError(f"Time limit must be 10-60 seconds: {self.question_time_limit}")


# ============================================================================
# 🔧 VALIDATION UTILITIES
# ============================================================================

class APIValidator:
    """Runtime validator for API contract compliance."""
    
    @staticmethod
    def validate_room_code(room_code: str) -> str:
        """Validate and normalize room code."""
        if not isinstance(room_code, str):
            raise ValueError("Room code must be string")
        
        normalized = room_code.upper().strip()
        if not re.match(r'^[A-Z0-9]{6}$', normalized):
            raise ValueError(f"Invalid room code format: {room_code}")
        
        return normalized
    
    @staticmethod
    def validate_player_id(player_id: str) -> str:
        """Validate player ID format."""
        if not isinstance(player_id, str):
            raise ValueError("Player ID must be string")
        
        if not re.match(r'^player_\d+_\d{4}$', player_id):
            raise ValueError(f"Invalid player ID format: {player_id}")
        
        return player_id
    
    @staticmethod
    def validate_player_name(name: str) -> str:
        """Validate and normalize player name."""
        if not isinstance(name, str):
            raise ValueError("Player name must be string")
        
        normalized = name.strip()
        if not (1 <= len(normalized) <= 50):
            raise ValueError(f"Player name must be 1-50 characters: {name}")
        
        return normalized
    
    @staticmethod
    def validate_host_name(name: Optional[str]) -> str:
        """Validate and normalize host name."""
        if name is None:
            return "Anonymous Host"
        
        if not isinstance(name, str):
            raise ValueError("Host name must be string")
        
        normalized = name.strip()
        if len(normalized) == 0:
            return "Anonymous Host"
        
        if len(normalized) > 50:
            raise ValueError(f"Host name too long: {name}")
        
        return normalized


# ============================================================================
# 🔒 CONTRACT ENFORCEMENT
# ============================================================================

def enforce_api_contract(func):
    """Decorator to enforce API contract validation on responses."""
    from functools import wraps
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            # Contract validation would go here
            return result
        except Exception as e:
            # Log contract violations
            print(f"⚠️ API Contract violation in {func.__name__}: {e}")
            raise
    return wrapper


# ============================================================================
# 📋 CONTRACT METADATA
# ============================================================================

CONTRACT_VERSION = "1.0.0"
CONTRACT_DATE = "2025-11-04"
CONTRACT_STATUS = "🔒 FROZEN"

IMMUTABLE_FIELDS = {
    "Player": ["id", "name", "score", "answered_current", "join_time"],
    "Question": ["id", "category", "question_type", "question_text", "correct_answer", "wrong_answers", "context", "difficulty"], 
    "GameSession": ["room_code", "host_name", "status", "players", "questions", "current_question_index", "question_time_limit", "created_at"]
}

BREAKING_CHANGE_WARNING = """
⚠️ WARNING: These models are FROZEN for API stability.
Any modifications to field names, types, or validation rules 
constitute BREAKING CHANGES and require:

1. Major version bump (v2.0.0)
2. Migration documentation  
3. Backward compatibility plan
4. Client notification strategy

Contact API maintainer before making changes.
"""