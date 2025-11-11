# 🎯 1280 Trivia Game - Comprehensive Audit Request

## Context

You are auditing **1280 Trivia**, a Flask-SocketIO multiplayer trivia game designed for parties. The game is currently in active development and has accumulated technical debt, architectural issues, and scope creep that need to be identified and resolved.

---

## Project Overview

### **Technology Stack**
- **Backend**: Python 3.14, Flask, Flask-SocketIO
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Real-time**: Socket.IO for WebSocket communication
- **Data**: CSV-based question storage, in-memory game state
- **Testing**: Playwright (TypeScript) - currently broken/incomplete

### **Game Architecture**
The game follows a **multi-view architecture**:

1. **TV/Spectator View** (`/tv/<room_code>`)
   - Large screen display for all players to watch
   - Shows questions, answers, leaderboard
   - Host controls (Start Game, End Game, Reveal Answer buttons)

2. **Player View** (`/player/<player_id>`)
   - Individual mobile/tablet interface
   - Answer submission
   - Personal score tracking

3. **Join Flow** (`/join`)
   - Players enter room code
   - Enter their name
   - Get redirected to player view

### **Game Flow**
```
1. Host creates game → Gets room code → Opens TV view
2. Players join via /join → Enter room code + name
3. TV shows player count incrementing
4. Host clicks "Start Game" button
5. Questions appear on TV + player devices
6. Players submit answers on their devices
7. Host clicks "Reveal Answer" on TV (CURRENTLY BROKEN)
8. Scoring happens, leaderboard updates
9. Next question auto-advances (or manual advance)
10. Special rounds: Minigame (Killing Floor), Final Sprint
11. Final leaderboard shown
```

### **Question Types**
The game supports multiple question formats:
- **Regular trivia**: Multiple choice, one correct answer
- **Poll questions**: Subjective, vote-based (e.g., "Who's most likely to...")
- **Roast rounds**: Player-targeted questions
- **Receipts**: Personal story reveals
- **Personalized questions**: Generated from friend group survey data (SCOPE CREEP - see below)

### **Known Architecture**

**Backend Structure:**
```
backend/
├── app/
│   ├── __init__.py              # Flask app factory, SocketIO init
│   ├── config.py                # Config classes
│   ├── game/
│   │   └── engine.py            # Core game logic, session management
│   ├── routes/
│   │   ├── main.py              # Page routes (/join, /tv, /player)
│   │   └── game.py              # API routes (/api/game/*)
│   └── generators/
│       ├── question_generator.py    # Main question generator
│       ├── personalized_generator.py # Friend survey questions (REMOVE?)
│       └── csv_loader.py            # CSV question loading
```

**Frontend Structure:**
```
frontend/
├── templates/
│   ├── index.html          # Landing page
│   ├── join.html           # Player join screen
│   ├── player.html         # Player game view
│   └── tv.html             # TV/spectator view
└── static/
    ├── css/style.css
    └── js/
        ├── join.js         # Join flow logic
        ├── player.js       # Player controller
        └── tv.js           # TV controller
```

**Data Files:**
```
Root directory CSV files:
├── regular_trivia_questions.csv      # Generic trivia (KEEP)
├── poll_questions.csv                # Generic polls (KEEP)
├── most_likely_questions.csv         # Generic "most likely" (KEEP)
├── sex_trivia_questions.csv          # Adult trivia (KEEP)
├── friend_group_data.csv             # PERSONAL DATA - REMOVE
├── gina_lauren_personalized.csv      # PERSONAL DATA - REMOVE
└── gina_lauren_questions.csv         # PERSONAL DATA - REMOVE
```

---

## Scope Issues - Known Problems

### **1. Personal Data Contamination**
The `main` branch contains **personal friend group survey data** that should only exist on a `product` branch:
- `friend_group_data.csv` - Contains explicit personal survey responses
- `gina_lauren_*.csv` - Generated questions about specific people (Gina, Lauren, Benny, Ian)
- `backend/app/generators/personalized_generator.py` - Generates questions from survey data

**This is a privacy/scope violation and needs cleanup recommendations.**

### **2. Survey System (Out of Scope)**
Recent commits added a pre-game survey system:
- Commit `284889e`: "Add survey-to-questions generator with complete data flow"
- Commit `44c4286`: "Add pre-game survey system"

These may have introduced:
- `backend/app/routes/survey.py` (unknown if exists)
- `backend/app/models/survey.py` (unknown if exists)
- `frontend/templates/survey.html` (unknown if exists)
- Survey-related imports/dependencies

**Determine if this belongs on main branch or should be product-only.**

---

## Known Critical Bugs (Reported by User)

### **Bug 1: Poll Questions Never Award Points**
**Issue**: The reveal flow is broken for poll questions.

**Root Cause**:
- Poll scoring logic lives in `backend/app/game/engine.py` lines 255-339 (inside `get_answer_stats()`)
- This function is ONLY called by `/api/game/reveal/<room_code>` endpoint
- The new TV UI removed the "Reveal Answer" button (or it's broken)
- Without manual reveal, polls end with zero scoring

**Files Involved**:
- `backend/app/game/engine.py:255-339`
- `backend/app/routes/game.py:243-258` (reveal endpoint)
- `frontend/templates/tv.html:840-870` (TV controls)
- `frontend/static/js/tv.js:21-38` (button handlers)

**Expected Fix**: Either restore reveal button OR move poll scoring to auto-advance path

---

### **Bug 2: Poll Questions Leak into Final Sprint**
**Issue**: Final sprint uses the same mixed question set as normal play, causing subjective poll questions to appear.

**Root Cause**:
- Final sprint reuses `mixed` question generator (`backend/app/routes/game.py:129-136`)
- Poll questions have placeholder "correct" answers (`backend/app/generators/question_generator.py:705-918`)
- `_handle_final_sprint_answer` compares player answer to `correct_answer` (`backend/app/game/engine.py:429-520`)
- Players are arbitrarily eliminated based on guessing subjective polls

**Expected Fix**: Filter out `question_type === 'poll'` from sprint questions OR create dedicated sprint generator

---

### **Bug 3: Player Timers Accumulate (Multiple `setInterval`)**
**Issue**: Countdown runs twice as fast after switching questions.

**Root Cause**:
- `displayQuestion()` always calls `this.startTimer()` (`frontend/static/js/player.js:427-449`)
- Previous `setInterval` is never cleared
- Multiple intervals stack up, causing rapid countdown and background `showTimeUp()` calls

**Expected Fix**: Add `if (this.timer) clearInterval(this.timer);` before starting new timer

---

### **Bug 4: TV Progress Always Shows 0/0**
**Issue**: Header shows "0 / 0" instead of current/total questions.

**Root Cause**:
- `loadGameInfo()` checks `data.success` before updating (`frontend/static/js/tv.js:126-133`)
- Backend `/api/game/stats/<room_code>` returns bare stats object WITHOUT `success` flag (`backend/app/routes/game.py:378-382`)
- Stats are discarded until a socket event updates them

**Expected Fix**: Remove `data.success` check OR add `{"success": true}` wrapper to API response

---

### **Bug 5: QR Code Script Throws Error**
**Issue**: QR code fails to render, wrong URL displayed.

**Root Cause**:
- Template tries to instantiate `new QRCode(document.getElementById("tv-qr-code"), ...)` (`frontend/templates/tv.html:925-935`)
- The HTML never renders a `<div id="tv-qr-code">` element (it was removed to save space)
- URL is hard-coded to `http://192.168.1.159:5001/join` instead of dynamic origin

**Expected Fix**: Add missing `<div id="tv-qr-code"></div>` AND change to `window.location.origin + "/join"`

---

### **Bug 6: Player Rank Never Shows**
**Issue**: Player HUD shows rank as "-" instead of actual rank.

**Root Cause**:
- `updatePlayerInfo()` expects `player.rank` field (`frontend/static/js/player.js:583-595`)
- `player_list_updated` payload is built WITHOUT rank data (`backend/app/routes/game.py:285-299`)
- Server never includes rank in player objects

**Expected Fix**: Call `game_engine.get_leaderboard()` and include rank in socket payloads

---

### **Bug 7: "Start Game" Button Hidden for Mobile Hosts**
**Issue**: Player who creates the game on their phone can't see "Start Game" button.

**Root Cause**:
- Button visibility is gated on `sessionStorage.is_creator` (`frontend/static/js/player.js:15`)
- The active creation flow (`frontend/templates/index.html:42-66`) NEVER sets this key
- The code that sets it only exists in archived files

**Expected Fix**: Set `sessionStorage.is_creator = 'true'` when player creates a room

---

## Audit Tasks

### **1. Code Quality & Architecture**
- [ ] Identify code duplication across files
- [ ] Find unused functions, imports, variables
- [ ] Check for inconsistent naming conventions
- [ ] Identify missing error handling
- [ ] Find hardcoded values that should be config
- [ ] Check for security vulnerabilities (XSS, injection, etc.)
- [ ] Identify race conditions in SocketIO handlers

### **2. Data Flow Analysis**
- [ ] Map complete question → answer → scoring → leaderboard flow
- [ ] Identify where auto-advance happens vs. manual control
- [ ] Trace all SocketIO event chains
- [ ] Find state synchronization issues between TV/player views
- [ ] Check for memory leaks in session management

### **3. Bug Verification**
For each of the 7 bugs listed above:
- [ ] Confirm the bug exists in current code
- [ ] Verify the root cause analysis
- [ ] Propose specific fix with file:line references
- [ ] Identify any related bugs caused by same pattern

### **4. Scope Cleanup**
- [ ] List ALL files containing personal data (search for "Gina", "Lauren", "Benny", "Ian")
- [ ] Identify survey system files that may exist
- [ ] Check for `backend/app/models/` directory (should be gitignored per `.gitignore:42`)
- [ ] Find references to `friend_group_data.csv` in code
- [ ] Recommend git commands to remove personal data

### **5. Missing Features**
- [ ] Check if "Reveal Answer" button exists and works
- [ ] Verify auto-advance is implemented for all question types
- [ ] Check if minigame scoring works correctly
- [ ] Verify final sprint elimination logic
- [ ] Test session cleanup/expiration

### **6. Test Coverage**
- [ ] Review Playwright tests in `tests/` directory
- [ ] Identify what's tested vs. untested
- [ ] Check if tests are runnable (check for `package.json`)
- [ ] Recommend critical test cases to add

### **7. UI/UX Issues**
- [ ] Check responsive design (mobile vs. TV)
- [ ] Verify all buttons are visible on 1920x1080 display
- [ ] Check for layout overflow/scrolling issues
- [ ] Verify WebSocket reconnection handling
- [ ] Check for race conditions in UI updates

### **8. Performance**
- [ ] Identify inefficient database/data queries
- [ ] Check for unnecessary re-renders
- [ ] Find memory leaks (unclosed connections, uncleared intervals)
- [ ] Check SocketIO room management

---

## Deliverables

Please provide:

### **1. Executive Summary**
- Overall code health rating (1-10)
- Top 5 critical issues to fix immediately
- Top 5 architectural improvements needed

### **2. Bug Report**
For each bug (existing 7 + any new ones found):
```markdown
### Bug: [Title]
**Severity**: Critical | High | Medium | Low
**File(s)**: `path/to/file.py:line`
**Root Cause**: [Brief explanation]
**Impact**: [What breaks / who's affected]
**Proposed Fix**: [Specific code changes]
**Related Issues**: [Other bugs caused by same pattern]
```

### **3. Scope Cleanup Plan**
```bash
# Commands to remove personal data from main branch
git rm [files...]
# .gitignore additions
# Verification commands
```

### **4. Code Quality Report**
- Unused code to remove
- Functions that should be refactored
- Missing error handling
- Security vulnerabilities
- Naming inconsistencies

### **5. Architecture Recommendations**
- Suggested file structure changes
- Missing abstractions
- Coupling issues
- State management improvements

### **6. Testing Strategy**
- Critical paths that need tests
- Test fixtures needed
- Integration test scenarios

---

## Important Notes

1. **Don't Run Code**: You are auditing only. Do not execute the server or tests.
2. **Read Files Thoroughly**: Use the Read tool extensively to understand actual implementation
3. **Cross-Reference**: Verify claims by checking multiple related files
4. **Be Specific**: Always include file paths and line numbers
5. **Prioritize**: Mark severity levels (Critical bugs break core gameplay)
6. **Think Holistically**: Consider how frontend/backend/sockets interact
7. **Question Assumptions**: If documentation contradicts code, trust the code
8. **Privacy First**: Treat personal data (Gina, Lauren, etc.) as PII that must be removed

---

## Key Files to Start With

1. **Game Logic**: `backend/app/game/engine.py` (~520 lines)
2. **API Routes**: `backend/app/routes/game.py` (~380+ lines)
3. **TV Controller**: `frontend/static/js/tv.js` (~460 lines)
4. **Player Controller**: `frontend/static/js/player.js` (~600+ lines)
5. **Question Generator**: `backend/app/generators/question_generator.py` (~918 lines)

---

## Questions to Answer

1. Is the reveal flow completely broken or just missing UI?
2. Are there any SocketIO events that fire but have no handlers?
3. Is session cleanup implemented? Do rooms expire?
4. Can the game handle player disconnects gracefully?
5. Are there any SQL injection risks (if DB is used anywhere)?
6. Is the personalized generator safe to keep or must it be removed?
7. Are there any XXS vulnerabilities in player name input?
8. Does the auto-advance work for ALL question types or just some?

---

## Output Format

Please structure your audit report as:

```markdown
# 1280 Trivia - Full Audit Report
Date: [DATE]
Auditor: Claude (Fresh Context)

## Executive Summary
[...]

## Critical Bugs (Immediate Action Required)
[...]

## High Priority Issues
[...]

## Medium Priority Issues
[...]

## Code Quality Issues
[...]

## Architecture Recommendations
[...]

## Scope Cleanup (Personal Data Removal)
[...]

## Testing Recommendations
[...]

## Security Concerns
[...]

## Performance Optimizations
[...]

## Appendix: File Structure Analysis
[...]
```

---

## Success Criteria

Your audit is complete when you can answer:
- ✅ All 7 reported bugs are verified and have fix plans
- ✅ All personal data files are identified for removal
- ✅ All critical bugs are prioritized
- ✅ Missing features are documented
- ✅ Security vulnerabilities are flagged
- ✅ Test coverage gaps are identified
- ✅ Refactoring opportunities are listed

---

**Begin your audit now. Read the codebase thoroughly and provide a comprehensive report.**
