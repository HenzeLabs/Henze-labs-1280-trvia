# 1280 Trivia

A Jackbox-style trivia game that parses iMessage chat data to generate roast-style questions for your friends at 1280 West Condos.

Tech stack

- Python (Flask)
- Flask-SocketIO (WebSockets)
- SQLite
- HTML/CSS/JS frontend (simple)

Quick start (macOS / zsh)

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
python -m backend.app.run
```

Notes

- The iMessage parser expects a local `chat.db` at the path configured in `backend/app/config.py` (default: `~/Library/Messages/chat.db`). MacOS stores iMessage data in that path, but permissions and SIP may prevent access—you may need to export or copy the DB to a working location.
- The admin panel provides endpoints to parse chats and generate questions from stored messages.

Next steps you can ask me to do now

- Parse specific chats and import messages into the DB
- Generate a question set from your chat data
- Start the local dev server and test the flow
- Add a custom question editor UI

Security & ethics

- The generator filters and composes questions to avoid sharing private details. Review generated questions before playing with strangers.
