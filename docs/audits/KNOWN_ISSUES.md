# Known Issues – 1280 Trivia

**Last Updated**: 2025-11-10
**Status**: All critical and high-severity issues have been RESOLVED

---

## ✅ Fixed Issues (Resolved in Current Release)

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

## Medium Priority Issues (Not Yet Fixed)

### BUG #5: Player Joins After Game Started
**Status**: ✅ ALREADY PROTECTED
**Notes**: Backend prevents joins when `session.status != "waiting"` (engine.py:144-146)

### BUG #6: Zero Players Can Start Game
**Status**: ✅ ALREADY PROTECTED
**Notes**: Backend checks `len(session.players) == 0` and returns False (engine.py:180)

### BUG #10: Poll Questions With Zero Votes
**Status**: ✅ ALREADY PROTECTED
**Notes**: Poll scoring handles zero votes gracefully (no division by zero)

### BUG #11: Final Sprint Tie Not Handled
**Status**: 🟠 MEDIUM
**Root Cause**: Leaderboard doesn't specify tie-breaking rules for final sprint.
**Impact**: Multiple players can tie for 1st place - unclear who wins.
**Fix**: Add tie-breaker logic (e.g., fastest total time, or shared victory).

### BUG #16: TV Reconnect During Reveal Causes Desync
**Status**: 🟠 MEDIUM
**Root Cause**: WebSocket reconnect doesn't re-fetch reveal state; TV shows loading indefinitely.
**Impact**: Host must refresh page if they lose connection during answer reveal.
**Fix**: Add reconnect handler that calls `/api/game/state/<room_code>` to restore UI.

### 9. Background Task Lost if Reloader Enabled
**Status**: 🟠 MEDIUM
**Root Cause**: Flask development reloader kills background threads on code change.
**Impact**: Auto-advance timer lost during development.
**Fix**: Document that `debug=False` or `use_reloader=False` is required for testing.

---

## Low Priority Issues

### BUG #14: Player Name Emoji Handling
**Status**: 🟢 LOW
**Root Cause**: HTML escaping may not properly handle all emoji/unicode edge cases.
**Impact**: Rare display issues with complex emoji in player names.
**Fix**: Add comprehensive unicode normalization.

### BUG #15: Missing Error Handling in Socket Events
**Status**: 🟢 LOW
**Root Cause**: Some socket event handlers lack try/catch blocks.
**Impact**: Uncaught exceptions could crash socket handler.
**Fix**: Wrap all socket handlers with error boundaries.

### BUG #17: Countdown Bar Not Cleared on Error
**Status**: 🟢 LOW
**Root Cause**: Timer UI state not reset when errors occur.
**Impact**: Visual bug - timer keeps running after error.
**Fix**: Add timer cleanup to error handlers.

### BUG #18: Missing Test IDs in TV View
**Status**: 🟢 LOW
**Root Cause**: TV view lacks data-testid attributes for automated testing.
**Impact**: Harder to write reliable E2E tests.
**Fix**: Add data-testid attributes to key TV elements.

### Minigame Legacy Listeners in tv.js/player.js
**Status**: 🟢 LOW
**Root Cause**: Socket handlers for `minigame_start`, `minigame_result` exist but are never triggered.
**Impact**: Dead code; no functional impact.
**Fix**: Remove or document as future feature.

### Manual Reveal Route Unused but Exposed
**Status**: 🟢 LOW
**Root Cause**: `/api/game/reveal/<room_code>` endpoint exists but auto-reveal removed all calls to it.
**Impact**: Exposed API surface; no security risk but confusing.
**Fix**: Either restore manual reveal OR remove endpoint and consolidate logic.

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
