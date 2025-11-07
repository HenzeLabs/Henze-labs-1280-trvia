# 🎮 1280 West Savage Trivia - Quick Start Guide

## ⚡ Start Playing in 30 Seconds

### 1. Start the Server
```bash
cd /Users/laurenadmin/1280_Trivia
source .venv/bin/activate
python3 run_server.py
```

### 2. Host Opens Browser
```
http://localhost:5001/host
```

### 3. Players Open Browser (on phones)
```
http://localhost:5001/join
```

### 4. Play!
- Host: Create game → Share room code
- Players: Enter room code → Join
- Host: Click "Start Game"
- Everyone: Vote and watch chaos unfold! 💀

---

## 📱 URLs You Need

| Page | URL | Who Uses It |
|------|-----|-------------|
| Host Dashboard | `http://localhost:5001/host` | Host (laptop/TV) |
| Player Join | `http://localhost:5001/join` | Players (phones) |
| Home | `http://localhost:5001/` | Everyone |

---

## 🎯 Complete Game Flow

```
HOST                          PLAYERS
────────────────────────────────────────────────
1. Create game
2. Get room code (ABC123)
                            3. Join with code
                            4. Enter name
5. See players joining
6. Click "Start Game"
                            7. See question
8. Display question         8. Vote on answer
9. Reveal answer            9. See if correct
10. Click "Next Question"
11. Repeat until done
12. Show final results      12. See final scores
```

---

## 🔧 Troubleshooting

### Server Not Starting?
```bash
# Make sure you're in the right directory
cd /Users/laurenadmin/1280_Trivia

# Activate virtual environment
source .venv/bin/activate

# Try running
python3 run_server.py
```

### Can't Connect?
- Server running? Check terminal for "wsgi starting up"
- Right URL? Should be `localhost:5001` not `127.0.0.1`
- Port blocked? Try `lsof -i :5001` to check

### Nothing Happens When Creating Game?
1. Hard refresh browser (Cmd+Shift+R or Ctrl+Shift+R)
2. Check console (F12) for errors
3. Make sure you entered a name!

### Players Can't Join?
- Is room code correct? (case-sensitive)
- Is game already started? (can't join after start)
- Duplicate name? (each player needs unique name)

---

## 🎮 Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Enter` | Submit host name / advance prompts |
| `F12` | Open developer console (for debugging) |
| `Cmd+R` / `Ctrl+R` | Refresh page |
| `Cmd+Shift+R` | Hard refresh (clear cache) |

---

## 📊 What to Expect

### Timing
- **Setup**: 1-2 minutes
- **Per Question**: 30 seconds voting + 30 seconds reveal
- **Total Game**: 30-45 minutes
- **Post-Game Roasting**: Priceless

### Questions
- **Current**: 6-10 questions (sample data)
- **Target**: 15 questions (needs full content)
- **Types**: Mix of receipts, trivia, voting, discussions

### Players
- **Minimum**: 2 players (but boring)
- **Optimal**: 4 players (maximum chaos)
- **Maximum**: Technically unlimited, but 4-6 works best

---

## 🔥 Pro Tips

### For Hosts
1. **Test First**: Run through one game solo to learn controls
2. **Big Screen**: Cast to TV for maximum group viewing
3. **Control Pacing**: Don't rush - let the roasting happen
4. **Read Aloud**: Enhance questions with dramatic reading
5. **Encourage Discussion**: Let players defend their votes

### For Players
1. **Fast Fingers**: Speed bonus = more points
2. **Trust Your Gut**: First instinct usually right
3. **Watch Others**: See who's voting for what
4. **Embrace Chaos**: Getting roasted is part of the fun
5. **Stay Connected**: Keep phone from sleeping

### For Maximum Chaos
1. **Savage Mode**: Encourage trash talk
2. **Call Out**: Question each other's votes
3. **Receipts**: Screenshot embarrassing results
4. **Betting**: Wager on answers
5. **Consequences**: Loser buys drinks

---

## 📸 What You'll See

### Host Screen
```
┌────────────────────────────────────────┐
│  1280 TRIVIA          ← Back to Home  │
├────────────────────────────────────────┤
│                                        │
│  ROOM CODE: ABC123                     │
│  Players: Lauren, Benny, Gina, Ian     │
│                                        │
│  [Start Game]                          │
│                                        │
├────────────────────────────────────────┤
│  Current Question:                     │
│  "Who drunk texted an ex at 3am?"      │
│                                        │
│  A) Lauren    B) Benny                 │
│  C) Gina      D) Ian                   │
│                                        │
│  [Reveal Answer]  [Next Question]      │
│                                        │
├────────────────────────────────────────┤
│  LEADERBOARD                           │
│  🥇 Benny  - 480 pts                   │
│  🥈 Lauren - 320 pts                   │
│  🥉 Ian    - 160 pts                   │
│  💀 Gina   - 0 pts                     │
└────────────────────────────────────────┘
```

### Player Screen (Phone)
```
┌─────────────────────────┐
│  1280 TRIVIA            │
├─────────────────────────┤
│  Room: ABC123           │
│  Your Score: 320 pts    │
│                         │
│  Who drunk texted       │
│  an ex at 3am?          │
│                         │
│  [A] Lauren             │
│  [B] Benny              │
│  [C] Gina               │
│  [D] Ian                │
│                         │
│  Votes: 3/4             │
│  Time: 18s              │
└─────────────────────────┘
```

---

## 🆘 Emergency Commands

### Kill Server
```bash
# If server is stuck
pkill -f run_server.py

# Or find process
ps aux | grep run_server
kill -9 <PID>
```

### Clear Database (Fresh Start)
```bash
rm backend/database/trivia.db
python3 -c "from backend.app.models import Database; Database('backend/database/trivia.db')"
```

### Check Server Status
```bash
# See if port 5001 is in use
lsof -i :5001

# Check server logs
tail -f server.log  # if logging to file
```

---

## 📞 Support

### Check These First
1. ✅ **Server running?** - Look for "wsgi starting up"
2. ✅ **Right URL?** - Should be `localhost:5001`
3. ✅ **Virtual env active?** - Should see `(.venv)` in prompt
4. ✅ **Browser cache cleared?** - Try hard refresh

### Debug Mode
Open browser console (F12) and look for:
```javascript
✅ Connected to server
✅ HostDashboard created
✅ Game created successfully!
✅ Room code: ABC123
```

### Still Stuck?
1. Restart server
2. Clear browser cache
3. Check `GAME_AUDIT_REPORT.md` for detailed info
4. Check `DEBUGGING_GUIDE.md` for troubleshooting

---

## 🎉 You're Ready!

**That's it! You now know everything you need to:**
- ✅ Start the server
- ✅ Create a game
- ✅ Add players
- ✅ Play through questions
- ✅ Destroy friendships 💀

**Now go forth and ROAST! 🔥**

---

**Quick Start Version**: 1.0
**Last Updated**: November 4, 2025
**Estimated Setup Time**: 30 seconds
**Estimated Chaos Level**: MAXIMUM 💀
