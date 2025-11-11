"""Configuration settings for the application."""

import os
from pathlib import Path

class Config:
    """Base configuration class."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here-change-in-production'
    
    # Database configuration
    DATABASE_PATH = Path(__file__).parent.parent / 'database' / 'trivia.db'
    
    # iMessage database path (updated to use copied DB in project root)
    IMESSAGE_DB_PATH = Path(__file__).parent.parent.parent / 'chat.db'
    
    # Game settings
    QUESTION_TIME_LIMIT = 30  # seconds
    MAX_PLAYERS = 10
    AUTO_REVEAL_DELAY = int(os.environ.get('AUTO_REVEAL_DELAY', 5))
    AUTO_REVEAL_DISPLAY_TIME = int(os.environ.get('AUTO_REVEAL_DISPLAY_TIME', 3))
    
    # Chat parsing settings
    TARGET_CHATS = [
        "1280 Gang Bang",
        "OG 1280",
        "It's Only Gay If You Push Back ",  # Using exact name as found in DB (with space)
        "Just a Bowl"
    ]
    
    # Contact mapping for phone numbers to names
    CONTACT_MAP = {
        "+18034976579": "Benny",
        "18034976579": "Benny",
        "8034976579": "Benny",
        "+19109295033": "Gina", 
        "19109295033": "Gina",
        "9109295033": "Gina",
        "+14046410104": "Ian",
        "14046410104": "Ian", 
        "4046410104": "Ian",
        "+18645065892": "Lauren",
        "18645065892": "Lauren",
        "8645065892": "Lauren"
    }
    
    # Question generation settings
    ROAST_QUESTION_RATIO = 0.4  # 40% roast questions
    RECEIPT_QUESTION_RATIO = 0.3  # 30% receipt questions
    NORMAL_TRIVIA_RATIO = 0.3   # 30% normal trivia

    # Feature Flags
    ENABLE_MANUAL_REVEAL = os.environ.get('ENABLE_MANUAL_REVEAL', 'false').lower() == 'true'  # Deprecated: use auto-reveal
    ENABLE_SURVEY_SYSTEM = os.environ.get('ENABLE_SURVEY_SYSTEM', 'false').lower() == 'true'  # Experimental
    ENABLE_MINIGAMES = os.environ.get('ENABLE_MINIGAMES', 'false').lower() == 'true'  # Not implemented

    # Auto-Reveal Configuration
    ALLOWED_AUTOREVEAL_PHASES = ("question", "poll")  # Phases that trigger auto-reveal

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
