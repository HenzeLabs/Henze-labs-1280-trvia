# 🎨 UI Tour Guide - Visual Inspection Mode

This guide shows you how to use the UI tour test to inspect and adjust every screen in your trivia game.

## What is the UI Tour?

The UI tour is a special Playwright test that **pauses at each screen** so you can:
- 🔍 Inspect elements with browser DevTools
- 🎨 Make CSS adjustments and see them live
- 📸 Take screenshots
- ✏️ Modify HTML/styles in the browser
- ▶️ Resume to see the next screen

## Prerequisites

⚠️ **CRITICAL: Start your server first!**

```bash
# Terminal 1: Start the server
python run_server.py

# Wait for: "Running on http://localhost:5001"
```

Or with virtual environment:
```bash
source venv/bin/activate && python run_server.py
```

**Keep this terminal running** and open a **new terminal** for tests.

## Quick Start

### Run the Complete UI Tour (All 11 Screens)

```bash
npx playwright test ui-tour.spec.ts --headed --debug
```

This will show you:
1. 🏠 Home page
2. 📺 TV waiting/lobby (empty)
3. 📱 Join page (player phone)
4. 🎮 Player lobby waiting screen
5. 📺 TV updated (1 player joined)
6. 🎯 Question screen (TV view)
7. 📱 Question screen (player view)
8. ✅ Answer submitted state
9. ⏭️ Auto-advance to next question
10. 🏆 Final results screen
11. 📺 TV final state

### Run Quick Lobby Tour (Focus on Waiting States)

```bash
npx playwright test ui-tour.spec.ts -g "Quick lobby tour"
```

This shows:
- TV with 0 players
- TV with 1 player
- TV with 2 players

## How to Use During the Tour

### When Test Pauses

1. **Browser window opens automatically** in headed mode
2. **Console shows guidance** like:
   ```
   ✋ PAUSED - Inspecting HOME PAGE
      - Check button styles
      - Verify Netflix aesthetic
      - Test responsive layout
   ```
3. **Playwright Inspector appears** - you can:
   - Click "Resume" to continue
   - Click "Step over" to go through code line by line
   - Close inspector to end test

### Making Live Changes

**In the browser window (while paused):**
1. Right-click → Inspect Element
2. Edit CSS in DevTools Styles panel
3. Changes apply immediately
4. Take notes of what works
5. Click "Resume" in Playwright Inspector

**Example: Adjusting Button Style**
```css
/* In DevTools, try: */
#create-game-btn {
  font-size: 18px;        /* Bigger text */
  padding: 20px 40px;     /* More padding */
  border-radius: 12px;    /* Rounder corners */
}
```

### Testing Responsive Design

**Change viewport size:**
1. In browser DevTools: Toggle device toolbar (Cmd+Shift+M / Ctrl+Shift+M)
2. Select iPhone 12, iPad, or custom dimensions
3. See how your design responds
4. Resume test to see on different screens

## Screens Reference

### 🏠 Screen 1: Home Page
**File:** `frontend/templates/index.html`
**What to check:**
- Button hover states
- Typography hierarchy
- Spacing and alignment
- Mobile responsiveness

### 📺 Screen 2: TV Lobby
**File:** `frontend/templates/tv.html`
**What to check:**
- Room code visibility (needs to be BIG)
- Player count display
- Start button states (disabled/enabled)
- Background styling

### 📱 Screen 3: Join Page
**File:** `frontend/templates/join.html`
**What to check:**
- Input field sizes (touch-friendly?)
- Keyboard accessibility
- Error message styling
- Mobile layout

### 🎮 Screen 4: Player Lobby
**File:** `frontend/templates/player.html` (waiting-screen section)
**What to check:**
- Room code display
- Waiting message
- Loading indicators
- Player status

### 🎯 Screen 5-6: Question Screens
**Files:**
- TV: `frontend/templates/tv.html` (question section)
- Player: `frontend/templates/player.html` (question-screen section)

**What to check:**
- Question text size (readable from couch for TV?)
- Answer button sizes (thumb-friendly for mobile?)
- Category badge styling
- Timer display
- Answer highlight on hover

### ✅ Screen 7: Answer Submitted
**File:** `frontend/templates/player.html` (waiting-next section)
**What to check:**
- Confirmation message
- Waiting indicator
- Disabled state styling

### 🏆 Screen 10: Final Results
**File:** `frontend/templates/player.html` (final-results section)
**What to check:**
- Leaderboard layout
- Score display prominence
- Rank highlighting
- Winner celebration

## Running Specific Screens Only

Want to focus on just one screen? Modify the test:

```typescript
// Comment out sections you don't want to see
test("Custom tour - questions only", async ({ browser }) => {
  // ... setup code ...

  await createGame(tvPage);
  await joinGame(playerPage, roomCode, "Test");
  await startGame(tvPage);

  // PAUSE HERE - inspect question screen
  await tvPage.pause();
  await playerPage.pause();
});
```

## Tips & Tricks

### 1. Take Screenshots at Each Pause
```bash
# In Playwright Inspector, click camera icon
# Or use browser DevTools screenshot tool
```

### 2. Test Different Question Types
The tour uses real generated questions, so each run may show different content types.

### 3. Test Multiple Screen Sizes
```typescript
// Add custom viewports
const tvPage = await tvContext.newPage({
  viewport: { width: 1920, height: 1080 }
});

const playerPage = await playerContext.newPage({
  viewport: { width: 390, height: 844 } // iPhone 12
});
```

### 4. Compare TV vs Player Side-by-Side
Position browser windows side-by-side to compare simultaneously.

### 5. Record Issues
Keep the console output open - it shows which screen you're on.

## Common Adjustments

### Make Room Code Bigger on TV
```css
/* tv.html - .tv-room-code */
.tv-room-code {
  font-size: 120px;  /* Was 72px */
  font-weight: 900;
}
```

### Make Answer Buttons Touch-Friendly
```css
/* player.html - .answer-button */
.answer-button {
  min-height: 64px;  /* Apple's recommended touch target */
  font-size: 18px;
  padding: 20px;
}
```

### Improve Question Readability
```css
/* tv.html - .tv-question-text */
.tv-question-text {
  font-size: 64px;   /* Was 56px */
  line-height: 1.3;  /* Tighter line height */
  max-width: 90%;    /* Don't stretch too wide */
}
```

## Stopping the Tour

**Three ways to exit:**
1. Let it complete (runs through all screens)
2. Close Playwright Inspector window
3. Press Ctrl+C in terminal

## Running Without Pauses (Normal Test)

To run the same flow without pauses (for CI/automated testing):

```bash
# Remove --debug flag
npx playwright test ui-tour.spec.ts --headed
```

The test will run through all screens automatically.

## Next Steps After Tour

1. **Note down CSS changes** you made during inspection
2. **Apply changes** to actual template files
3. **Run regular tests** to ensure nothing broke:
   ```bash
   npx playwright test
   ```
4. **Commit changes** with descriptive messages

## Troubleshooting

**Browser doesn't open?**
- Make sure you used `--headed` flag
- Try `--headed --debug` together

**Inspector doesn't appear?**
- Make sure you used `--debug` flag
- Try `PWDEBUG=1 npx playwright test ui-tour.spec.ts`

**Test times out?**
- Default timeout is 10 minutes per test
- That's plenty of time for inspection
- If you need more, edit `test.setTimeout(600000)` in the test file

**Changes don't persist?**
- DevTools changes are temporary (browser memory only)
- Copy CSS to actual files: `frontend/templates/*.html` or `frontend/static/css/*.css`

## Pro Tips

🎨 **Use DevTools' "Copy styles"** - Right-click element → Copy → Copy styles
📸 **Screenshot everything** - Document before/after for comparison
🔄 **Run tour multiple times** - Questions are random, see variety
👥 **Compare with friends** - Different perspectives catch different issues
📱 **Test on real phone** - Use phone browser to join game during tour

---

**Need help?** Check the test code in `tests/ui-tour.spec.ts` for more details.
