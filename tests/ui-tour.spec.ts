/**
 * 🎨 UI Tour - Visual inspection test with pauses at each screen
 *
 * Run with: npx playwright test ui-tour.spec.ts --headed --debug
 *
 * This test pauses at each major screen so you can:
 * - Inspect elements in the browser DevTools
 * - Make CSS/HTML adjustments
 * - Take screenshots
 * - Resume to see the next screen
 */

import { test, expect, Page } from "@playwright/test";
import {
  createGame,
  joinGame,
  startGame,
  answerQuestion,
  waitForNextQuestion,
  getCurrentQuestion,
} from "./support/test-utils";

const shouldPauseForUITour = process.env.CI !== "true";

async function maybePause(page: Page) {
  if (shouldPauseForUITour) {
    await page.pause();
  } else {
    await page.waitForTimeout(500);
  }
}

test.describe.configure({ mode: "serial" }); // Run tests in order

test.describe("🎨 UI Visual Tour", () => {
  test.setTimeout(600000); // 10 minutes - plenty of time for inspection

  test("Complete UI tour - all screens and states", async ({ browser }) => {
    const tvContext = await browser.newContext();
    const playerContext = await browser.newContext();

    const tvPage = await tvContext.newPage();
    const playerPage = await playerContext.newPage();

    try {
      // ========================================
      // 🏠 SCREEN 1: Home Page
      // ========================================
      console.log("\n🏠 SCREEN 1: Home Page");
      await tvPage.goto("/");
      await tvPage.waitForLoadState("networkidle");

      console.log("✋ PAUSED - Inspecting HOME PAGE");
      console.log("   - Check button styles");
      console.log("   - Verify Netflix aesthetic");
      console.log("   - Test responsive layout");
      await maybePause(tvPage);

      // ========================================
      // 📺 SCREEN 2: TV Waiting/Lobby Screen
      // ========================================
      console.log("\n📺 SCREEN 2: TV Waiting/Lobby Screen");
      const roomCode = await createGame(tvPage);

      console.log("✋ PAUSED - Inspecting TV LOBBY");
      console.log(`   - Room Code: ${roomCode}`);
      console.log("   - Check room code display");
      console.log("   - Verify start button (should be disabled)");
      console.log("   - Check player count (should be 0)");
      await maybePause(tvPage);

      // ========================================
      // 📱 SCREEN 3: Join Page (Player Phone)
      // ========================================
      console.log("\n📱 SCREEN 3: Join Page");
      await playerPage.goto("/join");
      await playerPage.waitForLoadState("networkidle");

      console.log("✋ PAUSED - Inspecting JOIN PAGE");
      console.log("   - Check input field styles");
      console.log("   - Verify mobile-friendly layout");
      console.log("   - Test form validation");
      await maybePause(playerPage);

      // ========================================
      // 🎮 SCREEN 4: Player Lobby (Waiting)
      // ========================================
      console.log("\n🎮 SCREEN 4: Player Lobby (Waiting)");
      await joinGame(playerPage, roomCode, "UI Test Player");

      console.log("✋ PAUSED - Inspecting PLAYER LOBBY");
      console.log(`   - Room Code Display: ${roomCode}`);
      console.log("   - Check waiting screen styling");
      console.log("   - Verify room code visibility");
      await maybePause(playerPage);

      // Check TV updated with player count
      console.log("✋ PAUSED - Check TV UPDATED with player");
      console.log("   - Player count should show 1");
      console.log("   - Start button should be enabled");
      await maybePause(tvPage);

      // ========================================
      // 🎯 SCREEN 5: Question Screen (TV)
      // ========================================
      console.log("\n🎯 SCREEN 5: Question Screen - TV View");
      await startGame(tvPage);

      const tvQuestion = await tvPage.getByTestId("question-text").textContent();
      console.log("✋ PAUSED - Inspecting QUESTION on TV");
      console.log(`   - Question: ${tvQuestion}`);
      console.log("   - Check question text size/readability");
      console.log("   - Verify answer display");
      console.log("   - Check category badge");
      await maybePause(tvPage);

      // ========================================
      // 📱 SCREEN 6: Question Screen (Player Phone)
      // ========================================
      console.log("\n📱 SCREEN 6: Question Screen - Player View");
      await expect(playerPage.getByTestId("question-text")).toBeVisible();

      const playerQuestion = await playerPage.getByTestId("question-text").textContent();
      console.log("✋ PAUSED - Inspecting QUESTION on PLAYER");
      console.log(`   - Question: ${playerQuestion}`);
      console.log("   - Check mobile question layout");
      console.log("   - Verify answer button styles");
      console.log("   - Test touch-friendly sizes");
      await maybePause(playerPage);

      // ========================================
      // ✅ SCREEN 7: Answer Submitted (Player)
      // ========================================
      console.log("\n✅ SCREEN 7: Answer Submitted State");
      await answerQuestion(playerPage, 0);

      console.log("✋ PAUSED - Inspecting ANSWER SUBMITTED");
      console.log("   - Check submitted state styling");
      console.log("   - Verify waiting message");
      console.log("   - Check for feedback indicators");
      await maybePause(playerPage);

      // ========================================
      // ⏭️ SCREEN 8: Auto-Advance to Next Question
      // ========================================
      console.log("\n⏭️ SCREEN 8: Auto-Advance Transition");
      const firstQuestion = await getCurrentQuestion(playerPage);
      await waitForNextQuestion(playerPage, firstQuestion, 20000);

      const secondQuestion = await getCurrentQuestion(playerPage);
      console.log("✋ PAUSED - Inspecting NEXT QUESTION");
      console.log(`   - Previous: ${firstQuestion?.substring(0, 50)}...`);
      console.log(`   - Current: ${secondQuestion?.substring(0, 50)}...`);
      console.log("   - Check transition smoothness");
      console.log("   - Verify question counter updated");
      await maybePause(playerPage);

      // ========================================
      // 🎊 SCREEN 9: Answer Multiple Questions
      // ========================================
      console.log("\n🎊 Answering remaining questions...");
      for (let i = 2; i <= 10; i++) {
        console.log(`   Answering question ${i}/10...`);
        const currentQ = await getCurrentQuestion(playerPage);
        await answerQuestion(playerPage, 0);

        if (i < 10) {
          await waitForNextQuestion(playerPage, currentQ, 15000);
        }
      }

      // ========================================
      // 🏆 SCREEN 10: Final Results
      // ========================================
      console.log("\n🏆 SCREEN 10: Final Results");
      await expect(playerPage.getByTestId("final-results")).toBeVisible({ timeout: 20000 });

      console.log("✋ PAUSED - Inspecting FINAL RESULTS");
      console.log("   - Check leaderboard styling");
      console.log("   - Verify score display");
      console.log("   - Check final rank");
      console.log("   - Test results layout");
      await maybePause(playerPage);

      // ========================================
      // 📺 SCREEN 11: TV Final State
      // ========================================
      console.log("\n📺 SCREEN 11: TV Final State");
      console.log("✋ PAUSED - Inspecting TV END STATE");
      console.log("   - Check TV final screen");
      console.log("   - Verify leaderboard on TV");
      await maybePause(tvPage);

      console.log("\n✅ UI TOUR COMPLETE!");
      console.log("All screens have been inspected.");

    } finally {
      await tvPage.close();
      await playerPage.close();
      await tvContext.close();
      await playerContext.close();
    }
  });

  test("Quick lobby tour - focus on waiting states", async ({ browser }) => {
    const tvContext = await browser.newContext();
    const player1Context = await browser.newContext();
    const player2Context = await browser.newContext();

    const tvPage = await tvContext.newPage();
    const player1Page = await player1Context.newPage();
    const player2Page = await player2Context.newPage();

    try {
      // Create game
      const roomCode = await createGame(tvPage);

      console.log("\n📺 TV with 0 players");
      console.log("✋ PAUSED - Check empty lobby state");
      await maybePause(tvPage);

      // First player joins
      await joinGame(player1Page, roomCode, "Player 1");

      console.log("\n👤 TV with 1 player");
      console.log("✋ PAUSED - Check 1-player lobby state");
      await maybePause(tvPage);

      // Second player joins
      await joinGame(player2Page, roomCode, "Player 2");

      console.log("\n👥 TV with 2 players");
      console.log("✋ PAUSED - Check 2-player lobby state");
      console.log("   - Verify both players shown");
      console.log("   - Check player list styling");
      await maybePause(tvPage);

      console.log("\n✅ LOBBY TOUR COMPLETE!");

    } finally {
      await tvPage.close();
      await player1Page.close();
      await player2Page.close();
      await tvContext.close();
      await player1Context.close();
      await player2Context.close();
    }
  });
});
