#!/usr/bin/env python3
"""
Run the 1280 Trivia Flask-SocketIO server.
"""

import sys
import logging
from pathlib import Path

# Add the backend directory to the Python path
backend_path = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_path))

from app import create_app, socketio
from app.config import DevelopmentConfig

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s"
    )

    app = create_app(DevelopmentConfig)

    # Runtime safety check for background task compatibility
    use_reloader = False  # CRITICAL: Must be False for auto-reveal to work
    if use_reloader:
        logging.warning("⚠️  WARNING: use_reloader=True will BREAK auto-reveal!")
        logging.warning("⚠️  Background tasks (auto-advance) do not survive Flask reloader.")
        logging.warning("⚠️  Set use_reloader=False or auto-reveal will fail.")
        raise RuntimeError("use_reloader=True is incompatible with auto-reveal background tasks")

    print("🚀 Starting 1280 Trivia server...")
    print("🌐 Open your browser to: http://192.168.1.159:5001")
    print("📱 Players can join on their phones at: http://192.168.1.159:5001/join")
    print("\n✅ Auto-reveal background tasks: ENABLED")
    print("   (use_reloader=False allows greenlet survival)")
    print("\n🎯 Press Ctrl+C to stop the server")

    # Run with SocketIO
    # CRITICAL: use_reloader=False is MANDATORY for auto-reveal background tasks
    # Background tasks (greenlets) do not survive Flask's auto-reloader
    # Without this setting, auto-advance will fail after the first question
    socketio.run(app,
                host='0.0.0.0',
                port=5001,
                debug=False,
                use_reloader=use_reloader,  # REQUIRED to be False for background tasks
                allow_unsafe_werkzeug=True)
