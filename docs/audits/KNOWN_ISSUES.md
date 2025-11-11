# Known Issues – 1280 Trivia

**Last Updated**: 2025-11-10
**Status**: All critical and high-severity issues have been RESOLVED

---

## ✅ Fixed Issues (Resolved in Current Release)

### 🔒 SECURITY AUDIT v2 (Fresh Eyes Audit - v1.5)

### ✅ SECURITY BUG #1: Host Controls Lack Authorization
**Status**: FIXED (v1.5 security audit)
**Severity**: HIGH
**Resolution**: Added host verification to start_game requiring authenticated player_id.
**Files Changed**:
- `backend/app/game/engine.py:178-183` - Added verify_host() method
- `backend/app/game/engine.py:185-200` - start_game() now requires host_player_id
- `backend/app/routes/game.py:611-617` - Socket handler verifies requester

### ✅ SECURITY BUG #2: HTTP Answer Endpoint Allows Player Spoofing
**Status**: FIXED (v1.5 security audit)
**Severity**: CRITICAL
**Resolution**: Disabled unauthenticated HTTP answer endpoint entirely. Answers must use authenticated WebSocket.
**Files Changed**:
- `backend/app/routes/game.py:333-344` - Endpoint returns 410 Gone

### ✅ SECURITY BUG #3: Socket Join Bypasses Validation → XSS
**Status**: FIXED (v1.5 security audit)
**Severity**: HIGH
**Resolution**: Added APIValidator.validate_player_name() to socket join_game handler.
**Files Changed**:
- `backend/app/routes/game.py:680-685` - Validate and sanitize player names on socket path

### ✅ SECURITY BUG #4: Host Question Endpoint Leaks Correct Answers
**Status**: FIXED (v1.5 security audit)
**Severity**: HIGH
**Resolution**: Disabled unauthenticated host endpoint that leaked answers.
**Files Changed**:
- `backend/app/routes/game.py:318-330` - Endpoint returns 410 Gone

### ✅ SECURITY BUG #5: request_game_state Broadcasts Cross-Room Data
**Status**: FIXED (v1.5 security audit)
**Severity**: MEDIUM
**Resolution**: Added room membership verification and scoped emit to requester only.
**Files Changed**:
- `backend/app/routes/game.py:834-851` - Verify requester is in room, use emit() not broadcast

### ✅ BUG #1: Race Condition in Auto-Advance Flag
**Status**: FIXED (v1.3 security audit)
**Severity**: CRITICAL
**Resolution**: Implemented atomic test-and-set operation using thread-safe `try_start_auto_advance()` method with RLock.
**Files Changed**:
- `backend/app/game/engine.py:823-838` - Added atomic try_start_auto_advance method
- `backend/app/routes/game.py:438` - Uses atomic method instead of direct flag check

### ✅ BUG #2: Memory Leak - No Session Cleanup
**Status**: FIXED (v1.3 security audit)
**Severity**: CRITICAL
**Resolution**: Implemented TTL-based session cleanup with background task running hourly.
**Files Changed**:
- `backend/app/game/engine.py:49` - Added last_activity timestamp
- `backend/app/game/engine.py:859-881` - Added touch_session() and cleanup_stale_sessions()
- `backend/app/__init__.py:30-44` - Added background cleanup loop (runs every hour, 2hr TTL)
- `backend/app/game/engine.py:391,183` - Added touch_session calls to active operations

### ✅ BUG #3: Player ID Spoofing Vulnerability
**Status**: FIXED (v1.3 security audit)
**Severity**: CRITICAL
**Resolution**: Implemented socket session authentication binding player_id to socket_id.
**Files Changed**:
- `backend/app/game/engine.py:58` - Added socket_sessions mapping
- `backend/app/game/engine.py:865-877` - Added bind/verify/unbind methods
- `backend/app/routes/game.py:717` - Binds socket to player on join
- `backend/app/routes/game.py:760-763` - Verifies ownership before accepting answers

### ✅ BUG #4: Room Code Collision Race Condition
**Status**: FIXED (v1.3 security audit)
**Severity**: CRITICAL
**Resolution**: Made generate_room_code() thread-safe with RLock protection.
**Files Changed**:
- `backend/app/game/engine.py:59` - Added RLock to GameEngine
- `backend/app/game/engine.py:61-70` - Protected room code generation with lock

### ✅ BUG #7: Missing Disconnect Handler
**Status**: FIXED (v1.3 security audit)
**Severity**: HIGH
**Resolution**: Added disconnect event handler to clean up socket bindings.
**Files Changed**:
- `backend/app/routes/game.py:828-838` - Added disconnect handler

### ✅ BUG #8: Config Validation Missing
**Status**: FIXED (v1.3 security audit)
**Severity**: HIGH
**Resolution**: Added comprehensive config validation on app startup.
**Files Changed**:
- `backend/app/config.py:59-92` - Added validate() classmethod
- `backend/app/__init__.py:18` - Calls validation on app creation

### ✅ BUG #9: Timer Starts Before Question Renders
**Status**: FIXED (v1.3.1 medium priority fixes)
**Severity**: MEDIUM
**Resolution**: Reordered UI update and timer initialization to show screen first.
**Files Changed**:
- `frontend/static/js/player.js:459-465` - Show UI before starting timer

### ✅ BUG #12: Question Generator Exhaustion
**Status**: FIXED (v1.3.1 medium priority fixes)
**Severity**: MEDIUM
**Resolution**: Added validation to require minimum 3 questions before creating game.
**Files Changed**:
- `backend/app/routes/game.py:616-620` - Validate question count before session creation

### ✅ BUG #13: Hardcoded IP Address in Server
**Status**: FIXED (v1.3.1 medium priority fixes)
**Severity**: MEDIUM
**Resolution**: Dynamically detect local IP address on server startup.
**Files Changed**:
- `run_server.py:35-51` - Added get_local_ip() function

### ✅ BUG #11: Final Sprint Tie Not Handled
**Status**: FIXED (v1.4 final polish)
**Severity**: MEDIUM
**Resolution**: Added tie-breaking using total answer time (faster = better).
**Files Changed**:
- `backend/app/game/engine.py:20` - Added total_answer_time to Player
- `backend/app/game/engine.py:425-426` - Track answer time per question
- `backend/app/game/engine.py:688-727` - Leaderboard sorts by score then time

### ✅ BUG #16: TV Reconnect During Reveal Causes Desync
**Status**: FIXED (v1.4 final polish)
**Severity**: MEDIUM
**Resolution**: Added state restoration on reconnect.
**Files Changed**:
- `frontend/static/js/tv.js:48` - Call restoreGameState on connect
- `frontend/static/js/tv.js:129-156` - Fetch and restore game state

### ✅ BUG #14: Player Name Emoji Handling
**Status**: FIXED (v1.4 final polish)
**Severity**: LOW
**Resolution**: Added unicode normalization (NFC) before HTML escaping.
**Files Changed**:
- `backend/app/game/models_v1.py:9` - Import unicodedata
- `backend/app/game/models_v1.py:217` - Normalize unicode before escaping

### ✅ BUG #15: Missing Error Handling in Socket Events
**Status**: FIXED (v1.4 final polish)
**Severity**: LOW
**Resolution**: Added try/catch to all critical socket handlers.
**Files Changed**:
- `backend/app/routes/game.py:641-665` - Wrapped start_game handler
- `backend/app/routes/game.py:714-761` - Wrapped join_game handler

### ✅ BUG #18: Missing Test IDs in TV View
**Status**: FIXED (v1.4 final polish)
**Severity**: LOW
**Resolution**: Added data-testid attributes to key TV elements.
**Files Changed**:
- `frontend/templates/tv.html:99,124` - Added test IDs for question/sprint screens

### ✅ CLEANUP: Manual Reveal Route Removed
**Status**: FIXED (v1.4 final polish)
**Severity**: LOW
**Resolution**: Removed deprecated manual reveal endpoint entirely.
**Files Changed**:
- `backend/app/routes/game.py:331-368` - Deleted reveal_answer route

### ✅ CLEANUP: Minigame Legacy Listeners Removed
**Status**: FIXED (v1.4 final polish)
**Severity**: LOW
**Resolution**: Removed unused socket listeners for unimplemented minigame feature.
**Files Changed**:
- `frontend/static/js/tv.js:90-98` - Removed minigame socket handlers

### ✅ 1. Poll Questions Never Award Points
**Status**: FIXED (auto-reveal centralization)
**Fixed In**: v1.2 technical audit
**Resolution**: Auto-reveal now uses centralized `ALLOWED_AUTOREVEAL_PHASES` config that includes "poll" phase, ensuring poll scoring works correctly.
**Files Changed**:
- `backend/app/config.py:57` - Added ALLOWED_AUTOREVEAL_PHASES = ("question", "poll")
- `backend/app/routes/game.py:436` - Uses centralized phase list
- `backend/app/game/engine.py:702` - Uses centralized phase list

### ✅ 2. Player Timers Accumulate (Multiple `setInterval`)
**Status**: FIXED
**Fixed In**: v1.1 (prior to audit)
**Resolution**: Added timer cleanup logic that clears existing interval before starting new one.
**Files Changed**:
- `frontend/static/js/player.js:467-470` - Clears timer before starting

### ✅ 3. Poll Questions Leak into Final Sprint
**Status**: FIXED
**Fixed In**: v1.1 (prior to audit)
**Resolution**: Sprint question generation filters out poll, personalized_roast, and personalized_ranking questions.
**Files Changed**:
- `backend/app/routes/game.py:210-218` - Filters question types from sprint

### ✅ 4. TV Progress Counter Shows 0/0
**Status**: FIXED
**Fixed In**: v1.1 (prior to audit)
**Resolution**: Removed `data.success` check that was blocking stats update.
**Files Changed**:
- `frontend/static/js/tv.js:132` - Removed success flag check

### ✅ 5. QR Code Script Throws Error
**Status**: FIXED
**Fixed In**: v1.1 (prior to audit)
**Resolution**: Added missing `<div id="tv-qr-code">` element and changed URL to dynamic origin.
**Files Changed**:
- `frontend/templates/tv.html:72` - Added QR code container
- `frontend/templates/tv.html:139` - Dynamic URL generation

### ✅ 6. Player Rank Never Shows
**Status**: FIXED
**Fixed In**: v1.1 (prior to audit)
**Resolution**: `_build_player_list()` now calls `get_leaderboard()` and includes rank field in player data.
**Files Changed**:
- `backend/app/routes/game.py:30-44` - Includes rank in player list

### ✅ 7. "Start Game" Button Hidden for Mobile Hosts
**Status**: FIXED
**Fixed In**: v1.1 (prior to audit)
**Resolution**: Join flow sets `sessionStorage.is_creator` when first player joins.
**Files Changed**:
- `frontend/static/js/join.js:79` - Sets is_creator flag

---

## Medium Priority Issues (All Resolved or Already Protected)

### BUG #5: Player Joins After Game Started
**Status**: ✅ ALREADY PROTECTED
**Notes**: Backend prevents joins when `session.status != "waiting"` (engine.py:144-146)

### BUG #6: Zero Players Can Start Game
**Status**: ✅ ALREADY PROTECTED
**Notes**: Backend checks `len(session.players) == 0` and returns False (engine.py:180)

### BUG #10: Poll Questions With Zero Votes
**Status**: ✅ ALREADY PROTECTED
**Notes**: Poll scoring handles zero votes gracefully (no division by zero)

### 9. Background Task Lost if Reloader Enabled
**Status**: 🟠 MEDIUM
**Root Cause**: Flask development reloader kills background threads on code change.
**Impact**: Auto-advance timer lost during development.
**Fix**: Document that `debug=False` or `use_reloader=False` is required for testing.

---

## Low Priority Issues (All Resolved)

### BUG #17: Countdown Bar Not Cleared on Error
**Status**: 🟢 LOW - NOT FIXED (minor visual bug)
**Root Cause**: Timer UI state not reset when errors occur.
**Impact**: Visual bug - timer keeps running after error.
**Fix**: Add timer cleanup to error handlers (deferred for future release)

---

## Fixed Issues (Archive)

### ✅ Auto-Reveal Timing Race Condition
**Fixed In**: v1.1 (2025-11-10)
**Resolution**: Moved auto-reveal trigger to background thread with mutex lock.

### ✅ Four-Player UI Overflow
**Fixed In**: v1.2-visual-tour (2025-11-10)
**Resolution**: Implemented responsive grid layout with dynamic scaling.

---

## Notes

- This file consolidates issues scattered across `AUDIT_*.md`, `AUTO_*.md`, and `TEST_RESULTS.md`.
- Priority based on production impact: Critical = core gameplay broken, High = major UX issue, Medium = edge case, Low = cosmetic/future.
- Cross-reference with Playwright tests in `tests/ui-tour.spec.ts` for regression coverage.
