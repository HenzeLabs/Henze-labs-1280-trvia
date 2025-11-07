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
    
    # Chat parsing settings (disabled in product version - use survey system instead)
    TARGET_CHATS = []
    
    # Contact mapping for phone numbers to names (disabled in product version)
    CONTACT_MAP = {}
    
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