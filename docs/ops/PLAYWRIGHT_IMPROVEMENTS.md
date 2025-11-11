# Playwright Test Suite Improvements

## ✅ Completed Enhancements

### 1. Environment Variable Configuration
- **Added**: `.env.test` for configurable test settings
- **Benefit**: No more hardcoded URLs - easy to switch between local/staging/production
- **Usage**:
  ```env
  PLAYWRIGHT_BASE_URL=http://localhost:5001
  FLASK_PORT=5001
  TEST_TIMEOUT=30000
  ```

### 2. Stable Test Selectors with `data-testid`
- **Added**: `testIdAttribute: "data-testid"` in Playwright config
- **Implemented**: Test IDs across all key UI elements
- **Benefit**: Tests won't break when CSS classes or text changes

**Test IDs Added:**
- Home: `create-game-btn`, `join-game-link`
- Join: `room-code-input`, `player-name-input`, `join-game-btn`
- Player: `waiting-screen`, `start-game-btn`, `question-text`, `answer-0/1/2/3`
- TV: `tv-room-code`, `tv-waiting`, `all-answered-banner`

### 3. Global Setup & Test Utilities
- **Created**: `tests/support/global-setup.ts` for pre-test initialization
- **Created**: `tests/support/test-utils.ts` with reusable helpers:
  - `createGame()` - Start new game, return room code
  - `joinGame()` - Join as player
  - `startGame()` - Begin gameplay
  - `answerQuestion()` - Submit answer
  - `waitForWebSocket()` - Wait for connection
  - Many more...

### 4. Multi-Device Testing
- **Added**: Mobile Safari project for cross-browser confidence
- **Projects**:
  - `chromium-desktop` - Desktop Chrome (1920x1080)
  - `chromium-tablet` - Tablet (1180x820)
  - `chromium-low-end` - Low-end simulation
  - `mobile-safari` - iPhone 12

### 5. CI/CD Optimizations
- **Workers**: Parallel execution in CI (2 workers), sequential locally
- **Retries**: Auto-retry on failure in CI environments
- **Server**: `reuseExistingServer: !process.env.CI` for faster local dev

### 6. Improved Test Organization
- **Created**: Comprehensive test utilities
- **Created**: Complete game flow tests with utilities
- **Created**: Test README documentation

## 🎯 Test Architecture

```
tests/
├── support/
│   ├── global-setup.ts      # Pre-test initialization
│   └── test-utils.ts        # Reusable helpers
├── complete-game-flow.spec.ts   # Full game scenarios
└── simplified-game-flow.spec.ts # Quick smoke tests

playwright.config.ts           # Main config with env vars
.env.test                     # Environment configuration
```

## 📊 Benefits

### Before:
```typescript
// Brittle selectors
await page.click('#create-game-btn');
await page.fill('#room-code', roomCode);
```

### After:
```typescript
// Stable, semantic selectors
await page.getByTestId('create-game-btn').click();
await page.getByTestId('room-code-input').fill(roomCode);

// Or use utilities
const roomCode = await createGame(page);
await joinGame(page, roomCode, "Player 1");
```

## 🚀 Running Tests

```bash
# Run all tests
npx playwright test

# Run specific browser
npx playwright test --project=mobile-safari

# Debug mode
npx playwright test --debug

# UI mode (interactive)
npx playwright test --ui

# View report
npx playwright show-report
```

## 📝 Writing New Tests

```typescript
import { test, expect } from "@playwright/test";
import { createGame, joinGame, startGame } from "./support/test-utils";

test("game flow", async ({ browser }) => {
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    // Clean, readable test code
    const roomCode = await createGame(page);
    await joinGame(page, roomCode, "Test Player");
    await startGame(page);

    // Stable selectors
    await expect(page.getByTestId("question-text")).toBeVisible();
  } finally {
    await page.close();
    await context.close();
  }
});
```

## 🔧 Configuration

**Local Development:**
- Sequential execution (workers: 1)
- Reuses existing server
- No retries

**CI Environment:**
- Parallel execution (workers: 2)
- Fresh server per run
- Auto-retry on failure (2 attempts)

## 📚 Documentation

- **Test README**: `tests/README.md` - Complete testing guide
- **Test Utils**: Fully documented helper functions
- **Config**: Environment variables explained in `.env.test`

## 🎨 Best Practices Implemented

1. ✅ **Stable Selectors**: Using `data-testid` instead of CSS classes
2. ✅ **DRY Principle**: Reusable utilities for common actions
3. ✅ **Isolation**: Each test uses separate browser contexts
4. ✅ **Cleanup**: Proper teardown in finally blocks
5. ✅ **Debugging**: Screenshots on failure, trace on retry
6. ✅ **Cross-Platform**: Tests on desktop, tablet, and mobile
7. ✅ **Environment Agnostic**: Configurable base URLs
8. ✅ **CI-Ready**: Optimized for continuous integration

## 🔮 Future Enhancements (Optional)

- [ ] Visual regression testing with Percy/Chromatic
- [ ] Performance budgets (page load < 2s, etc.)
- [ ] Accessibility testing (axe-core integration)
- [ ] Network mocking for offline scenarios
- [ ] Database seeding in global-setup
- [ ] Parallel test isolation with unique room codes

## 📞 Support

Run into issues? Check:
1. `tests/README.md` - Comprehensive testing guide
2. Test results in `test-results/` directory
3. Playwright docs: https://playwright.dev
