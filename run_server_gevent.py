#!/usr/bin/env python3
"""
Flask-SocketIO server using gevent instead of eventlet.
Use this if eventlet continues to hang on your system.
"""

import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_path = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_path))

# Monkey-patch gevent BEFORE importing Flask/SocketIO
from gevent import monkey
monkey.patch_all()

from app import create_app, socketio
from app.config import DevelopmentConfig

if __name__ == "__main__":
    app = create_app(DevelopmentConfig)

    # Use Render's PORT environment variable if available, otherwise default to 5001
    port = int(os.environ.get('PORT', 5001))

    print(f"🚀 Starting Flask-SocketIO server on http://localhost:{port} ...")
    print("   (Using gevent async mode)")

    # Run with gevent async mode (set in SocketIO initialization)
    # IMPORTANT: debug=False and use_reloader=False to prevent Flask reloader issues
    socketio.run(
        app,
        host="0.0.0.0",
        port=port,
        debug=False,
        use_reloader=False,  # Reloader breaks gevent greenlets
        log_output=True
    )
