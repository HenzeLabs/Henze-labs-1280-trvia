# 1280 Trivia - API Contract v1

## 🔒 **IMMUTABLE API SPECIFICATION**

**Version**: v1-api-contract-stable  
**Status**: 🔒 **FROZEN** - Breaking changes require explicit version bump  
**Compatibility**: All future UI and animation layers must conform to this contract

---

## 📋 **REST API Contract**

### **HTTP Endpoints**

| Endpoint                               | Method | Direction       | Payload               | Response                | Notes                      |
| -------------------------------------- | ------ | --------------- | --------------------- | ----------------------- | -------------------------- |
| `/api/game/create`                     | POST   | Client → Server | `CreateGameRequest`   | `CreateGameResponse`    | Creates new game session   |
| `/api/game/join`                       | POST   | Client → Server | `JoinGameRequest`     | `JoinGameResponse`      | Player joins existing game |
| `/api/game/start/{room_code}`          | POST   | Client → Server | None                  | `GameActionResponse`    | Starts game session        |
| `/api/game/question/{room_code}`       | GET    | Client → Server | None                  | `QuestionResponse`      | Gets current question      |
| `/api/game/answer`                     | POST   | Client → Server | `SubmitAnswerRequest` | `SubmitAnswerResponse`  | Submits player answer      |
| `/api/game/leaderboard/{room_code}`    | GET    | Client → Server | None                  | `LeaderboardResponse`   | Gets current standings     |
| `/api/game/next/{room_code}`           | POST   | Client → Server | None                  | `NextQuestionResponse`  | Advances to next question  |
| `/api/game/player-session/{player_id}` | GET    | Client → Server | None                  | `PlayerSessionResponse` | Gets player session info   |
| `/api/game/stats/{room_code}`          | GET    | Client → Server | None                  | `GameStatsResponse`     | Gets game statistics       |

---

## 🔌 **WebSocket Events Contract**

### **Client → Server Events**

| Event                | Payload            | Response                  | Notes                                     |
| -------------------- | ------------------ | ------------------------- | ----------------------------------------- |
| `join_room`          | `JoinRoomEvent`    | None                      | Join WebSocket room for real-time updates |
| `leave_room`         | `LeaveRoomEvent`   | None                      | Leave WebSocket room                      |
| `ping`               | None               | `pong` event              | Connection health check                   |
| `request_game_state` | `GameStateRequest` | `game_state_update` event | Request current game state                |

### **Server → Client Events**

| Event                 | Payload               | Trigger                | Notes                               |
| --------------------- | --------------------- | ---------------------- | ----------------------------------- |
| `player_list_updated` | `PlayerListUpdate`    | Player joins/leaves    | Broadcast to all room members       |
| `game_started`        | None                  | Game starts            | Broadcast to all players            |
| `new_question`        | `NewQuestionEvent`    | New question available | Broadcast to all players            |
| `player_answered`     | `PlayerAnsweredEvent` | Player submits answer  | Broadcast to room (host visibility) |
| `game_finished`       | `GameFinishedEvent`   | Game ends              | Broadcast to all players            |
| `pong`                | None                  | `ping` received        | Connection health response          |
| `game_state_update`   | `GameStateUpdate`     | State requested        | Sent to requesting client           |

---

## 📦 **Data Models Contract**

### **Core Entities**

#### **Player**

```python
@dataclass
class Player:
    id: str                    # Format: "player_{index}_{random4digit}"
    name: str                  # Player display name (max 50 chars)
    score: int = 0             # Total points earned
    answered_current: bool = False  # Has answered current question
    join_time: datetime        # When player joined session
```

#### **Question**

```python
@dataclass
class Question:
    id: int                    # Sequential question ID
    category: str              # "Receipts", "Red Flags", "Trivia", etc
    question_type: str         # "receipts", "roast", "most_likely", "trivia"
    question_text: str         # The actual question text
    correct_answer: str        # Correct answer choice
    wrong_answers: List[str]   # Array of incorrect choices (2-3 items)
    context: str = ""          # Source context (e.g., "1280 Group")
    difficulty: int = 1        # Difficulty level 1-5
```

#### **GameSession**

```python
@dataclass
class GameSession:
    room_code: str                    # 6-character alphanumeric code
    host_name: str                    # Host display name
    status: str = "waiting"           # "waiting", "playing", "finished"
    players: Dict[str, Player]        # player_id → Player mapping
    questions: List[Question]         # All questions for this session
    current_question_index: int = 0   # Current question (0-based)
    current_question_start_time: Optional[datetime] = None
    question_time_limit: int = 30     # Seconds per question
    created_at: datetime              # Session creation timestamp
```

---

## 📨 **Request/Response Schemas**

### **HTTP Request Payloads**

#### **CreateGameRequest**

```json
{
  "host_name": "string" // Optional, defaults to "Anonymous Host"
}
```

#### **JoinGameRequest**

```json
{
  "room_code": "string", // 6-character room code (required)
  "player_name": "string" // Player display name (required)
}
```

#### **SubmitAnswerRequest**

```json
{
  "player_id": "string", // Player ID from join response (required)
  "answer": "string" // Selected answer text (required)
}
```

### **HTTP Response Payloads**

#### **CreateGameResponse**

```json
{
  "success": true,
  "room_code": "ABC123", // 6-character room code
  "message": "Game created! Room code: ABC123"
}
```

#### **JoinGameResponse**

```json
{
  "success": true,
  "player_id": "player_0_1234", // Unique player identifier
  "room_code": "ABC123", // Room code joined
  "message": "Joined game successfully!"
}
```

#### **GameActionResponse**

```json
{
  "success": true,
  "message": "string" // Human-readable result message
}
```

#### **QuestionResponse**

```json
{
  "question": {
    "id": 1,
    "category": "Receipts",
    "question_type": "receipts",
    "question_text": "Who said: 'I can't believe I locked myself out again'?",
    "answers": ["Alice", "Bob", "Charlie", "Dana"], // Shuffled options
    "context": "1280 Group",
    "difficulty": 1,
    "time_remaining": 30 // Seconds left to answer
  }
}
```

#### **SubmitAnswerResponse**

```json
{
  "success": true,
  "is_correct": true, // Whether answer was correct
  "correct_answer": "Alice", // The correct answer
  "points_earned": 160, // Points awarded this question
  "total_score": 160 // Player's total score
}
```

#### **LeaderboardResponse**

```json
{
  "leaderboard": [
    {
      "rank": 1, // Current ranking (1-based)
      "name": "Alice", // Player display name
      "score": 320, // Total points
      "answered_current": true // Has answered current question
    }
  ]
}
```

#### **NextQuestionResponse**

```json
{
  "success": true,
  "message": "Next question loaded"
}

// OR when game ends:
{
  "success": true,
  "game_finished": true,
  "summary": {
    "final_leaderboard": [...],    // Final rankings
    "total_questions": 10,         // Questions played
    "winner": {                    // Top player
      "name": "Alice",
      "score": 800
    }
  }
}
```

#### **PlayerSessionResponse**

```json
{
  "success": true,
  "session": {
    "room_code": "ABC123", // Current room
    "status": "playing", // Session status
    "player_count": 3 // Total players in session
  }
}
```

#### **GameStatsResponse**

```json
{
  "room_code": "ABC123",
  "host_name": "Host",
  "status": "playing", // "waiting", "playing", "finished"
  "total_players": 3, // Number of players
  "current_question": 2, // Current question number (1-based)
  "total_questions": 10, // Total questions in game
  "time_remaining": 25, // Seconds left on current question
  "players_answered": 2 // How many players have answered
}
```

---

## 🔌 **WebSocket Event Payloads**

### **Client → Server Events**

#### **JoinRoomEvent**

```json
{
  "room_code": "ABC123", // Room to join
  "player_id": "player_0_1234" // Player identifier (optional)
}
```

#### **LeaveRoomEvent**

```json
{
  "room_code": "ABC123" // Room to leave
}
```

#### **GameStateRequest**

```json
{
  "room_code": "ABC123" // Room to get state for
}
```

### **Server → Client Events**

#### **PlayerListUpdate**

```json
{
  "players": [
    {
      "id": "player_0_1234", // Player ID
      "name": "Alice", // Display name
      "score": 160 // Current score
    }
  ],
  "total_players": 3 // Total player count
}
```

#### **NewQuestionEvent**

```json
{
  "question": {
    // Same structure as QuestionResponse.question
    "id": 2,
    "category": "Red Flags",
    "question_type": "roast",
    "question_text": "Who was most likely to...",
    "answers": ["Alice", "Bob", "Charlie"],
    "context": "1280 Group",
    "difficulty": 2,
    "time_remaining": 30
  }
}
```

#### **PlayerAnsweredEvent**

```json
{
  "player_id": "player_0_1234", // Who answered
  "is_correct": true // Whether they got it right
}
```

#### **GameFinishedEvent**

```json
{
  "summary": {
    // Same structure as NextQuestionResponse.summary
    "final_leaderboard": [...],
    "total_questions": 10,
    "winner": {
      "name": "Alice",
      "score": 800
    }
  }
}
```

#### **GameStateUpdate**

```json
{
  "stats": {
    // Same structure as GameStatsResponse
  },
  "question": {
    // Current question (if in playing status)
  },
  "leaderboard": [
    // Current standings
  ]
}
```

---

## ⚠️ **Error Response Contract**

All failed requests return this structure:

```json
{
  "success": false,
  "message": "string", // Human-readable error description
  "error_code": "string" // Optional machine-readable error code
}
```

### **Standard Error Codes**

- `ROOM_NOT_FOUND` - Invalid room code
- `GAME_IN_PROGRESS` - Cannot join active game
- `PLAYER_NOT_FOUND` - Invalid player ID
- `ALREADY_ANSWERED` - Player already answered current question
- `TIME_EXPIRED` - Question time limit exceeded
- `INVALID_PAYLOAD` - Malformed request data

---

## 🔒 **Contract Guarantees**

### **Immutable Fields**

These fields NEVER change format once set:

- `player_id` format: `"player_{index}_{random4digit}"`
- `room_code` format: 6-character alphanumeric
- `status` values: `"waiting"`, `"playing"`, `"finished"`
- All timestamp fields use ISO datetime format
- Score values are always non-negative integers

### **Backward Compatibility Promise**

- New fields may be added but existing fields will not change
- Response structures remain stable
- HTTP status codes remain consistent
- WebSocket event names and payloads remain stable

### **Validation Rules**

- Room codes: 6 characters, alphanumeric, case-insensitive
- Player names: 1-50 characters, no special validation
- Host names: 1-50 characters, defaults to "Anonymous Host"
- Question time limit: 10-60 seconds
- Max players per session: 20

---

## 🔄 **State Transitions**

### **Game Session States**

```
"waiting" → "playing" → "finished"
     ↑________________________↓
        (new game created)
```

### **Player Answer States**

```
answered_current: false → true (per question)
                   ↑_______↓
              (resets on new question)
```

---

## 📝 **Usage Notes**

1. **Room Codes**: Always uppercase in responses, case-insensitive in requests
2. **Player IDs**: Generated server-side, never reused within session
3. **Timing**: All timestamps in UTC, time_remaining always accurate to second
4. **Real-time**: WebSocket events fired immediately on state changes
5. **Persistence**: Sessions exist only in memory, cleared on server restart

---

**Contract Version**: v1.0.0  
**Last Updated**: November 4, 2025  
**Stability**: 🔒 FROZEN - Breaking changes require major version bump
