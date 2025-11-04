#!/usr/bin/env python3
"""
Run the 1280 Trivia Flask-SocketIO server.
"""

import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_path = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_path))

from app import create_app, socketio
from app.config import DevelopmentConfig

if __name__ == '__main__':
    app = create_app(DevelopmentConfig)
    
    print("🚀 Starting 1280 Trivia server...")
    print("🌐 Open your browser to: http://localhost:5001")
    print("📱 Players can join on their phones at the same URL")
    print("⚙️  Admin panel: http://localhost:5001/admin")
    print("\n🎯 Press Ctrl+C to stop the server")
    
    # Run with SocketIO
    socketio.run(app, 
                host='0.0.0.0', 
                port=5001, 
                debug=True,
                allow_unsafe_werkzeug=True)