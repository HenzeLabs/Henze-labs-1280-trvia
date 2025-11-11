# Feature Flags & System Architecture

**Last Updated**: 2025-11-10
**Version**: v1.2 (post-hygiene audit)

---

## Core Features (Always Enabled)

### Lobby & Join Flow
- **Status**: ✅ Production-ready
- **Description**: Players join via room code, wait in lobby until host starts game
- **Files**:
  - `backend/app/routes/main.py` - Join/TV routes
  - `frontend/templates/join.html` - Player join page
  - `frontend/templates/tv.html` - TV lobby view

### Auto-Reveal Gameplay
- **Status**: ✅ Production-ready
- **Description**: Questions auto-advance after all players answer or timer expires
- **Configuration**:
  - `AUTO_REVEAL_DELAY` - Seconds before auto-advance (default: 5)
  - `AUTO_REVEAL_DISPLAY_TIME` - Seconds to show results (default: 3)
  - `ALLOWED_AUTOREVEAL_PHASES` - Phases that trigger auto-reveal (`("question", "poll")`)
- **Files**:
  - `backend/app/routes/game.py:435` - Auto-advance trigger
  - `backend/app/game/engine.py:702` - Phase eligibility check
- **Background Tasks**: Requires `use_reloader=False` in development

### Scoring & Leaderboard
- **Status**: ✅ Production-ready
- **Description**: Real-time score updates, final leaderboard at game end
- **Files**:
  - `backend/app/game/engine.py` - Score calculation
  - `frontend/static/js/player.js` - Player score display
  - `frontend/static/js/tv.js` - Leaderboard rendering

---

## Optional Features (Configurable)

### Survey System
- **Status**: 🧪 Experimental
- **Feature Flag**: `ENABLE_SURVEY_SYSTEM` (default: `false`)
- **Description**: Pre-game survey to generate personalized questions from friend group data
- **Enable**: `export ENABLE_SURVEY_SYSTEM=true`
- **Files**:
  - `backend/app/generators/personalized_generator.py`
  - `friend_group_data.csv` (archived in `archive/private_data/`)
- **Notes**:
  - This feature is separate from the core trivia game
  - Personal data should remain in `archive/private_data/` (gitignored)
  - Not recommended for public deployments due to privacy concerns

### Manual Reveal (Deprecated)
- **Status**: ⚠️ Deprecated (replaced by auto-reveal)
- **Feature Flag**: `ENABLE_MANUAL_REVEAL` (default: `false`)
- **Description**: Legacy endpoint for manual answer reveal via host button click
- **Enable**: `export ENABLE_MANUAL_REVEAL=true` (not recommended)
- **Route**: `/api/game/reveal/<room_code>` (returns HTTP 410 Gone when disabled)
- **Why Deprecated**:
  - Auto-reveal provides better UX and prevents poll scoring bugs
  - Manual reveal bypasses auto-advance scoring logic
  - Increases surface area for desync issues
- **Removal Plan**: Route will be deleted in v2.0

---

## Not Implemented (Feature Flags Exist)

### Minigames
- **Status**: ❌ Not implemented
- **Feature Flag**: `ENABLE_MINIGAMES` (default: `false`)
- **Description**: Placeholder for future "Killing Floor" elimination rounds
- **Files**:
  - Socket listeners exist in `frontend/static/js/tv.js` and `player.js`
  - Backend logic not implemented
- **Notes**: Dead code; safe to remove listeners

---

## Configuration Reference

### Environment Variables

```bash
# Game Settings
QUESTION_TIME_LIMIT=30           # Seconds per question
MAX_PLAYERS=10                   # Max players per room
AUTO_REVEAL_DELAY=5              # Seconds before auto-advance
AUTO_REVEAL_DISPLAY_TIME=3       # Seconds to show results

# Feature Flags
ENABLE_MANUAL_REVEAL=false       # Deprecated: manual reveal endpoint
ENABLE_SURVEY_SYSTEM=false       # Experimental: pre-game surveys
ENABLE_MINIGAMES=false           # Not implemented

# Security
SECRET_KEY=your-secret-key-here  # Change in production!
```

### Python Config (`backend/app/config.py`)

```python
class Config:
    # Core game settings
    QUESTION_TIME_LIMIT = 30
    MAX_PLAYERS = 10
    AUTO_REVEAL_DELAY = int(os.environ.get('AUTO_REVEAL_DELAY', 5))
    AUTO_REVEAL_DISPLAY_TIME = int(os.environ.get('AUTO_REVEAL_DISPLAY_TIME', 3))

    # Feature flags
    ENABLE_MANUAL_REVEAL = os.environ.get('ENABLE_MANUAL_REVEAL', 'false').lower() == 'true'
    ENABLE_SURVEY_SYSTEM = os.environ.get('ENABLE_SURVEY_SYSTEM', 'false').lower() == 'true'
    ENABLE_MINIGAMES = os.environ.get('ENABLE_MINIGAMES', 'false').lower() == 'true'

    # Auto-reveal configuration
    ALLOWED_AUTOREVEAL_PHASES = ("question", "poll")
```

---

## Feature Decision Tree

### Should I enable ENABLE_SURVEY_SYSTEM?

**✅ Enable if**:
- You have a private deployment for a specific friend group
- You have survey data in `friend_group_data.csv`
- You want personalized "roast" and "receipt" questions

**❌ Do NOT enable if**:
- This is a public deployment
- You don't have personalized survey data
- You care about privacy/GDPR compliance

### Should I enable ENABLE_MANUAL_REVEAL?

**❌ Never enable** - this feature is deprecated and causes poll scoring bugs.

### Should I enable ENABLE_MINIGAMES?

**❌ Do NOT enable** - this feature is not implemented yet.

---

## Adding a New Feature

### 1. Add Feature Flag to Config

```python
# backend/app/config.py
ENABLE_MY_FEATURE = os.environ.get('ENABLE_MY_FEATURE', 'false').lower() == 'true'
```

### 2. Gate Feature Logic

```python
# backend/app/routes/game.py
from flask import current_app

if current_app.config.get('ENABLE_MY_FEATURE', False):
    # Feature logic here
    pass
else:
    return jsonify({'success': False, 'message': 'Feature disabled'}), 410
```

### 3. Document in FEATURES.md

Update this file with:
- Feature status (experimental, beta, production)
- Description and use cases
- Configuration options
- Known issues or limitations

### 4. Update Tests

If the feature affects core gameplay, add tests to `tests/` directory.

---

## Feature Status Legend

- ✅ **Production-ready**: Stable, well-tested, recommended for all deployments
- 🧪 **Experimental**: Works but may have bugs or UX issues
- ⚠️ **Deprecated**: Still works but will be removed in future version
- ❌ **Not implemented**: Feature flag exists but no logic behind it

---

## Related Documentation

- [KNOWN_ISSUES.md](../audits/KNOWN_ISSUES.md) - Bugs affecting features
- [PRODUCTION_DEPLOYMENT.md](./PRODUCTION_DEPLOYMENT.md) - Deployment checklist
- [PROJECT_STRUCTURE.md](../../PROJECT_STRUCTURE.md) - Codebase architecture
