# Local Testing Workaround

Due to Flask-SocketIO/eventlet compatibility issues on your system, here's how to test locally:

## Option 1: Manual Browser Testing (Easiest)

1. **Start server in Terminal 1:**
   ```bash
   cd /Users/laurenadmin/1280_Trivia
   source venv/bin/activate
   python3 run_server.py
   ```

2. **Open in browser:**
   - Go to: http://localhost:5001
   - Create a game, note the room code
   - Open http://localhost:5001/join in other tabs to join as players

3. **Verify v1.7 content manually** using [V1.7_MANUAL_TEST_CHECKLIST.md](docs/audits/V1.7_MANUAL_TEST_CHECKLIST.md)

## Option 2: Playwright Against Running Server

If you get the server running successfully:

1. **Start server (Terminal 1):**
   ```bash
   cd /Users/laurenadmin/1280_Trivia
   source venv/bin/activate
   python3 run_server.py
   ```

2. **Wait for server to fully start** (look for "Press Ctrl+C to stop")

3. **Run Playwright (Terminal 2):**
   ```bash
   cd /Users/laurenadmin/1280_Trivia
   npx playwright test tests/v17-content-audit.spec.ts --project=chromium-desktop --headed
   ```

## Option 3: Test on Render (Recommended)

The easiest option is to just test on the deployed Render site:

**https://henze-labs-1280-trvia.onrender.com**

- No local server issues
- Works in clean Linux environment
- Can test with real friends on phones

## Known Issue: Flask-SocketIO Hangs Locally

Your local environment has a Flask-SocketIO/eventlet compatibility issue where:
- Server shows "started"
- But doesn't actually respond to HTTP requests
- Playwright tests timeout waiting for server

**This is why Render deployment is recommended for testing!**

---

**Bottom line:** Use Render for reliable testing. Local testing is blocked by environment issues.
