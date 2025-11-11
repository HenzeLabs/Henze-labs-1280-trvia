# Fresh Security Audit Prompt - 1280 Trivia Game

## Context

You are conducting a **comprehensive security and code quality audit** of a Flask-SocketIO multiplayer trivia game. This is a **fresh audit with new eyes** - approach it as if you've never seen this codebase before.

## Your Mission

Perform a thorough security audit focusing on:
1. **Security vulnerabilities** (authentication, authorization, injection, XSS, CSRF)
2. **Race conditions** (concurrency bugs, thread safety)
3. **Memory leaks** (resource cleanup, session management)
4. **Logic bugs** (edge cases, error handling, state management)
5. **Performance issues** (N+1 queries, inefficient algorithms, bottlenecks)
6. **Code quality** (dead code, inconsistencies, technical debt)

## What You Need to Know

### Tech Stack
- **Backend**: Python 3.x, Flask, Flask-SocketIO, SQLite
- **Frontend**: Vanilla JavaScript, Socket.IO client
- **Architecture**: In-memory game state (no database for sessions), real-time WebSocket communication

### Game Flow
1. Host creates game → generates room code
2. Players join via room code → get unique player_id
3. Host starts game → questions displayed in sequence
4. Players submit answers → scoring calculated
5. Auto-reveal triggers when all players answer
6. Final sprint phase → race to finish
7. Game ends → leaderboard displayed

### Critical Features
- **Auto-reveal system**: Background task auto-advances after all players answer
- **Socket authentication**: Binds socket_id to player_id to prevent spoofing
- **Session cleanup**: TTL-based cleanup removes stale sessions (2hr TTL)
- **Thread safety**: RLock protects concurrent operations
- **API contract**: Frozen v1.0.0 schema (breaking changes prohibited)

### Previous Audit Results (v1.3-v1.4)
The codebase has undergone **3 security audits** fixing 18 bugs:
- 6 critical/high severity (race conditions, memory leaks, auth bypass)
- 5 medium priority (UI bugs, validation)
- 7 low priority (polish, cleanup)

**Your job is to find what we missed.**

## Audit Methodology

### Phase 1: Architecture Review (30 min)
Read these files to understand the system:
- `README.md` - Project overview
- `docs/api_contract.md` - API specification
- `backend/app/game/engine.py` - Core game logic
- `backend/app/routes/game.py` - API routes and WebSocket handlers
- `backend/app/__init__.py` - App initialization

**Questions to answer:**
- What are the trust boundaries?
- Where is user input accepted?
- What operations are thread-safe?
- How is state managed?
- What can fail catastrophically?

### Phase 2: Threat Modeling (20 min)
Identify attack vectors:
- **Malicious player**: Can they cheat, crash the game, or access other players' data?
- **Malicious host**: Can they manipulate scores, kick players, or leak data?
- **Network attacker**: Can they intercept, replay, or forge messages?
- **Resource exhaustion**: Can they DoS the server with spam or memory leaks?

### Phase 3: Code Review (60 min)
Systematically review each file for:

#### Security Issues
- [ ] Input validation (room codes, player names, answers)
- [ ] Authentication/authorization (who can do what?)
- [ ] Injection vulnerabilities (SQL, XSS, command injection)
- [ ] Session management (fixation, hijacking, expiration)
- [ ] Secrets exposure (API keys, tokens in logs/errors)

#### Concurrency Issues
- [ ] Race conditions (shared state without locks)
- [ ] Deadlocks (circular lock dependencies)
- [ ] Thread safety (mutable shared data)
- [ ] Atomic operations (test-and-set, increment)

#### Resource Management
- [ ] Memory leaks (unbounded growth, circular references)
- [ ] File handle leaks (unclosed files, sockets)
- [ ] Connection leaks (database, WebSocket)
- [ ] Cleanup on error paths

#### Logic Bugs
- [ ] Edge cases (empty lists, zero values, null/undefined)
- [ ] Error handling (try/catch coverage, error propagation)
- [ ] State transitions (invalid state changes)
- [ ] Boundary conditions (off-by-one, overflow)

#### Code Quality
- [ ] Dead code (unused functions, unreachable branches)
- [ ] Inconsistencies (duplicate logic, conflicting patterns)
- [ ] Performance (O(n²) algorithms, unnecessary loops)
- [ ] Maintainability (magic numbers, unclear naming)

### Phase 4: Dynamic Testing (30 min)
Run the application and test:
- [ ] Create game with 0 players, 1 player, 10 players
- [ ] Join game with invalid room code, duplicate names, special characters
- [ ] Submit answers after timeout, before question loads, twice
- [ ] Disconnect/reconnect during different game phases
- [ ] Spam API endpoints (rate limiting?)
- [ ] Open DevTools → check for console errors, network failures

### Phase 5: Documentation (20 min)
Write findings in this format:

```markdown
## BUG #X: [Short Title]
**Severity**: CRITICAL | HIGH | MEDIUM | LOW
**Category**: Security | Concurrency | Memory | Logic | Performance | Quality
**Location**: `file.py:line` or `file.js:function`

**Description**:
[What is the bug? How does it manifest?]

**Impact**:
[What happens if exploited? Who is affected?]

**Reproduction**:
1. Step 1
2. Step 2
3. Observe behavior

**Root Cause**:
[Why does this happen? What's the underlying issue?]

**Recommended Fix**:
[How should this be fixed? Code snippet if possible]

**Priority Justification**:
[Why this severity? What's the risk?]
```

## Specific Areas to Investigate

### High-Risk Areas (Focus Here First)
1. **Socket event handlers** (`backend/app/routes/game.py:600-850`)
   - Are all events authenticated?
   - Can players trigger events for other players?
   - What happens if malformed data is sent?

2. **Auto-advance background task** (`backend/app/routes/game.py:65-150`)
   - Can it be triggered multiple times?
   - What if session is deleted mid-execution?
   - Does it handle exceptions gracefully?

3. **Session cleanup** (`backend/app/__init__.py:30-44`, `backend/app/game/engine.py:883-905`)
   - Can active games be cleaned up?
   - What if cleanup runs during gameplay?
   - Are all resources freed?

4. **Player authentication** (`backend/app/game/engine.py:865-877`)
   - Can socket bindings be forged?
   - What if player disconnects and reconnects?
   - Are bindings cleaned up properly?

5. **Question generation** (`backend/app/generators/question_generator.py`)
   - Can it fail silently?
   - What if no questions are generated?
   - Are there infinite loops?

6. **Frontend state management** (`frontend/static/js/player.js`, `frontend/static/js/tv.js`)
   - Can UI get out of sync with server?
   - What if WebSocket disconnects mid-game?
   - Are timers cleaned up properly?

### Edge Cases to Test
- Game with 1 player (minimum)
- Game with 20 players (maximum)
- Player joins during final sprint
- All players disconnect simultaneously
- Host disconnects mid-game
- Answer submitted after time expires
- Room code collision (unlikely but possible)
- Unicode/emoji in player names
- Very long player names (>50 chars)
- SQL injection in player names (even though no SQL used)
- XSS in player names (HTML/JS injection)
- Negative scores (can they happen?)
- Integer overflow in scores
- Division by zero in scoring
- Empty question set
- Duplicate questions
- Poll with no votes
- Final sprint with no questions

### Questions to Answer
1. **Can a player cheat?** (manipulate scores, see answers early, vote multiple times)
2. **Can a player crash the game?** (malformed input, resource exhaustion, race conditions)
3. **Can a player access other players' data?** (player_id enumeration, session hijacking)
4. **What happens if the server restarts mid-game?** (state persistence, recovery)
5. **What happens if two players have the same name?** (prevented, but what if race condition?)
6. **Can the auto-reveal system fail?** (background task dies, exception thrown)
7. **Are there any memory leaks?** (unbounded growth, circular references)
8. **Are there any race conditions?** (concurrent access to shared state)
9. **Is error handling comprehensive?** (all exceptions caught, logged, handled gracefully)
10. **Is the API contract actually enforced?** (validation, schema checks)

## Deliverables

Provide:
1. **Executive Summary** (2-3 paragraphs)
   - Overall security posture
   - Critical findings count
   - Risk assessment

2. **Detailed Findings** (one section per bug)
   - Use the template above
   - Include code snippets
   - Prioritize by severity

3. **Recommendations** (prioritized list)
   - Quick wins (easy fixes, high impact)
   - Long-term improvements (architecture changes)
   - Testing strategy (unit tests, integration tests)

4. **Risk Matrix**
   ```
   | Severity | Count | Examples |
   |----------|-------|----------|
   | CRITICAL | X     | Bug #1, #2 |
   | HIGH     | X     | Bug #3, #4 |
   | MEDIUM   | X     | Bug #5, #6 |
   | LOW      | X     | Bug #7, #8 |
   ```

## Success Criteria

A successful audit will:
- ✅ Find at least 3-5 new issues (or confirm codebase is solid)
- ✅ Identify at least 1 critical or high-severity issue (if any exist)
- ✅ Provide actionable recommendations with code examples
- ✅ Explain root causes, not just symptoms
- ✅ Prioritize findings by real-world impact

## What NOT to Report

Skip these (already known/accepted):
- ❌ BUG #17: Countdown bar not cleared on error (deferred, low priority)
- ❌ Missing HTTPS (local development server)
- ❌ No rate limiting (small private game, not public)
- ❌ No CSRF tokens (WebSocket-based, not form-based)
- ❌ Secrets in config.py (development only, documented)
- ❌ No database for sessions (intentional design choice)
- ❌ Flask debug mode (disabled in production)

## Files to Review (Priority Order)

### Critical (Must Review)
1. `backend/app/game/engine.py` - Core game logic, state management
2. `backend/app/routes/game.py` - API routes, WebSocket handlers
3. `backend/app/__init__.py` - App initialization, background tasks
4. `frontend/static/js/player.js` - Player UI, answer submission
5. `frontend/static/js/tv.js` - TV view, state synchronization

### Important (Should Review)
6. `backend/app/config.py` - Configuration, validation
7. `backend/app/game/models_v1.py` - API contract, validation
8. `backend/app/generators/question_generator.py` - Question generation
9. `run_server.py` - Server startup, configuration

### Optional (Nice to Review)
10. `backend/app/parsers/imessage_parser.py` - iMessage parsing
11. `backend/app/models.py` - Database models
12. `frontend/static/css/*.css` - Styling (low priority)

## Time Budget

- **Architecture Review**: 30 min
- **Threat Modeling**: 20 min
- **Code Review**: 60 min
- **Dynamic Testing**: 30 min
- **Documentation**: 20 min
- **Total**: ~2.5 hours

## Final Notes

- **Be thorough but pragmatic** - focus on real risks, not theoretical ones
- **Assume malicious actors** - players will try to cheat/break things
- **Think like an attacker** - how would you exploit this system?
- **Provide evidence** - show code snippets, reproduction steps
- **Be constructive** - suggest fixes, not just problems
- **Fresh perspective** - ignore previous audits, find new issues

**Good luck! We're counting on you to find what we missed.** 🔍🛡️
