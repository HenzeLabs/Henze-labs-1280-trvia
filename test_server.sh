#!/bin/bash
# Quick server test script

source venv/bin/activate

echo "🧪 Testing gevent server..."
python3 run_server_gevent.py &
SERVERPID=$!

echo "   Server PID: $SERVERPID"
echo "   Waiting 8 seconds for startup..."
sleep 8

echo "🔍 Testing if server responds..."
curl -I http://localhost:5001 2>&1 | head -5

echo ""
echo "🛑 Stopping server..."
kill $SERVERPID 2>/dev/null
sleep 2

echo ""
echo "✅ If you saw HTTP response above, server works!"
echo "   Now run: python3 run_server_gevent.py"
