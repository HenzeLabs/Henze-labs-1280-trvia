# v1.7 Content Audit - Manual Testing Guide

## Quick Start

### Option 1: Use the startup script
```bash
./start_server_v17.sh
```

### Option 2: Manual startup
```bash
source venv/bin/activate  # or source .venv/bin/activate
python3 run_server.py
```

Server will start at: **http://localhost:5001**

---

## Testing Checklist

### 1. Server Startup ✓
- [ ] Server starts without errors
- [ ] Console shows: `* Running on http://127.0.0.1:5001`
- [ ] No Python exceptions in terminal

### 2. Basic Functionality ✓
- [ ] Homepage loads at http://localhost:5001
- [ ] "Create Game" button works
- [ ] Room code is generated (4 characters)
- [ ] Join page works at http://localhost:5001/join
- [ ] Players can join with names

### 3. v1.7 Content Fixes ✓

#### Fix #1: Tamer Poll Questions (Level 4-6)
- [ ] Play 3 games and note when poll questions appear
- [ ] Early polls (Q1-Q5) should be level 4-6 (not all level 10)
- [ ] Examples to look for:
  - "Who's most likely to cry at a sad movie?" (Level 5)
  - "Who's most likely to adopt 10 cats?" (Level 4)
  - "Who's most likely to become a TikTok influencer?" (Level 6)

#### Fix #2: Personalized Questions (2-3 per game)
- [ ] Play a 15-question game
- [ ] Count personalized questions (look for Gina/Lauren specific callouts)
- [ ] Should see 2-3 personalized questions per game
- [ ] Examples:
  - "Who passed out at a reggae club?" (Gina)
  - "Who drunk texts people they've slept with?" (Lauren)
  - "Whose bed is held up by paint cans?" (Gina)

#### Fix #3: Expanded Regular Trivia (58 questions)
- [ ] Play 5 games back-to-back
- [ ] Track regular trivia questions
- [ ] Should see minimal/no repeats across 5 games
- [ ] Verify variety: geography, science, pop culture, technology

#### Fix #4: Shock-Value Sex Trivia
- [ ] Look for new shock-value questions:
  - "What does 'DTF' stand for?" → Down To F*ck
  - "What does 'BBC' mean in a sexual context?" → Big Black C*ck
  - "What's a 'sneaky link'?" → Secret hookup
- [ ] Verify they appear in sex trivia rotation

#### Fix #5: PII Filter in Receipts
- [ ] Play 3 games with receipt questions
- [ ] Verify NO phone numbers appear in receipts
- [ ] Verify NO email addresses appear in receipts
- [ ] Verify NO street addresses appear in receipts
- [ ] Receipt questions should still be funny/embarrassing but safe

### 4. Game Flow & Vibe ✓
- [ ] Questions escalate from tame → wild
- [ ] Final Sprint (last 5 questions) feels climactic
- [ ] Inside jokes land (Benny/Taylor, Tom/cop, Gina/communication)
- [ ] No awkward/cringe moments
- [ ] Overall vibe: Fun roast session (not mean-spirited)

### 5. Question Mix Distribution ✓
Play 3 full games and track question types:

**Game 1:**
- Receipt: ___ (target: 1)
- Roast: ___ (target: 1)
- Personalized: ___ (target: 2-3)
- Most Likely: ___ (target: 3)
- Sex Trivia: ___ (target: 3)
- Regular Trivia: ___ (target: 5)
- Poll: ___ (target: 2)

**Game 2:**
- Receipt: ___
- Roast: ___
- Personalized: ___
- Most Likely: ___
- Sex Trivia: ___
- Regular Trivia: ___
- Poll: ___

**Game 3:**
- Receipt: ___
- Roast: ___
- Personalized: ___
- Most Likely: ___
- Sex Trivia: ___
- Regular Trivia: ___
- Poll: ___

**Target Distribution (15 questions):**
- ~7% Receipt (1)
- ~7% Roast (1)
- ~13% Personalized (2)
- ~20% Most Likely (3)
- ~20% Sex Trivia (3)
- ~33% Regular Trivia (5)
- ~13% Poll (2)

---

## Troubleshooting

### Server won't start
```bash
# Check if port is in use
lsof -i :5001

# Kill existing process
lsof -ti :5001 | xargs kill -9

# Try again
python3 run_server.py
```

### Virtual environment issues
```bash
# Recreate venv
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Database issues
```bash
# Reinitialize database
python3 -c "from backend.app.models import Database; Database('backend/database/trivia.db')"
```

### CSV files not loading
```bash
# Check CSV files exist
ls -la archive/private_data/*.csv

# Verify CSV format
head -n 5 archive/private_data/regular_trivia_questions.csv
```

---

## Success Criteria

✅ All 5 v1.7 fixes verified working  
✅ No runtime errors or crashes  
✅ Question mix matches target distribution  
✅ Game vibe is fun (4+/5 rating)  
✅ No PII leaks in receipts  
✅ Minimal question repeats across 5 games  

---

## Next Steps After Testing

1. **If all tests pass:**
   - Tag release: `git tag v1.7-content-audit-validated`
   - Update FINAL_STATUS.md
   - Ready for production deployment

2. **If issues found:**
   - Document issues in new GitHub issue or AUDIT_V1.7_RESULTS.md
   - Fix and retest
   - Repeat until all tests pass

---

## Quick Manual Test (5 minutes)

Don't have time for full testing? Do this quick check:

1. Start server: `./start_server_v17.sh`
2. Open http://localhost:5001
3. Create game
4. Join with 2 players (2 browser tabs)
5. Play through 5 questions
6. Verify:
   - ✓ At least 1 tamer poll (if poll appears)
   - ✓ Mix of question types
   - ✓ No errors in browser console
   - ✓ Game feels fun

If quick test passes → Full testing likely to pass too!

---

**Happy Testing! 🎮🔥**
