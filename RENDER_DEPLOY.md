# Deploying 1280 Trivia to Render

This guide helps you deploy to Render to test v1.7 content (workaround for local Flask-SocketIO/eventlet issues).

## Quick Deploy Steps

### 1. Create Render Account
- Go to https://render.com
- Sign up with GitHub (easiest)

### 2. Push Your Code to GitHub
```bash
# Make sure all changes are committed
git add .
git commit -m "Ready for Render deployment - v1.7 content audit"
git push origin main
```

### 3. Create Web Service on Render

1. Click "New +" → "Web Service"
2. Connect your GitHub repo: `1280_Trivia`
3. Configure:
   - **Name**: `1280-trivia-v17` (or your choice)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python3 run_server.py`
   - **Instance Type**: `Free` (for testing)

### 4. Add Environment Variables (if needed)

In Render dashboard → Environment:
- `PYTHON_VERSION`: `3.9` (or your version)
- `PORT`: `5001` (if your app needs it)

### 5. Deploy!

Click "Create Web Service" - Render will:
- Clone your repo
- Install dependencies from `requirements.txt`
- Start the server
- Give you a URL like: `https://1280-trivia-v17.onrender.com`

## Testing v1.7 Content on Render

Once deployed, open the Render URL in your browser and test:

### Manual Testing Checklist
Use [docs/audits/V1.7_MANUAL_TEST_CHECKLIST.md](docs/audits/V1.7_MANUAL_TEST_CHECKLIST.md):

1. **Create a game** on the TV view
2. **Join with 2-4 players** on phones (use the Render URL)
3. **Play 15 questions** and verify:
   - ✅ Tamer poll questions (level 4-6) appear early
   - ✅ 2-3 personalized questions per game
   - ✅ Shock-focused sex trivia (DTF, sneaky link, etc.)
   - ✅ Diverse regular trivia categories
   - ✅ No PII in receipt questions

### Running Playwright Tests Against Render

Update your test to point to Render URL:

```bash
# Set BASE_URL environment variable
export BASE_URL=https://1280-trivia-v17.onrender.com

# Run Playwright test
npx playwright test tests/v17-content-audit.spec.ts --project=chromium-desktop
```

## Troubleshooting

### CSV Files Not Found on Render

If you see warnings about CSV files, you need to ensure they're in the repo:

```bash
# Verify CSV files are tracked by git
git ls-files | grep "\.csv$"

# If symlinks aren't working, copy files directly
cp archive/private_data/*.csv backend/app/

# Commit and redeploy
git add backend/app/*.csv
git commit -m "Add CSV files for Render deployment"
git push origin main
```

### Port Issues

If the app doesn't start, Render uses `PORT` environment variable. Update `run_server.py`:

```python
import os
port = int(os.environ.get('PORT', 5001))
socketio.run(app, host='0.0.0.0', port=port, debug=False)
```

### Logs

Check Render logs:
- Go to your service dashboard
- Click "Logs" tab
- Look for startup messages and errors

## Cost

- **Free tier**: Good for testing, app sleeps after 15 min of inactivity
- **Paid tier** ($7/mo): Keeps app always running, faster

## Alternative: Heroku

If Render doesn't work, try Heroku (very similar setup):
1. Create `Procfile`: `web: python3 run_server.py`
2. Push to Heroku: `git push heroku main`
3. Open app: `heroku open`

---

**Bottom Line**: Deploying to Render bypasses your local Flask-SocketIO/eventlet issue and lets you test all v1.7 content in a real environment! 🚀
