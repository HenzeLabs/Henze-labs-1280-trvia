# 🚀 Quick Start - Testing & UI Tour

## ⚠️ FIRST: Start Your Server!

**Before running ANY tests, make sure the server is running:**

```bash
# Terminal 1: Start the Flask server
python run_server.py

# Wait for: "Running on http://localhost:5001"
```

Or if using virtual environment:
```bash
source venv/bin/activate && python run_server.py
```

**Then in a new terminal window:**

## Run All Tests (Automated)

```bash
# Terminal 2: Run tests (server must be running in Terminal 1)

# Run all tests (8 tests: 3 complete + 5 smoke)
npx playwright test

# Run only smoke tests (fast feedback)
npx playwright test --grep @smoke

# Run on mobile
npx playwright test --project=mobile-safari

# View test report
npx playwright show-report
```

## UI Visual Tour (Manual Inspection)

```bash
# Terminal 2: (server running in Terminal 1)

# 🎨 Complete tour - all 11 screens with pauses
npx playwright test ui-tour.spec.ts --headed --debug

# 👥 Quick lobby tour - focus on waiting states
npx playwright test ui-tour.spec.ts -g "Quick lobby tour" --headed --debug
```

**What happens:**
1. Browser opens automatically
2. Test pauses at each screen
3. Console shows what to inspect
4. Click "Resume" to see next screen
5. Make CSS changes in DevTools (live preview)

## Test Files

- **`complete-game-flow.spec.ts`** - Full end-to-end (3 tests)
- **`simplified-game-flow.spec.ts`** - Quick smoke tests (5 tests)
- **`ui-tour.spec.ts`** - Visual inspection with pauses (2 tours)

## Quick Commands

```bash
# Run specific test file
npx playwright test complete-game-flow.spec.ts

# Run with UI mode (interactive)
npx playwright test --ui

# Debug specific test
npx playwright test --debug -g "should create game"

# Generate code (record actions)
npx playwright codegen localhost:5001
```

## During UI Tour - What You Can Do

✅ **Inspect elements** - Right-click → Inspect
✅ **Edit CSS live** - Changes apply immediately in DevTools
✅ **Take screenshots** - Camera icon in DevTools or Playwright
✅ **Test responsive** - Toggle device toolbar (Cmd+Shift+M)
✅ **Compare screens** - Position windows side-by-side
✅ **Note changes** - Copy successful CSS to apply to files

## Screens in UI Tour

1. 🏠 Home page
2. 📺 TV lobby (empty)
3. 📱 Join page
4. 🎮 Player waiting
5. 📺 TV with player
6. 🎯 Question (TV)
7. 📱 Question (player)
8. ✅ Answer submitted
9. ⏭️ Next question
10. 🏆 Final results
11. 📺 TV end state

## Common Issues

**❌ Tests fail immediately?**
→ **SERVER NOT RUNNING!** Start server first: `python run_server.py`
→ Check server is on correct port (5001)
→ Verify `.env.test` has correct BASE_URL

**Browser shows blank pages?**
→ Server is not running or wrong port
→ Check `http://localhost:5001` works in your browser manually

**Browser doesn't open?**
→ Add `--headed` flag

**Inspector missing?**
→ Add `--debug` flag

**Need more time?**
→ Timeout is 10 minutes, that's plenty

**Server already running on port 5001?**
→ Good! You're ready to run tests

## File Locations

**Tests:** `/tests/`
**Templates:** `/frontend/templates/`
**CSS:** `/frontend/static/css/`
**JS:** `/frontend/static/js/`

## More Details

See **`UI_TOUR_GUIDE.md`** for comprehensive guide with examples.
