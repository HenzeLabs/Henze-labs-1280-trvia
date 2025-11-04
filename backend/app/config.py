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

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False