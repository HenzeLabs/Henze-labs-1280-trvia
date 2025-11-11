#!/usr/bin/env python3
"""
Minimal Flask-SocketIO server bootloader for debugging.
Use this if run_server.py hangs due to eventlet issues.
"""

import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_path = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_path))

# Monkey-patch eventlet BEFORE importing Flask/SocketIO
import eventlet
eventlet.monkey_patch()

from app import create_app, socketio
from app.config import DevelopmentConfig

if __name__ == "__main__":
    app = create_app(DevelopmentConfig)

    # Use Render's PORT environment variable if available, otherwise default to 5001
    port = int(os.environ.get('PORT', 5001))

    print(f"🚀 Starting Flask-SocketIO server on http://localhost:{port} ...")
    print("   (Minimal bootloader - eventlet monkey-patched)")

    # Minimal configuration - just get it running
    socketio.run(
        app,
        host="0.0.0.0",
        port=port,
        debug=True,
        log_output=True
    )
