/**
 * 📸 UI Screenshot Tour - Automated visual documentation
 *
 * Run with: npx playwright test ui-screenshot-tour.spec.ts --headed
 *
 * This test automatically captures screenshots of all screens:
 * - No pausing required
 * - Screenshots saved to test-results/
 * - Fast and automated
 */

import { test, expect } from "@playwright/test";
import {
  createGame,
  joinGame,
  startGame,
  answerQuestion,
  waitForNextQuestion,
  getCurrentQuestion,
} from "./support/test-utils";

test.describe.configure({ mode: "serial" });

test.describe("📸 UI Screenshot Tour", () => {
  test.setTimeout(300000); // 5 minutes

  test("Capture all UI screens", async ({ browser }) => {
    const tvContext = await browser.newContext({
      viewport: { width: 1280, height: 720 },
    });
    const playerContext = await browser.newContext({
      viewport: { width: 375, height: 812 }, // iPhone size
    });

    const tvPage = await tvContext.newPage();
    const playerPage = await playerContext.newPage();

    try {
      // ========================================
      // 🏠 SCREEN 1: Home Page
      // ========================================
      console.log("\n📸 Capturing SCREEN 1: Home Page");
      await tvPage.goto("/");
      await tvPage.waitForLoadState("networkidle");
      await tvPage.screenshot({ path: "test-results/01-home-page.png", fullPage: true });

      // ========================================
      // 📺 SCREEN 2: TV Lobby
      // ========================================
      console.log("📸 Capturing SCREEN 2: TV Lobby");
      const roomCode = await createGame(tvPage);
      await tvPage.screenshot({ path: "test-results/02-tv-lobby-empty.png", fullPage: true });

      // ========================================
      // 📱 SCREEN 3: Join Page
      // ========================================
      console.log("📸 Capturing SCREEN 3: Join Page");
      await playerPage.goto("/join");
      await playerPage.waitForLoadState("networkidle");
      await playerPage.screenshot({ path: "test-results/03-join-page.png", fullPage: true });

      // ========================================
      // 🎮 SCREEN 4: Player Lobby
      // ========================================
      console.log("📸 Capturing SCREEN 4: Player Lobby");
      await joinGame(playerPage, roomCode, "UI Test Player");
      await playerPage.screenshot({ path: "test-results/04-player-lobby-waiting.png", fullPage: true });

      // TV updated with player
      console.log("📸 Capturing TV with 1 player");
      await tvPage.screenshot({ path: "test-results/05-tv-lobby-with-player.png", fullPage: true });

      // ========================================
      // 🎯 SCREEN 5: Question on TV
      // ========================================
      console.log("📸 Capturing SCREEN 5: Question on TV");
      await startGame(tvPage);
      await tvPage.waitForTimeout(1000); // Wait for animation
      await tvPage.screenshot({ path: "test-results/06-tv-question-screen.png", fullPage: true });

      // ========================================
      // 📱 SCREEN 6: Question on Player
      // ========================================
      console.log("📸 Capturing SCREEN 6: Question on Player");
      await expect(playerPage.getByTestId("question-text")).toBeVisible({ timeout: 10000 });
      await playerPage.waitForTimeout(500);
      await playerPage.screenshot({ path: "test-results/07-player-question-screen.png", fullPage: true });

      // ========================================
      // ✅ SCREEN 7: Answer Submitted
      // ========================================
      console.log("📸 Capturing SCREEN 7: Answer Submitted");
      await answerQuestion(playerPage, 0);
      await playerPage.waitForTimeout(500);
      await playerPage.screenshot({ path: "test-results/08-player-answer-submitted.png", fullPage: true });

      // ========================================
      // 📊 SCREEN 8: TV Showing Answers
      // ========================================
      console.log("📸 Capturing SCREEN 8: TV with answers");
      await tvPage.waitForTimeout(1000);
      await tvPage.screenshot({ path: "test-results/09-tv-answer-results.png", fullPage: true });

      // ========================================
      // 🎊 Answer Remaining Questions
      // ========================================
      console.log("\n🎊 Answering remaining questions (2-10)...");
      let previousQ = await getCurrentQuestion(playerPage);

      for (let i = 2; i <= 10; i++) {
        try {
          console.log(`   Question ${i}/10...`);

          // Wait for next question to appear
          try {
            await waitForNextQuestion(playerPage, previousQ, 20000);
          } catch (e) {
            console.log(`   ⚠️ Timeout waiting for question ${i}, continuing...`);
          }

          // Get the new question text
          previousQ = await getCurrentQuestion(playerPage);

          // Answer the question
          await answerQuestion(playerPage, 0);
          await playerPage.waitForTimeout(1000);

          // Capture a few mid-game screenshots
          if (i === 5) {
            console.log("📸 Capturing mid-game state (Q5)");
            await playerPage.screenshot({ path: "test-results/10-player-mid-game-q5.png", fullPage: true });
            await tvPage.screenshot({ path: "test-results/11-tv-mid-game-q5.png", fullPage: true });
          }
        } catch (error) {
          console.log(`   ⚠️ Error on question ${i}:`, error);
        }
      }

      // ========================================
      // 🏆 SCREEN 9: Final Results - Player
      // ========================================
      console.log("\n📸 Capturing SCREEN 9: Final Results - Player");
      try {
        await expect(playerPage.getByTestId("final-results")).toBeVisible({ timeout: 30000 });
        await playerPage.waitForTimeout(1000);
        await playerPage.screenshot({ path: "test-results/12-player-final-results.png", fullPage: true });
      } catch (error) {
        console.log("⚠️ Could not capture player final results:", error);
        await playerPage.screenshot({ path: "test-results/12-player-final-results-ERROR.png", fullPage: true });
      }

      // ========================================
      // 📺 SCREEN 10: Final Results - TV
      // ========================================
      console.log("📸 Capturing SCREEN 10: Final Results - TV");
      await tvPage.waitForTimeout(2000);
      await tvPage.screenshot({ path: "test-results/13-tv-final-leaderboard.png", fullPage: true });

      console.log("\n✅ SCREENSHOT TOUR COMPLETE!");
      console.log("📁 Screenshots saved to: test-results/");
      console.log("\n📸 Captured screens:");
      console.log("   01 - Home Page");
      console.log("   02 - TV Lobby (empty)");
      console.log("   03 - Join Page");
      console.log("   04 - Player Lobby (waiting)");
      console.log("   05 - TV Lobby (with player)");
      console.log("   06 - TV Question Screen");
      console.log("   07 - Player Question Screen");
      console.log("   08 - Player Answer Submitted");
      console.log("   09 - TV Answer Results");
      console.log("   10 - Player Mid-Game (Q5)");
      console.log("   11 - TV Mid-Game (Q5)");
      console.log("   12 - Player Final Results ⭐");
      console.log("   13 - TV Final Leaderboard ⭐");

    } finally {
      await tvPage.close();
      await playerPage.close();
      await tvContext.close();
      await playerContext.close();
    }
  });

  test("Quick multi-player screenshot tour", async ({ browser }) => {
    const tvContext = await browser.newContext({
      viewport: { width: 1280, height: 720 },
    });
    const player1Context = await browser.newContext({
      viewport: { width: 375, height: 812 },
    });
    const player2Context = await browser.newContext({
      viewport: { width: 375, height: 812 },
    });

    const tvPage = await tvContext.newPage();
    const player1Page = await player1Context.newPage();
    const player2Page = await player2Context.newPage();

    try {
      console.log("\n📸 Multi-player lobby tour");
      const roomCode = await createGame(tvPage);

      await tvPage.screenshot({ path: "test-results/multi-01-tv-empty.png", fullPage: true });

      await joinGame(player1Page, roomCode, "Player 1");
      await tvPage.screenshot({ path: "test-results/multi-02-tv-1-player.png", fullPage: true });

      await joinGame(player2Page, roomCode, "Player 2");
      await tvPage.screenshot({ path: "test-results/multi-03-tv-2-players.png", fullPage: true });

      console.log("✅ Multi-player screenshots captured!");

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
