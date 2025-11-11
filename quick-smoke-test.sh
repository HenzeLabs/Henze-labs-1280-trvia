#!/bin/bash
#
# Quick Smoke Test - Manual Verification Helper
#
# Validates critical endpoints after security fixes
#

set -e

echo "🚀 Quick Smoke Test - Security Fix Validation"
echo "=============================================="
echo ""

# Check if server is running
if ! curl -s http://localhost:5001/ > /dev/null 2>&1; then
    echo "❌ Server not running on port 5001"
    echo "   Start with: python3 run_server.py"
    exit 1
fi

echo "✅ Server is running"
echo ""

# Test 1: Disabled endpoints return 410
echo "Test 1: Disabled endpoints (BUG #1, #2, #4, #7)"
echo "------------------------------------------------"

ENDPOINTS=(
    "POST:/api/game/start/TEST"
    "POST:/api/game/next/TEST"
    "GET:/api/game/question/TEST/host"
    "GET:/api/game/player-session/player_test"
    "POST:/api/game/answer"
)

PASS=0
FAIL=0

for endpoint in "${ENDPOINTS[@]}"; do
    METHOD="${endpoint%%:*}"
    URL="${endpoint#*:}"

    STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X $METHOD http://localhost:5001$URL \
        -H "Content-Type: application/json" \
        -d '{"player_id":"test","answer":"A"}' 2>/dev/null)

    if [ "$STATUS" -eq 410 ]; then
        echo "  ✅ $METHOD $URL → 410 Gone"
        ((PASS++))
    else
        echo "  ❌ $METHOD $URL → $STATUS (expected 410)"
        ((FAIL++))
    fi
done

echo ""

# Test 2: DoS protection (question count limits)
echo "Test 2: DoS Protection (BUG #9)"
echo "--------------------------------"

# Try excessive question count
RESPONSE=$(curl -s -X POST http://localhost:5001/api/game/create \
    -H "Content-Type: application/json" \
    -d '{"player_name":"Tester","num_questions":999}')

if echo "$RESPONSE" | grep -q "cannot exceed 25\|DoS protection"; then
    echo "  ✅ Excessive question count rejected (999)"
    ((PASS++))
else
    echo "  ❌ Excessive question count NOT rejected"
    echo "     Response: $RESPONSE"
    ((FAIL++))
fi

# Try valid question count
RESPONSE=$(curl -s -X POST http://localhost:5001/api/game/create \
    -H "Content-Type: application/json" \
    -d '{"player_name":"ValidTester","num_questions":5}')

if echo "$RESPONSE" | grep -q '"room_code"'; then
    ROOM_CODE=$(echo "$RESPONSE" | grep -o '"room_code":"[^"]*' | cut -d'"' -f4)
    echo "  ✅ Valid question count accepted (5) → Room: $ROOM_CODE"
    ((PASS++))
else
    echo "  ❌ Valid question count rejected"
    echo "     Response: $RESPONSE"
    ((FAIL++))
fi

echo ""

# Test 3: Health check
echo "Test 3: Server Health"
echo "---------------------"

if curl -s http://localhost:5001/ | grep -q "1280 Trivia\|Create New Game"; then
    echo "  ✅ Home page loads correctly"
    ((PASS++))
else
    echo "  ❌ Home page failed to load"
    ((FAIL++))
fi

if curl -s http://localhost:5001/join | grep -q "Join Game\|Room Code"; then
    echo "  ✅ Join page loads correctly"
    ((PASS++))
else
    echo "  ❌ Join page failed to load"
    ((FAIL++))
fi

echo ""
echo "=============================================="
echo "Test Results: $PASS passed, $FAIL failed"
echo ""

if [ $FAIL -eq 0 ]; then
    echo "✅ ALL SMOKE TESTS PASSED"
    echo ""
    echo "Critical security fixes validated:"
    echo "  ✓ Disabled endpoints return 410 Gone"
    echo "  ✓ DoS protection active (question limits)"
    echo "  ✓ Server pages load correctly"
    echo ""
    echo "Next: Run full test suite with ./run-regression-tests.sh"
    exit 0
else
    echo "❌ SOME TESTS FAILED"
    echo ""
    echo "Check server logs for details:"
    echo "  tail -50 /tmp/trivia_regression_test.log"
    exit 1
fi
