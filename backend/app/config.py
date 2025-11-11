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

    @classmethod
    def validate(cls):
        """Validate configuration values to prevent runtime errors."""
        errors = []

        # Validate positive integers
        if cls.QUESTION_TIME_LIMIT <= 0:
            errors.append(f"QUESTION_TIME_LIMIT must be > 0, got {cls.QUESTION_TIME_LIMIT}")
        if cls.MAX_PLAYERS <= 0:
            errors.append(f"MAX_PLAYERS must be > 0, got {cls.MAX_PLAYERS}")
        if cls.AUTO_REVEAL_DELAY < 0:
            errors.append(f"AUTO_REVEAL_DELAY must be >= 0, got {cls.AUTO_REVEAL_DELAY}")
        if cls.AUTO_REVEAL_DISPLAY_TIME < 0:
            errors.append(f"AUTO_REVEAL_DISPLAY_TIME must be >= 0, got {cls.AUTO_REVEAL_DISPLAY_TIME}")

        # Validate ratios sum to 1.0 (or close to it)
        ratio_sum = cls.ROAST_QUESTION_RATIO + cls.RECEIPT_QUESTION_RATIO + cls.NORMAL_TRIVIA_RATIO
        if not (0.99 <= ratio_sum <= 1.01):
            errors.append(f"Question ratios must sum to 1.0, got {ratio_sum:.2f}")

        # Validate individual ratios are between 0 and 1
        for ratio_name in ['ROAST_QUESTION_RATIO', 'RECEIPT_QUESTION_RATIO', 'NORMAL_TRIVIA_RATIO']:
            ratio_value = getattr(cls, ratio_name)
            if not (0 <= ratio_value <= 1):
                errors.append(f"{ratio_name} must be between 0 and 1, got {ratio_value}")

        # Validate SECRET_KEY is changed in production
        if not cls.DEBUG and cls.SECRET_KEY == 'your-secret-key-here-change-in-production':
            errors.append("SECRET_KEY must be changed in production!")

        if errors:
            raise ValueError("Configuration validation failed:\n" + "\n".join(f"  - {err}" for err in errors))

        return True

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
