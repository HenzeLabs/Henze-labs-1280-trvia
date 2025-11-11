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

    # Validate configuration on startup
    config_class.validate()

    # Disable template caching for development
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.jinja_env.auto_reload = True
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    
    # Initialize extensions
    socketio.init_app(app)
    
    # Register blueprints
    from .routes import main, game
    app.register_blueprint(main.bp)
    app.register_blueprint(game.bp)

    # Start background cleanup task for stale sessions
    def cleanup_loop():
        """Background task to periodically clean up stale sessions."""
        import time
        from .game.engine import game_engine
        while True:
            time.sleep(3600)  # Run every hour
            try:
                cleaned = game_engine.cleanup_stale_sessions(ttl_hours=2)
                if cleaned > 0:
                    print(f"🧹 Session cleanup: removed {cleaned} stale sessions")
            except Exception as e:
                print(f"❌ Error in cleanup task: {e}")

    socketio.start_background_task(cleanup_loop)

    return app