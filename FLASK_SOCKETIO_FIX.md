# Flask-SocketIO Hanging Issue - Complete Fix Guide

Your Flask-SocketIO server hangs due to eventlet compatibility issues on macOS with Python 3.12+. This guide provides a systematic fix.

## Quick Fix (5 minutes)

### Step 1: Clean Environment

```bash
cd /Users/laurenadmin/1280_Trivia
./setup_clean_env.sh
```

This creates a fresh venv with known-good package versions:
- Flask 3.0.3
- Flask-SocketIO 5.3.6
- eventlet 0.33.3 (critical - newer versions hang on macOS)

### Step 2: Test with Minimal Server

```bash
source venv/bin/activate
python3 run_server_minimal.py
```

**Expected output:**
```
🚀 Starting Flask-SocketIO server on http://localhost:5001 ...
   (Minimal bootloader - eventlet monkey-patched)
 * Running on http://127.0.0.1:5001
```

### Step 3: Verify It Works

In another terminal:
```bash
curl http://localhost:5001
```

Should return HTML (not hang).

---

## If Minimal Server Still Hangs

### Switch to gevent (Plan B)

1. **Uninstall eventlet:**
   ```bash
   source venv/bin/activate
   pip uninstall eventlet
   ```

2. **Install gevent:**
   ```bash
   pip install gevent gevent-websocket
   ```

3. **Run gevent server:**
   ```bash
   python3 run_server_gevent.py
   ```

gevent is more stable on macOS and should work where eventlet fails.

---

## Test with Playwright

Once the server responds to `curl`:

1. **Start server (Terminal 1):**
   ```bash
   source venv/bin/activate
   python3 run_server_minimal.py  # or run_server_gevent.py
   ```

2. **Run Playwright tests (Terminal 2):**
   ```bash
   cd /Users/laurenadmin/1280_Trivia
   npx playwright test tests/v17-content-audit.spec.ts --project=chromium-desktop --headed
   ```

The tests should now connect successfully!

---

## Debugging Tips

### Check if Flask works without SocketIO

```bash
python3 -m flask run
```

If this works but socketio doesn't, it's definitely an eventlet/gevent issue.

### Check Python version

```bash
python3 --version
```

- Python 3.11 or earlier: eventlet 0.33.3 should work
- Python 3.12+: eventlet may hang, use gevent instead

### Check what's blocking port 5001

```bash
lsof -i :5001
```

If something else is using it:
```bash
kill -9 $(lsof -t -i :5001)
```

---

## Production Deployment (Render)

Update `requirements.txt` with the working stack:

**For eventlet:**
```
Flask==3.0.3
Flask-SocketIO==5.3.6
eventlet==0.33.3
python-dotenv==1.0.0
bidict==0.23.1
```

**For gevent:**
```
Flask==3.0.3
Flask-SocketIO==5.3.6
gevent==23.9.1
gevent-websocket==0.10.1
python-dotenv==1.0.0
bidict==0.23.1
```

Then update Render start command:
- eventlet: `python3 run_server_minimal.py`
- gevent: `python3 run_server_gevent.py`

---

## Why This Happens

**Root cause:** eventlet's green threading doesn't play well with Python 3.12+ on macOS due to changes in:
- SSL context handling
- Thread initialization
- Asyncio integration

**Solution:** Either:
1. Pin to eventlet 0.33.3 (last stable version)
2. Switch to gevent (more actively maintained)

---

## Files Created

- `setup_clean_env.sh` - Automated environment setup
- `run_server_minimal.py` - Minimal bootloader with eventlet
- `run_server_gevent.py` - Alternative using gevent
- `FLASK_SOCKETIO_FIX.md` - This guide

---

## Success Checklist

- [ ] Clean venv created
- [ ] Known-good packages installed
- [ ] Server starts without hanging
- [ ] `curl http://localhost:5001` responds
- [ ] Playwright tests can connect
- [ ] v1.7 content audit test passes

Once all checked, your environment is fixed! 🎉
