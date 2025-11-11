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
│   ├── global-setup.ts      # Global test initialization
│   └── test-utils.ts        # Reusable test utilities
├── complete-game-flow.spec.ts   # Full game flow tests
└── simplified-game-flow.spec.ts # Quick smoke tests
```

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

## Debugging

1. **Screenshots**: Automatically captured on failure in `test-results/`
2. **Traces**: View with `npx playwright show-trace trace.zip`
3. **Video**: Enable in `playwright.config.ts` if needed

## Tips

- Use `page.pause()` to debug interactively
- Check `test-results/` for failure screenshots
- Use `--headed` flag to see browser during test execution
- Use `test.only()` to run a single test
