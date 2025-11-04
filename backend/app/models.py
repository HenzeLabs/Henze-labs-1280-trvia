"""Database models for the trivia game."""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

class Database:
    """Database connection and operations."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Initialize database tables."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        with self.get_connection() as conn:
            # Messages table for parsed chat data
            conn.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_name TEXT NOT NULL,
                    sender TEXT NOT NULL,
                    message_text TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    message_type TEXT DEFAULT 'text',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Questions table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    question_type TEXT NOT NULL,
                    question_text TEXT NOT NULL,
                    correct_answer TEXT NOT NULL,
                    wrong_answers TEXT NOT NULL,
                    context TEXT,
                    difficulty INTEGER DEFAULT 1,
                    source_message_id INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (source_message_id) REFERENCES messages (id)
                )
            ''')
            
            # Game sessions table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS game_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    room_code TEXT UNIQUE NOT NULL,
                    host_name TEXT NOT NULL,
                    status TEXT DEFAULT 'waiting',
                    current_question_id INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    ended_at DATETIME
                )
            ''')
            
            # Players table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS players (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_session_id INTEGER NOT NULL,
                    player_name TEXT NOT NULL,
                    score INTEGER DEFAULT 0,
                    joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (game_session_id) REFERENCES game_sessions (id)
                )
            ''')
            
            # Game answers table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS game_answers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_id INTEGER NOT NULL,
                    question_id INTEGER NOT NULL,
                    answer TEXT NOT NULL,
                    is_correct BOOLEAN NOT NULL,
                    answered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (player_id) REFERENCES players (id),
                    FOREIGN KEY (question_id) REFERENCES questions (id)
                )
            ''')
            
            conn.commit()

class Message:
    """Message model."""
    
    def __init__(self, db: Database):
        self.db = db
    
    def add_message(self, chat_name: str, sender: str, message_text: str, 
                   timestamp: datetime, message_type: str = 'text') -> int:
        """Add a new message to the database."""
        with self.db.get_connection() as conn:
            cursor = conn.execute('''
                INSERT INTO messages (chat_name, sender, message_text, timestamp, message_type)
                VALUES (?, ?, ?, ?, ?)
            ''', (chat_name, sender, message_text, timestamp, message_type))
            return cursor.lastrowid
    
    def get_messages_by_chat(self, chat_name: str, limit: int = 1000) -> List[Dict]:
        """Get messages from a specific chat."""
        with self.db.get_connection() as conn:
            cursor = conn.execute('''
                SELECT * FROM messages 
                WHERE chat_name = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (chat_name, limit))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_random_messages(self, limit: int = 100) -> List[Dict]:
        """Get random messages for question generation."""
        with self.db.get_connection() as conn:
            cursor = conn.execute('''
                SELECT * FROM messages 
                WHERE LENGTH(message_text) > 10 
                ORDER BY RANDOM() 
                LIMIT ?
            ''', (limit,))
            return [dict(row) for row in cursor.fetchall()]

class Question:
    """Question model."""
    
    def __init__(self, db: Database):
        self.db = db
    
    def add_question(self, category: str, question_type: str, question_text: str,
                    correct_answer: str, wrong_answers: List[str], 
                    context: str = None, difficulty: int = 1,
                    source_message_id: int = None) -> int:
        """Add a new question to the database."""
        with self.db.get_connection() as conn:
            cursor = conn.execute('''
                INSERT INTO questions (category, question_type, question_text, 
                                     correct_answer, wrong_answers, context, 
                                     difficulty, source_message_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (category, question_type, question_text, correct_answer,
                  json.dumps(wrong_answers), context, difficulty, source_message_id))
            return cursor.lastrowid
    
    def get_random_questions(self, category: str = None, limit: int = 10) -> List[Dict]:
        """Get random questions, optionally filtered by category."""
        with self.db.get_connection() as conn:
            if category:
                cursor = conn.execute('''
                    SELECT * FROM questions 
                    WHERE category = ? 
                    ORDER BY RANDOM() 
                    LIMIT ?
                ''', (category, limit))
            else:
                cursor = conn.execute('''
                    SELECT * FROM questions 
                    ORDER BY RANDOM() 
                    LIMIT ?
                ''', (limit,))
            
            questions = []
            for row in cursor.fetchall():
                question = dict(row)
                question['wrong_answers'] = json.loads(question['wrong_answers'])
                questions.append(question)
            return questions
    
    def get_question_by_id(self, question_id: int) -> Optional[Dict]:
        """Get a specific question by ID."""
        with self.db.get_connection() as conn:
            cursor = conn.execute('SELECT * FROM questions WHERE id = ?', (question_id,))
            row = cursor.fetchone()
            if row:
                question = dict(row)
                question['wrong_answers'] = json.loads(question['wrong_answers'])
                return question
            return None

class GameSession:
    """Game session model."""
    
    def __init__(self, db: Database):
        self.db = db
    
    def create_session(self, room_code: str, host_name: str) -> int:
        """Create a new game session."""
        with self.db.get_connection() as conn:
            cursor = conn.execute('''
                INSERT INTO game_sessions (room_code, host_name)
                VALUES (?, ?)
            ''', (room_code, host_name))
            return cursor.lastrowid
    
    def get_session_by_code(self, room_code: str) -> Optional[Dict]:
        """Get game session by room code."""
        with self.db.get_connection() as conn:
            cursor = conn.execute('''
                SELECT * FROM game_sessions WHERE room_code = ?
            ''', (room_code,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def update_session_status(self, session_id: int, status: str):
        """Update game session status."""
        with self.db.get_connection() as conn:
            conn.execute('''
                UPDATE game_sessions 
                SET status = ? 
                WHERE id = ?
            ''', (status, session_id))

class Player:
    """Player model."""
    
    def __init__(self, db: Database):
        self.db = db
    
    def add_player(self, game_session_id: int, player_name: str) -> int:
        """Add a player to a game session."""
        with self.db.get_connection() as conn:
            cursor = conn.execute('''
                INSERT INTO players (game_session_id, player_name)
                VALUES (?, ?)
            ''', (game_session_id, player_name))
            return cursor.lastrowid
    
    def get_players_by_session(self, game_session_id: int) -> List[Dict]:
        """Get all players in a game session."""
        with self.db.get_connection() as conn:
            cursor = conn.execute('''
                SELECT * FROM players 
                WHERE game_session_id = ? 
                ORDER BY score DESC
            ''', (game_session_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def update_player_score(self, player_id: int, score_increment: int):
        """Update a player's score."""
        with self.db.get_connection() as conn:
            conn.execute('''
                UPDATE players 
                SET score = score + ? 
                WHERE id = ?
            ''', (score_increment, player_id))