# Deploying 1280 Trivia to Vercel

Quick guide to deploy to Vercel for testing v1.7 content.

## ⚠️ Important Note About Vercel + WebSockets

**Vercel has limitations with WebSockets/SocketIO** on serverless functions. For a real-time game using Flask-SocketIO, **Render or Heroku are better options**.

However, if you want to try Vercel:

## Quick Vercel Deploy

### 1. Install Vercel CLI
```bash
npm install -g vercel
```

### 2. Login to Vercel
```bash
vercel login
```

### 3. Deploy
```bash
vercel
```

Follow the prompts:
- Set up and deploy? **Y**
- Which scope? (your account)
- Link to existing project? **N**
- Project name? `1280-trivia-v17`
- Directory? `./` (press Enter)
- Override settings? **N**

Vercel will give you a URL like: `https://1280-trivia-v17.vercel.app`

## Why Vercel Might Not Work Well

**WebSocket Limitations**:
- Vercel uses serverless functions (AWS Lambda)
- WebSockets don't work in serverless (they need persistent connections)
- Your Flask-SocketIO game needs WebSockets for real-time play

**What happens**:
- Game might load but WebSocket connections will fail
- Players won't be able to join/play in real-time

## ✅ Better Options for Flask-SocketIO

### Option 1: Render (Recommended)
**Pros**:
- Native support for WebSockets
- Persistent server (not serverless)
- Free tier available

**Setup**: See [RENDER_DEPLOY.md](RENDER_DEPLOY.md)

### Option 2: Heroku
**Pros**:
- Excellent WebSocket support
- Easy Python deployment
- Free tier (with limits)

**Setup**:
```bash
# Install Heroku CLI
brew tap heroku/brew && brew install heroku

# Login
heroku login

# Create app
heroku create 1280-trivia-v17

# Create Procfile
echo "web: python3 run_server.py" > Procfile

# Deploy
git add Procfile
git commit -m "Add Heroku Procfile"
git push heroku main

# Open app
heroku open
```

### Option 3: Railway
**Pros**:
- Modern interface
- WebSocket support
- Free tier

**Setup**:
1. Go to https://railway.app
2. Sign in with GitHub
3. "New Project" → "Deploy from GitHub repo"
4. Select `1280_Trivia`
5. Railway auto-detects Python and deploys

## If You Still Want to Try Vercel

You'll need to refactor to use Vercel's serverless model:
1. Remove Flask-SocketIO
2. Use HTTP polling instead of WebSockets
3. Use Vercel KV for state management

**This is a lot of work** - not recommended for quick testing.

## Recommendation

**For testing v1.7 content, use Render**:
- 3 minute setup
- Works perfectly with Flask-SocketIO
- Free tier is sufficient
- See [RENDER_DEPLOY.md](RENDER_DEPLOY.md) for step-by-step guide

---

**TL;DR**: Vercel doesn't support WebSockets well. Use Render or Heroku instead for your real-time trivia game! 🎮
