# Deprecated Host & Admin Files

This directory contains all files related to the old host-based architecture that was removed on November 6, 2025.

## Why These Were Removed

The game was simplified to eliminate complexity:

- **No separate host interface** - Game controls moved to TV view
- **No admin panel** - Not needed for gameplay
- **Auto game creation** - Direct from home page to TV view
- **Simpler flow** - Just TV + Players

## What Was Archived

### HTML Templates (`templates/`)

- `host.html` - Host dashboard
- `host_lobby.html` - Host lobby screen
- `host_play.html` - Host game control panel
- `host_results.html` - Host results view
- `create.html` - Game creation page
- `admin.html` - Admin panel

### JavaScript Files (`js/`)

- `host.js` - Host dashboard logic
- `host_lobby.js` - Host lobby functionality
- `host_play.js` - Host game control logic
- `host_results.js` - Host results display

### Backend Routes (`routes/`)

- `admin.py` - Admin panel routes

### Test Files

- `test_auto_advance_manual.py` - Manual auto-advance test
- `test_complete_game.py` - Complete game flow test

### Playwright Tests (`playwright_tests/`)

All `.spec.ts` files that tested the old host-based flow:

- `api-contract.spec.ts`
- `auto-advance-verification.spec.ts`
- `bulletproof-auto-advance.spec.ts`
- `complete-game.spec.ts`
- `edge-cases.spec.ts`
- `fix-validation.spec.ts`
- `four-player-bulletproof.spec.ts`
- `full-game.spec.ts`
- `jackbox-auto-advance.spec.ts`
- `simple-auto-advance.spec.ts`

## New Simplified Architecture

See `/SIMPLIFIED_GAME_FLOW.md` for details on the new architecture.

**Key Routes Removed:**

- `/create` - Game creation (now auto-created from home)
- `/host` - Host dashboard
- `/host/lobby` - Host lobby
- `/host/play` - Host game controls
- `/host/results` - Host results
- `/admin` - Admin panel

**Key Routes Kept:**

- `/` - Home (create or join)
- `/join` - Player join page
- `/tv/{room_code}` - TV view with built-in controls
- `/player/{player_id}` - Player game view

## If You Need To Reference These

These files are kept for reference only. They are fully functional but use the old architecture. Do not reintegrate them without updating to the new simplified flow.

---

_Archived: November 6, 2025_
_Reason: Simplified game architecture - removed host interface_
