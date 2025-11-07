# 🔒 API Contract Quick Reference

**Version**: v1-api-contract-stable  
**Status**: FROZEN - Breaking changes prohibited

## 🚨 **CRITICAL - READ FIRST**

This API contract is **IMMUTABLE**. Any changes to field names, types, validation rules, or response structures constitute **BREAKING CHANGES** requiring:

1. **Major version bump** (v2.0.0)
2. **Migration documentation**
3. **Backward compatibility plan**
4. **Client notification strategy**

## 📋 **Key Formats (NEVER CHANGE)**

```python
# Player ID format (immutable)
"player_{index}_{random4digit}"  # e.g., "player_0_1234"

# Room code format (immutable)
"[A-Z0-9]{6}"                   # e.g., "ABC123"

# Status values (immutable)
"waiting" | "playing" | "finished"

# Response structure (immutable)
{
  "success": true|false,
  "message": "string",           # Always present
  "error_code": "string"         # Present on errors
}
```

## 🔧 **Validation Functions**

```python
from backend.app.game.models_v1 import APIValidator

# Use these in routes
room_code = APIValidator.validate_room_code("abc123")  # → "ABC123"
player_id = APIValidator.validate_player_id("player_0_1234")
player_name = APIValidator.validate_player_name("Alice")
host_name = APIValidator.validate_host_name(None)  # → "Anonymous Host"
```

## 📦 **Core Models (FROZEN)**

```python
@dataclass(frozen=True)
class Player:
    id: str                    # "player_0_1234"
    name: str                  # 1-50 chars
    score: int = 0             # >= 0
    answered_current: bool = False
    join_time: datetime

@dataclass(frozen=True)
class Question:
    id: int                    # >= 0
    category: str              # "Receipts"|"Red Flags"|"Trivia"|"Most Likely"
    question_type: str         # "receipts"|"roast"|"most_likely"|"trivia"
    question_text: str         # Non-empty
    correct_answer: str        # Non-empty
    wrong_answers: List[str]   # 2-3 items
    context: str = ""
    difficulty: int = 1        # 1-5

@dataclass(frozen=True)
class GameSession:
    room_code: str                    # 6 chars [A-Z0-9]
    host_name: str                    # 1-50 chars
    status: str = "waiting"           # waiting|playing|finished
    players: Dict[str, Player] = {}   # max 20 players
    questions: List[Question] = []
    current_question_index: int = 0   # >= 0
    question_time_limit: int = 30     # 10-60 seconds
    created_at: datetime
```

## 🔌 **WebSocket Events (IMMUTABLE)**

### Client → Server

- `join_room`: `{"room_code": "ABC123", "player_id": "player_0_1234"}`
- `leave_room`: `{"room_code": "ABC123"}`
- `ping`: `{}` → `pong`

### Server → Client

- `player_list_updated`: `{"players": [...], "total_players": 3}`
- `game_started`: `{}`
- `new_question`: `{"question": {...}}`
- `player_answered`: `{"player_id": "...", "is_correct": true}`
- `game_finished`: `{"summary": {...}}`

## 🛡️ **Route Protection**

```python
from backend.app.game.models_v1 import enforce_api_contract

@bp.route('/endpoint', methods=['POST'])
@enforce_api_contract
def my_endpoint():
    # Validation happens automatically
    # Use APIValidator.validate_*() for inputs
    pass
```

## ⚠️ **Error Codes (STANDARD)**

- `ROOM_NOT_FOUND` - Invalid room code
- `GAME_IN_PROGRESS` - Cannot join active game
- `PLAYER_NOT_FOUND` - Invalid player ID
- `ALREADY_ANSWERED` - Player already answered
- `TIME_EXPIRED` - Question time limit exceeded
- `INVALID_PAYLOAD` - Malformed request

## 📖 **Documentation**

- **Full Contract**: `/docs/api_contract.md`
- **JSON Schema**: `/docs/api_schema.json`
- **Test Validation**: `python test_api_contract.py`

---

**Remember**: This contract protects all future UI development. Respect the freeze! 🔒
