# Security Fix Regression Test Checklist

**Version**: v1.6 post-security audit
**Date**: 2025-11-10
**Purpose**: Verify security fixes don't break core gameplay

---

## Quick Manual Smoke Test (5 minutes)

### Prerequisites
```bash
# Install dependencies if needed
pip install -r requirements.txt

# Start server
python run_server.py
```

### Test 1: Room Creation & Join Flow
**Validates**: BUG #7 (UUID player IDs), BUG #6 (join_game authentication)

1. **Create Game** (TV View)
   - Navigate to http://localhost:5001
   - Click "Create New Game"
   - Enter host name: "TestHost"
   - Select 5 questions
   - Click "Create Game"
   - ✅ **PASS**: Room code displayed (e.g., "ABCD")
   - ❌ **FAIL**: Error or no room code

2. **Join as Player 1**
   - Open http://localhost:5001/join in new tab
   - Enter room code from step 1
   - Enter name: "Player1"
   - Click "Join Game"
   - ✅ **PASS**: Redirected to player lobby, see "Waiting for game..."
   - ❌ **FAIL**: Error, XSS, or join blocked

3. **Join as Player 2**
   - Repeat step 2 with name "Player2"
   - ✅ **PASS**: Both players visible in TV view
   - ❌ **FAIL**: Only 1 player shown or error

**Expected Player IDs** (check network tab):
- Old (broken): `player_0_1234`, `player_1_5678` (predictable)
- New (fixed): `player_a3f8b2c9d1e4`, `player_7e9c4a1b5f3d` (UUID-based)

---

### Test 2: Start Game Authorization
**Validates**: BUG #1 (host authorization on start_game)

1. **Start Game from TV View** (host socket)
   - In TV view tab, click "Start Game"
   - ✅ **PASS**: Game starts, Question 1 appears on both TV and player screens
   - ❌ **FAIL**: Error, stuck on lobby, or game doesn't start

2. **Try Unauthorized Start** (manual test)
   - Open browser console in Player1 tab
   - Execute:
     ```javascript
     socket.emit('start_game', {room_code: 'ABCD'})
     ```
   - ✅ **PASS**: Error message "Not authenticated" or no effect
   - ❌ **FAIL**: Game starts from non-host socket

---

### Test 3: Answer Submission Flow
**Validates**: BUG #10 (no early answer leak), BUG #2 (WebSocket-only answers)

1. **Submit Answer via WebSocket** (normal flow)
   - On Player1 screen, select answer option
   - Click "Submit Answer"
   - ✅ **PASS**:
     - "Answer submitted!" confirmation
     - Points/score shown
     - **No correct answer revealed** until timer expires
   - ❌ **FAIL**: Correct answer shown immediately, or submission fails

2. **Try HTTP Answer Submission** (should be blocked)
   - Open browser console
   - Execute:
     ```javascript
     fetch('/api/game/answer', {
       method: 'POST',
       headers: {'Content-Type': 'application/json'},
       body: JSON.stringify({player_id: 'player_xxx', answer: 'A'})
     }).then(r => r.json()).then(console.log)
     ```
   - ✅ **PASS**: Returns `410 Gone` error
   - ❌ **FAIL**: Answer accepted or different error

3. **Answer Reveal Timing**
   - Wait for timer to expire or all players to answer
   - ✅ **PASS**: Correct answer shown ONLY after reveal event
   - ❌ **FAIL**: Answer leaked earlier

---

### Test 4: Next Question Authorization
**Validates**: BUG #1 extension (host authorization on next_question)

1. **Advance from TV View** (authorized)
   - After reveal, TV shows "Next Question" button
   - Click "Next Question"
   - ✅ **PASS**: Question 2 appears on all screens
   - ❌ **FAIL**: Error or stuck

2. **Try Unauthorized Advance** (manual test)
   - In Player1 console:
     ```javascript
     socket.emit('next_question', {room_code: 'ABCD'})
     ```
   - ✅ **PASS**: Error "Not authenticated" or no effect
   - ❌ **FAIL**: Question advances from non-host socket

---

### Test 5: Room Spying Protection
**Validates**: BUG #6 (no anonymous join_room), BUG #8 (no anonymous game_state)

1. **Try Anonymous Room Subscription**
   - Open new incognito tab (no join_game)
   - Open console, execute:
     ```javascript
     const socket = io('http://localhost:5001');
     socket.emit('join_room', {room_code: 'ABCD'});
     socket.on('player_list_updated', console.log);
     ```
   - ✅ **PASS**: Error "Direct room subscription disabled"
   - ❌ **FAIL**: Receives player list broadcasts

2. **Try Anonymous State Request**
   - In same incognito tab:
     ```javascript
     socket.emit('request_game_state', {room_code: 'ABCD'});
     socket.on('game_state_update', console.log);
     ```
   - ✅ **PASS**: Error "Not authenticated"
   - ❌ **FAIL**: Receives game state with questions/scores

---

### Test 6: DoS Protection
**Validates**: BUG #9 (question count limits)

1. **Try Excessive Question Count**
   - On home page, open browser console
   - Execute:
     ```javascript
     fetch('/api/game/create', {
       method: 'POST',
       headers: {'Content-Type': 'application/json'},
       body: JSON.stringify({player_name: 'Hacker', num_questions: 999})
     }).then(r => r.json()).then(console.log)
     ```
   - ✅ **PASS**: Error "cannot exceed 25 (DoS protection)"
   - ❌ **FAIL**: Server processes 999 questions or crashes

2. **Valid Question Count Range**
   - Try creating with 3, 10, 25 questions
   - ✅ **PASS**: All succeed
   - ❌ **FAIL**: Any value in range fails

---

### Test 7: Disabled Endpoints
**Validates**: All deprecated HTTP endpoints return 410 Gone

Run these in browser console:
```javascript
// Should all return 410 Gone
fetch('/api/game/start/ABCD', {method: 'POST'}).then(r => r.status);
fetch('/api/game/next/ABCD', {method: 'POST'}).then(r => r.status);
fetch('/api/game/question/ABCD/host').then(r => r.status);
fetch('/api/game/player-session/player_xxx').then(r => r.status);
```

- ✅ **PASS**: All return `410`
- ❌ **FAIL**: Any return different status or work

---

## Automated Test Suite

### Run Playwright Tests
```bash
# Quick smoke test (2 minutes)
npx playwright test tests/simplified-game-flow.spec.ts --headed

# Full UI tour (5 minutes)
npx playwright test tests/ui-tour.spec.ts

# Comprehensive validation (10 minutes)
npx playwright test tests/full-game-validation.spec.ts
```

**Expected Results**:
- ✅ All tests should PASS with security fixes
- ❌ If tests fail, check:
  1. Are UUIDs breaking client-side player ID expectations?
  2. Are disabled endpoints causing 404/410 errors in frontend?
  3. Are socket auth checks rejecting legitimate players?

---

## Known Breaking Changes from v1.5 → v1.6

### Player IDs Changed
- **Old**: `player_0_1234` (predictable)
- **New**: `player_a3f8b2c9d1e4f5g6` (UUID4)
- **Impact**: Frontend code expecting format `player_{index}_{4digit}` may break
- **Fix**: Use player_id as opaque string, don't parse it

### Disabled Endpoints
These now return `410 Gone`:
- `POST /api/game/start/<room_code>`
- `POST /api/game/next/<room_code>`
- `GET /api/game/question/<room_code>/host`
- `GET /api/game/player-session/<player_id>`
- `Socket event: join_room`

**Impact**: Any frontend code calling these will fail
**Fix**: Use WebSocket equivalents:
- `socket.emit('start_game', {room_code})`
- `socket.emit('next_question', {room_code})`
- State provided in `join_game` response

### Answer Feedback Changed
- **Removed**: `correct_answer` field from immediate `answer_feedback` event
- **Impact**: Players can't see correct answer until `answer_revealed` event
- **Fix**: Frontend should wait for reveal event before showing answer

---

## Regression Checklist Summary

- [ ] Room creation works
- [ ] Multiple players can join
- [ ] Player IDs are UUIDs (not predictable)
- [ ] Host can start game (TV view)
- [ ] Non-host cannot start game
- [ ] Players can submit answers via WebSocket
- [ ] HTTP answer submission blocked (410)
- [ ] Correct answer NOT leaked in immediate feedback
- [ ] Answer revealed only after timer/all players answered
- [ ] Host can advance to next question
- [ ] Non-host cannot advance
- [ ] Anonymous sockets cannot spy on rooms
- [ ] Anonymous sockets cannot request game state
- [ ] Excessive question counts rejected (>25)
- [ ] Valid question counts work (3-25)
- [ ] All deprecated endpoints return 410
- [ ] Playwright tests pass

---

## Contact

If tests fail or you find regressions:
1. Check git commit `894b4a6` (Security Audit v1.6)
2. Review KNOWN_ISSUES.md for expected behavior
3. Report issue with logs from `/tmp/trivia_test_server.log`
