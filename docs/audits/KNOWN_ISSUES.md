# Known Issues – 1280 Trivia

**Last Updated**: 2025-11-10
**Status**: All previously critical issues have been RESOLVED

---

## ✅ Fixed Issues (Resolved in Current Release)

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
