"""1280 Trivia Game Application."""

from flask import Flask
from flask_socketio import SocketIO
from .config import Config

# Initialize SocketIO
socketio = SocketIO(cors_allowed_origins="*")

def create_app(config_class=Config):
    """Create and configure the Flask application."""
    app = Flask(__name__, 
                template_folder='../../frontend/templates',
                static_folder='../../frontend/static')
    app.config.from_object(config_class)
    
    # Initialize extensions
    socketio.init_app(app)
    
    # Register blueprints
    from .routes import main, game
    app.register_blueprint(main.bp)
    app.register_blueprint(game.bp)
    
    return app