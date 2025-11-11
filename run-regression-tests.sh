#!/bin/bash
#
# Security Regression Test Runner for v1.5 + v1.6
#
# This script validates that security fixes don't break core gameplay
#

set -e

echo "🔒 Security Regression Test Suite - v1.6"
echo "========================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found${NC}"
    exit 1
fi

if ! command -v npx &> /dev/null; then
    echo -e "${RED}❌ npm/npx not found. Install Node.js first.${NC}"
    exit 1
fi

if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}❌ requirements.txt not found. Run from project root.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites OK${NC}"
echo ""

# Install Python dependencies
echo "📦 Installing Python dependencies..."
if ! pip3 list 2>/dev/null | grep -q Flask; then
    echo "Installing Flask and dependencies..."
    pip3 install -r requirements.txt --quiet
    echo -e "${GREEN}✅ Python dependencies installed${NC}"
else
    echo -e "${GREEN}✅ Flask already installed${NC}"
fi
echo ""

# Install Playwright if needed
echo "📦 Checking Playwright installation..."
if ! npx playwright --version &> /dev/null; then
    echo "Installing Playwright..."
    npm install -D @playwright/test
    npx playwright install chromium
    echo -e "${GREEN}✅ Playwright installed${NC}"
else
    echo -e "${GREEN}✅ Playwright already installed${NC}"
fi
echo ""

# Kill any existing server
echo "🧹 Cleaning up old processes..."
pkill -f "python.*run_server.py" 2>/dev/null || true
sleep 1
echo -e "${GREEN}✅ Cleanup complete${NC}"
echo ""

# Start server in background
echo "🚀 Starting test server..."
python3 run_server.py > /tmp/trivia_regression_test.log 2>&1 &
SERVER_PID=$!

# Wait for server to start
echo "⏳ Waiting for server startup..."
for i in {1..10}; do
    if curl -s http://localhost:5001/ > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Server ready on port 5001${NC}"
        break
    fi
    if [ $i -eq 10 ]; then
        echo -e "${RED}❌ Server failed to start. Check logs:${NC}"
        tail -30 /tmp/trivia_regression_test.log
        kill $SERVER_PID 2>/dev/null || true
        exit 1
    fi
    sleep 1
done
echo ""

# Run security regression tests
echo "🧪 Running security regression tests..."
echo ""

if npx playwright test tests/security-regression.spec.ts --reporter=list; then
    echo ""
    echo -e "${GREEN}✅ ALL SECURITY REGRESSION TESTS PASSED${NC}"
    TEST_STATUS=0
else
    echo ""
    echo -e "${RED}❌ SOME TESTS FAILED - Check output above${NC}"
    TEST_STATUS=1
fi

echo ""
echo "📊 Additional test options:"
echo "  - Quick smoke test:    npx playwright test tests/simplified-game-flow.spec.ts"
echo "  - Full UI tour:        npx playwright test tests/ui-tour.spec.ts"
echo "  - Comprehensive:       npx playwright test tests/full-game-validation.spec.ts"
echo ""

# Cleanup
echo "🧹 Stopping test server..."
kill $SERVER_PID 2>/dev/null || true
echo ""

if [ $TEST_STATUS -eq 0 ]; then
    echo -e "${GREEN}🎉 Security fixes validated - No gameplay regressions detected!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Review REGRESSION_TEST_CHECKLIST.md for manual verification"
    echo "  2. Deploy with confidence - all security patches working correctly"
else
    echo -e "${YELLOW}⚠️  Review test failures above and check:${NC}"
    echo "  - Server logs: /tmp/trivia_regression_test.log"
    echo "  - Playwright report: npx playwright show-report"
    echo "  - Known breaking changes in REGRESSION_TEST_CHECKLIST.md"
fi

exit $TEST_STATUS
