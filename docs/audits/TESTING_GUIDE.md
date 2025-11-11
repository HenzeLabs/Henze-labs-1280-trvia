# Testing Guide - Security Regression Validation

**Version**: v1.6 post-security audit
**Purpose**: Validate security fixes don't break core gameplay
**Est. Time**: 5-15 minutes depending on depth

---

## Quick Start (2 minutes)

### Option 1: Automated Quick Test
```bash
# Start server
python3 run_server.py

# In another terminal, run quick smoke test
./quick-smoke-test.sh
```

**Expected Output:**
```
✅ ALL SMOKE TESTS PASSED
Test Results: 8 passed, 0 failed
```

### Option 2: Full Regression Suite
```bash
# One-command run (installs deps, starts server, runs tests)
./run-regression-tests.sh
```

---

## Test Coverage

### Automated Tests (`security-regression.spec.ts`)

**8 comprehensive regression tests:**

1. **Room Creation & UUID Player IDs** (BUG #7)
   - Creates game, joins player
   - Validates room code format
   - Confirms UUID-based player IDs (not predictable)

2. **Host Authorization** (BUG #1)
   - Attempts unauthorized `start_game` from non-host
   - Verifies only TV (host) can start game
   - Tests `next_question` authorization

3. **Answer Submission Flow** (BUG #2, #10)
   - Submits answer via WebSocket
   - Confirms NO correct answer leaked immediately
   - Validates answer revealed only after timer

4. **DoS Protection** (BUG #9)
   - Rejects excessive question counts (>25)
   - Accepts valid range (3-25)

5. **Disabled Endpoints** (All bugs)
   - Verifies 4 HTTP endpoints return 410 Gone
   - Confirms deprecated paths are inaccessible

6. **Anonymous Socket Protection** (BUG #6, #8)
   - Attempts room subscription without auth
   - Tries to request game state anonymously
   - Validates both are blocked

7. **3-Player Complete Game Flow**
   - Full smoke test with multiple players
   - Join → Start → Answer → Reveal → Next
   - Confirms no gameplay breaks

8. **Frontend Console Errors**
   - Monitors browser console during gameplay
   - Flags unexpected errors (excluding 410s)
   - Validates clean execution

---

## Running Tests

### Prerequisites

**Python:**
```bash
python3 --version  # Should be 3.7+
pip3 install -r requirements.txt
```

**Node.js (for Playwright):**
```bash
node --version  # Should be 14+
npm install -D @playwright/test
npx playwright install chromium
```

### Test Commands

**Quick validation (2 min):**
```bash
./quick-smoke-test.sh
```

**Security regression suite (5 min):**
```bash
./run-regression-tests.sh
```

**Individual test files:**
```bash
# Security-specific tests
npx playwright test tests/security-regression.spec.ts

# Existing smoke tests
npx playwright test tests/simplified-game-flow.spec.ts

# Full UI tour
npx playwright test tests/ui-tour.spec.ts

# Comprehensive validation
npx playwright test tests/full-game-validation.spec.ts
```

**Debug mode (with browser visible):**
```bash
npx playwright test tests/security-regression.spec.ts --headed --workers=1
```

---

## Manual Verification Steps

If automated tests aren't available, follow [REGRESSION_TEST_CHECKLIST.md](REGRESSION_TEST_CHECKLIST.md) for step-by-step manual validation.

### Critical Manual Tests:

1. **Create room, join 2+ players**
   - Verify players show in TV view
   - Check player IDs in network tab (should be UUIDs)

2. **Start game from TV only**
   - Non-host should NOT be able to start

3. **Submit answers**
   - Correct answer should NOT appear immediately
   - Only after timer or all answered

4. **Check disabled endpoints** (use quick-smoke-test.sh)

---

## Expected Results

### ✅ Pass Criteria

All tests should pass if:
- Room creation and join work normally
- Player IDs are UUID-based (16 hex chars)
- Only host can start/advance game
- Answers submit correctly via WebSocket
- No correct answer leaked before reveal
- Excessive question counts rejected
- Disabled endpoints return 410
- Anonymous sockets blocked from spying
- No critical console errors during gameplay

### ❌ Failure Indicators

**Test failures may indicate:**
- Frontend code expecting old player ID format
- Client calling deprecated HTTP endpoints
- Missing socket authentication checks
- Answer feedback expecting `correct_answer` field

**Troubleshooting:**
```bash
# Check server logs
tail -100 /tmp/trivia_regression_test.log

# View Playwright report
npx playwright show-report

# Run with debug
DEBUG=pw:api npx playwright test tests/security-regression.spec.ts --headed
```

---

## Known Breaking Changes

See [REGRESSION_TEST_CHECKLIST.md](REGRESSION_TEST_CHECKLIST.md#known-breaking-changes-from-v15--v16) for full list.

**Key changes:**
- Player IDs: `player_0_1234` → `player_a3f8b2c9d1e4f5g6`
- 5 endpoints disabled (410 Gone)
- `answer_feedback` no longer includes `correct_answer`

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Security Regression Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - uses: actions/setup-node@v3
        with:
          node-version: '16'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          npm install -D @playwright/test
          npx playwright install chromium

      - name: Run regression tests
        run: ./run-regression-tests.sh
```

---

## Reporting Issues

If tests fail or you find regressions:

1. **Capture evidence:**
   ```bash
   # Save server logs
   cp /tmp/trivia_regression_test.log ./test-failure-logs.txt

   # Save Playwright trace
   npx playwright test --trace=on
   npx playwright show-trace trace.zip
   ```

2. **Document:**
   - Which test failed
   - Expected vs actual behavior
   - Browser console errors
   - Network tab (player ID format, endpoint status codes)

3. **Check commits:**
   - v1.5: `32507fc` (initial 5 security fixes)
   - v1.5.1: `053aca8` (host authorization hardening)
   - v1.6: `894b4a6` (additional 5 security fixes)

---

## Additional Resources

- [REGRESSION_TEST_CHECKLIST.md](REGRESSION_TEST_CHECKLIST.md) - Manual test procedures
- [KNOWN_ISSUES.md](KNOWN_ISSUES.md) - All security fixes documented
- [Playwright Documentation](https://playwright.dev/docs/intro)

---

## Summary Checklist

Before deploying v1.6:

- [ ] `./quick-smoke-test.sh` passes (8/8 tests)
- [ ] `./run-regression-tests.sh` passes (all Playwright tests)
- [ ] Manual smoke test with 2-3 players completes successfully
- [ ] No critical console errors in browser during gameplay
- [ ] Deprecated endpoints return 410 (not 200 or 404)
- [ ] Player IDs are UUID-based (check network tab)
- [ ] Answers don't leak before reveal
- [ ] Only host can start/advance game

**If all ✅: Deploy with confidence - security fixes validated!**
