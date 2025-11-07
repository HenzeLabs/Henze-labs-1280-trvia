# 1280 Trivia - Production Structure

## Essential Files (Required to Run)

```
1280_Trivia/
├── backend/
│   ├── app/
│   │   ├── __init__.py              # Flask app initialization
│   │   ├── config.py                # Configuration (DB paths, contact map)
│   │   ├── game/
│   │   │   ├── engine.py            # Core game logic, state management
│   │   │   └── models_v1.py         # Frozen data models (API contract)
│   │   ├── generators/
│   │   │   ├── question_generator.py      # All question generators
│   │   │   └── personalized_generator.py  # NEW! Questionnaire-based questions
│   │   ├── parsers/
│   │   │   └── imessage_parser.py   # Parse iMessage chat data
│   │   └── routes/
│   │       ├── admin.py             # Admin endpoints
│   │       ├── game.py              # Game API endpoints
│   │       └── main.py              # Frontend routes, WebSocket events
│   └── database/
│       └── trivia.db                # iMessage database
├── frontend/
│   ├── static/
│   │   ├── css/style.css            # All styling
│   │   └── js/
│   │       ├── app.js               # Shared utilities, API wrapper
│   │       ├── host.js              # Host dashboard logic
│   │       └── player.js            # Player dashboard logic
│   └── templates/
│       ├── index.html               # Landing page
│       ├── host.html                # Host view
│       ├── player.html              # Player view
│       ├── join.html                # Join game page
│       └── admin.html               # Admin panel
├── friend_group_data.csv            # Questionnaire data (personalized questions)
├── requirements.txt                 # Python dependencies
├── run_server.py                    # Server entry point
└── README.md                        # Setup and usage guide
```

## Archive (Reference Only)

```
archive/
├── audit_logs/                      # Game audit JSON files
│   └── game_audit_*.json           # 24 simulation runs
├── docs/                            # Documentation
│   ├── API_DOCUMENTATION.md
│   ├── DEBUGGING_GUIDE.md
│   ├── FINAL_STATUS.md
│   ├── FIX_SUMMARY.md
│   ├── GAME_AUDIT_REPORT.md
│   └── PLAYER_QUESTIONNAIRE.md
├── test_scripts/                    # Test suites
│   ├── test_*.py
│   ├── run_tests.py
│   └── validate_*.py
├── demo_scripts/                    # Demo and utility scripts
│   ├── authentic_1280_questions.py
│   ├── full_game_simulation.py
│   ├── preview_questions.py
│   └── [20+ other scripts]
├── chat.db                          # Sample iMessage export
├── debug_lobby.html                 # Debug tools
└── test_frontend.html
```

## To Run the Game

```bash
# Install dependencies
pip install -r requirements.txt

# Start server
python3 run_server.py

# Visit
http://localhost:5001
```

## Question Distribution (15-question game)

- 6 Regular Trivia (40%)
- 3 Sex Trivia (20%)
- 3 Most Likely (20%)
- 1 Receipt from chats (7%)
- 1 Personalized question (7%)
- 1 Poll question (7%)

## New Features (Latest)

### ✅ Poll Questions
- Vote-based "Who's most likely" questions
- Winner = most votes (150 + 25*votes points)
- Gold UI styling for winners

### ✅ Personalized Questions (NEW!)
- Generated from friend_group_data.csv
- Uses roasts, rankings, confessions, custom trivia
- Adds massive variety and personalization

### ✅ Game Stats Fix
- Auto-detects finished status
- No extra "Next" button needed

### ✅ Duplicate Prevention
- All generators track used questions
- Maximum variety across games

## Data Sources

1. **iMessage Chats** → Receipt questions (1,650 messages)
2. **Questionnaire** → Personalized questions (friend_group_data.csv)
3. **Static Pools** → Trivia, roasts, most likely, polls

## Next Steps

1. Collect more questionnaire responses (1 person → 4 people)
2. Each new response adds ~20 unique personalized questions
3. More responses = exponentially more variety!
