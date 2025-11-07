# 1280 Trivia

**🎮 PRODUCT BRANCH** - Clean version for public deployment

A Jackbox-style trivia game with personalized questions powered by pre-game surveys.

---

## 🎯 What Makes This Different?

Unlike generic party games, this lets friend groups create **personalized roasts and inside jokes** through a pre-game survey system. Mix custom questions with regular trivia for the perfect game night.

---

**All future UI and animation layers must consume data conforming to `v1-api-contract-stable`.**

The API contract is **FROZEN** at version v1.0.0 as of November 4, 2025. Backend schema changes require explicit version bump and migration plan. See `/docs/api_contract.md` for complete specification.

**Breaking changes to API endpoints, WebSocket events, or data models are PROHIBITED without major version increment.**

## Tech stack

- Python (Flask)
- Flask-SocketIO (WebSockets)
- SQLite
- HTML/CSS/JS frontend (simple)

## Quick start (macOS / zsh)

1. Create and activate a virtualenv (optional but recommended):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. (Optional) Set `IMESSAGE_DB_PATH` environment variable to point to your iMessage chat database if not using the default in `backend/app/config.py`.

4. Initialize the SQLite DB and run the app:

```bash
python -c "from backend.app.models import Database; Database('backend/database/trivia.db')"
# Run the Flask-SocketIO server (development)
python run_server.py
```

## Game Status

✅ **Core Logic**: Complete and validated (v1-core-logic-stable)  
✅ **Real-time Layer**: Complete and validated (v1.1-realtime-complete)  
✅ **API Contract**: Frozen and documented (v1-api-contract-stable)

**Ready for production use** - All core functionality validated through comprehensive test suite.

## API Documentation

- 📋 **Contract Specification**: `/docs/api_contract.md` - Complete API documentation
- 📦 **JSON Schema**: `/docs/api_schema.json` - Machine-readable validation schemas
- 🧪 **Test Suite**: Run `python run_tests.py` for full validation

## Notes

- The iMessage parser expects a local `chat.db` at the path configured in `backend/app/config.py` (default: `~/Library/Messages/chat.db`). MacOS stores iMessage data in that path, but permissions and SIP may prevent access—you may need to export or copy the DB to a working location.
- The admin panel provides endpoints to parse chats and generate questions from stored messages.

## Next steps you can ask me to do now

- Parse specific chats and import messages into the DB
- Generate a question set from your chat data
- Start the local dev server and test the flow
- Add a custom question editor UI

## Security & ethics

- The generator filters and composes questions to avoid sharing private details. Review generated questions before playing with strangers.
