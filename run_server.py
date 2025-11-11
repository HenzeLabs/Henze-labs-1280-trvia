#!/usr/bin/env python3
"""
Run the 1280 Trivia Flask-SocketIO server.
"""

import sys
import logging
import socket
import os
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

    # Get local IP dynamically (fixes BUG #13: hardcoded IP)
    def get_local_ip():
        """Get the local IP address for network access."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception:
            return "localhost"

    local_ip = get_local_ip()
    # Use Render's PORT environment variable if available, otherwise default to 5001
    port = int(os.environ.get('PORT', 5001))

    print("🚀 Starting 1280 Trivia server...")
    print(f"🌐 Open your browser to: http://{local_ip}:{port}")
    print(f"📱 Players can join on their phones at: http://{local_ip}:{port}/join")
    print("\n✅ Auto-reveal background tasks: ENABLED")
    print("   (use_reloader=False allows greenlet survival)")
    print("\n🎯 Press Ctrl+C to stop the server")

    # Run with SocketIO
    # CRITICAL: use_reloader=False is MANDATORY for auto-reveal background tasks
    # Background tasks (greenlets) do not survive Flask's auto-reloader
    # Without this setting, auto-advance will fail after the first question
    socketio.run(app,
                host='0.0.0.0',
                port=port,  # Use dynamic port from environment variable
                debug=False,
                use_reloader=use_reloader,  # REQUIRED to be False for background tasks
                allow_unsafe_werkzeug=True)
