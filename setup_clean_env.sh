#!/bin/bash
# Clean setup script for Flask-SocketIO environment
# Fixes eventlet hanging issues on macOS

set -e

echo "🧹 Cleaning up old virtual environment..."
rm -rf venv

echo "🔨 Creating fresh virtual environment..."
python3 -m venv venv

echo "📦 Activating virtual environment..."
source venv/bin/activate

echo "⬆️  Upgrading pip..."
pip install --upgrade pip

echo "📥 Installing known-good package versions..."
echo "   (Flask 3.0.3, Flask-SocketIO 5.3.6, eventlet 0.33.3)"
pip install flask==3.0.3 flask-socketio==5.3.6 eventlet==0.33.3 python-dotenv==1.0.0 bidict==0.23.1

echo ""
echo "✅ Clean environment ready!"
echo ""
echo "Next steps:"
echo "  1. source venv/bin/activate"
echo "  2. python3 run_server.py"
echo ""
echo "If server still hangs, try gevent instead:"
echo "  pip uninstall eventlet"
echo "  pip install gevent"
echo "  (then update run_server.py to use async_mode='gevent')"
