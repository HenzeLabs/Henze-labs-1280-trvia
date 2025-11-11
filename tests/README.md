# Playwright Test Suite

Comprehensive end-to-end tests for 1280 Trivia game.

## Setup

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Install Playwright browsers:**
   ```bash
   npx playwright install
   ```

3. **Configure environment (optional):**
   Edit `.env.test` to customize test settings:
   ```env
   PLAYWRIGHT_BASE_URL=http://localhost:5001
   FLASK_PORT=5001
   TEST_TIMEOUT=30000
   ```

## Running Tests

### Run all tests:
```bash
npx playwright test
```

### Run specific test file:
```bash
npx playwright test complete-game-flow.spec.ts
```

#### Capture four-player screenshot flow
```bash
npx playwright test four-player-screenshot.spec.ts --project=chromium-desktop
```

This test spins up the TV plus four player browsers, plays through an entire game, and saves staged screenshots for every question (TV + each player) inside `test-results/screenshots/`. It also writes a structured log of every action, network request, and console message to `test-results/logs/`.

### Run with UI mode (interactive):
```bash
npx playwright test --ui
```

### Run on specific browser:
```bash
npx playwright test --project=chromium-desktop
npx playwright test --project=mobile-safari
```

### Debug mode:
```bash
npx playwright test --debug
```

### View test report:
```bash
npx playwright show-report
```

## Test Structure

```
tests/
├── support/
│   ├── global-setup.ts           # Global test initialization
│   ├── test-utils.ts             # Reusable test utilities
│   └── sessionLogger.ts          # Auto-archiving for screenshots
├── ui-tour.spec.ts               # CI-friendly visual tour (13 screenshots)
├── four-player-screenshot.spec.ts # Manual inspection (multi-device)
├── full-game-validation.spec.ts  # End-to-end smoke test (10 questions)
├── complete-game-flow.spec.ts    # Legacy full flow tests
└── simplified-game-flow.spec.ts  # Legacy smoke tests
```

### Test Categories

**CI Tests (Run Automatically)**:
- `ui-tour.spec.ts` - Production visual regression (45s)
- `full-game-validation.spec.ts` - End-to-end smoke test (90s)

**Manual Tests (Local Only)**:
- `four-player-screenshot.spec.ts` - Multi-device layout validation (60s)

## Test Utilities

Import from `./support/test-utils`:

```typescript
import {
  createGame,           // Create new game and return room code
  joinGame,            // Join game as player
  startGame,           // Start game (creator only)
  answerQuestion,      // Submit an answer
  waitForWebSocket,    // Wait for WebSocket connection
  getCurrentQuestion,  // Get current question text
  getPlayerScore      // Get player's score
} from "./support/test-utils";
```

## Test ID Selectors

All interactive elements have `data-testid` attributes for stable selectors:

### Home Page
- `create-game-btn` - Create game button
- `join-game-link` - Join game link

### Join Page
- `room-code-input` - Room code input field
- `player-name-input` - Player name input
- `join-game-btn` - Join button
- `join-error` - Error message

### Player Page
- `waiting-screen` - Lobby waiting screen
- `room-code-display` - Room code display
- `start-game-btn` - Start button (creator only)
- `question-screen` - Question display
- `question-text` - Question text
- `question-category` - Category badge
- `time-remaining` - Timer
- `answer-0`, `answer-1`, etc. - Answer buttons
- `answer-submitted` - Answer submitted screen
- `final-results` - Final results screen
- `final-score` - Player's final score

### TV Page
- `tv-room-code` - Room code on TV
- `tv-waiting` - Waiting screen
- `tv-current-question` - Current question number
- `all-answered-banner` - All players answered banner

## Writing New Tests

### Example Test:
```typescript
import { test, expect } from "@playwright/test";
import { createGame, joinGame, startGame } from "./support/test-utils";

test("my custom test", async ({ browser }) => {
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    // Use utilities
    const roomCode = await createGame(page);

    // Use test IDs
    await expect(page.getByTestId("tv-room-code")).toHaveText(roomCode);

    // Your test logic...
  } finally {
    await page.close();
    await context.close();
  }
});
```

## Test Projects

- **chromium-desktop** - Desktop Chrome (1920x1080)
- **chromium-tablet** - Tablet viewport (1180x820)
- **chromium-low-end** - Low-end device simulation
- **mobile-safari** - iPhone 12 Safari

## CI/CD

Tests are configured to run in parallel in CI with 2 workers and automatic retries.

Set `CI=true` environment variable to enable CI mode:
```bash
CI=true npx playwright test
```

## Screenshot Organization

### Active Screenshots (Checked into Git)
```
test-results/
├── 01-home-page.png
├── 02-tv-lobby-empty.png
├── 03-join-page.png
├── 04-player-lobby-waiting.png
├── 05-tv-lobby-with-player.png
├── 06-tv-question-screen.png
├── 07-player-question-screen.png
├── 08-player-answer-submitted.png
├── 09-tv-answer-results.png
├── 10-player-mid-game-q5.png
├── 11-tv-mid-game-q5.png
├── 12-player-final-results.png
└── 13-tv-final-leaderboard.png
```

### Ephemeral Screenshots (Gitignored)
- `test-results/screenshots/` - Per-run captures with timestamps
- `test-results/logs/` - Session debug logs

### Archived (Gitignored after 14 days)
- `test-results/archive/ui_tour_YYYY-MM-DD/` - Archived tours
- Run `scripts/cleanup-test-results.sh` to remove old artifacts

## Known Test Issues

See [docs/audits/KNOWN_ISSUES.md](../docs/audits/KNOWN_ISSUES.md) for bugs that may affect tests:
- **Issue #1**: Poll questions may show 0 points
- **Issue #2**: Timer accumulation on reconnect
- **Issue #6**: Player rank shows "-" instead of position

## Debugging

1. **Screenshots**: Automatically captured on failure in `test-results/`
2. **Traces**: View with `npx playwright show-trace trace.zip`
3. **Video**: Enable in `playwright.config.ts` if needed
4. **Server Logs**: Check `/tmp/trivia_sim.log` for backend issues

### Common Issues

**Test times out waiting for question**:
```bash
# Check server logs
tail -f /tmp/trivia_sim.log

# Verify auto-advance is running
curl http://localhost:5001/api/game/stats/<room_code>
```

**Server not starting**:
```bash
# Kill orphaned processes
pkill -f "python.*run_server.py"

# Restart server
python run_server.py
```

## Tips

- Use `page.pause()` to debug interactively
- Check `test-results/` for failure screenshots
- Use `--headed` flag to see browser during test execution
- Use `test.only()` to run a single test
- Mark manual tests with `.skip(process.env.CI === 'true')` for local-only execution
