# Known Issues – 1280 Trivia

**Last Updated**: 2025-11-10
**Status**: Active tracking for production release

---

## Critical Issues (Blocking Production)

### 1. Poll Questions Never Award Points
**Status**: 🔴 CRITICAL
**Root Cause**: Poll scoring logic (`backend/app/game/engine.py:255-339`) only executes in `/api/game/reveal/<room_code>` endpoint, but auto-reveal flow bypasses this route.
**Impact**: Players never receive points for poll questions; affects ~25% of question pool.
**Fix**: Move poll vote-counting logic into auto-advance path OR restore manual reveal button with auto-trigger.
**Files**:
- `backend/app/game/engine.py:255-339` (get_answer_stats)
- `backend/app/routes/game.py:243-258` (reveal endpoint)

### 2. Player Timers Accumulate (Multiple `setInterval`)
**Status**: 🟡 HIGH
**Root Cause**: `displayQuestion()` calls `this.startTimer()` without clearing previous interval (`frontend/static/js/player.js:427-449`).
**Impact**: Countdown runs 2x-4x speed after question transitions; background `showTimeUp()` floods socket.
**Fix**: Add `if (this.timer) clearInterval(this.timer);` before starting new timer.
**Files**:
- `frontend/static/js/player.js:427-449` (displayQuestion)

### 3. Poll Questions Leak into Final Sprint
**Status**: 🟡 HIGH
**Root Cause**: Final sprint reuses `mixed` question generator which includes polls. Sprint scoring compares answers to placeholder "correct" values.
**Impact**: Players eliminated arbitrarily based on guessing subjective polls.
**Fix**: Filter `question_type !== 'poll'` from sprint question pool OR create dedicated sprint generator.
**Files**:
- `backend/app/routes/game.py:129-136` (start_game)
- `backend/app/game/engine.py:429-520` (_handle_final_sprint_answer)

---

## High Priority Issues

### 4. TV Progress Counter Shows 0/0
**Status**: 🟡 HIGH
**Root Cause**: `loadGameInfo()` checks `data.success` before updating (`frontend/static/js/tv.js:126-133`), but `/api/game/stats/<room_code>` returns bare object without `success` flag.
**Impact**: Players can't see progress through game.
**Fix**: Remove `data.success` check OR add wrapper to API response.
**Files**:
- `frontend/static/js/tv.js:126-133`
- `backend/app/routes/game.py:378-382`

### 5. QR Code Script Throws Error
**Status**: 🟡 HIGH
**Root Cause**: Template instantiates `new QRCode(document.getElementById("tv-qr-code"))` but `<div id="tv-qr-code">` was removed. URL is hard-coded to `http://192.168.1.159:5001/join`.
**Impact**: QR code doesn't render; wrong join URL shown.
**Fix**: Add `<div id="tv-qr-code"></div>` AND change to `window.location.origin + "/join"`.
**Files**:
- `frontend/templates/tv.html:925-935`

### 6. Player Rank Never Shows
**Status**: 🟡 HIGH
**Root Cause**: `updatePlayerInfo()` expects `player.rank` field but `player_list_updated` payload doesn't include it.
**Impact**: Player HUD shows rank as "-" instead of actual position.
**Fix**: Call `game_engine.get_leaderboard()` and include rank in socket payloads.
**Files**:
- `frontend/static/js/player.js:583-595`
- `backend/app/routes/game.py:285-299`

### 7. "Start Game" Button Hidden for Mobile Hosts
**Status**: 🟡 HIGH
**Root Cause**: Button visibility gated on `sessionStorage.is_creator` but room creation flow never sets this key.
**Impact**: Player who creates game on phone can't start it.
**Fix**: Set `sessionStorage.is_creator = 'true'` when player creates room.
**Files**:
- `frontend/static/js/player.js:15`
- `frontend/templates/index.html:42-66`

---

## Medium Priority Issues

### 8. TV Reconnect During Reveal Causes Desync
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

### 10. Minigame Legacy Listeners in tv.js/player.js
**Status**: 🟢 LOW
**Root Cause**: Socket handlers for `minigame_start`, `minigame_result` exist but are never triggered.
**Impact**: Dead code; no functional impact.
**Fix**: Remove or document as future feature.

### 11. Manual Reveal Route Unused but Exposed
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
