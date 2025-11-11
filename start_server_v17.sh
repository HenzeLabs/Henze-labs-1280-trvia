#!/bin/bash
# Quick server startup script for v1.7 testing

echo "🎮 Starting 1280 Trivia Server (v1.7 Content Audit)"
echo "=================================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
    echo "⚠️  No virtual environment found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    # Activate venv
    if [ -d "venv" ]; then
        source venv/bin/activate
    else
        source .venv/bin/activate
    fi
fi

echo "✅ Virtual environment activated"
echo ""

# Check if port 5001 is already in use
if lsof -i :5001 >/dev/null 2>&1; then
    echo "⚠️  Port 5001 is already in use!"
    echo "Kill the existing process? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        lsof -ti :5001 | xargs kill -9
        echo "✅ Killed existing process"
    else
        echo "❌ Exiting. Please stop the existing server first."
        exit 1
    fi
fi

echo "🚀 Starting Flask server on http://localhost:5001"
echo ""
echo "📋 Manual Testing Checklist:"
echo "  1. Open http://localhost:5001 in browser"
echo "  2. Create a game room"
echo "  3. Join with 2-3 players (separate tabs/phones)"
echo "  4. Play through 15 questions"
echo "  5. Verify v1.7 content:"
echo "     ✓ Tamer polls (level 4-6) early in game"
echo "     ✓ 2-3 personalized questions per game"
echo "     ✓ Expanded trivia pool (58 questions)"
echo "     ✓ Shock-value sex trivia present"
echo "     ✓ No PII in receipt questions"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=================================================="
echo ""

# Start the server
python3 run_server.py
