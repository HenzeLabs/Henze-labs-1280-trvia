/**
 * 🎮 2-Player Game Test
 *
 * Verifies that the game works perfectly with just 2 players
 */

import { test, expect } from "@playwright/test";
import {
  createGame,
  joinGame,
  startGame,
  answerQuestion,
  waitForNextQuestion,
} from "./support/test-utils";

test.describe("🎮 2-Player Game", () => {
  test.setTimeout(120000); // 2 minutes

  test("Complete game with 2 players", async ({ browser }) => {
    console.log("\n🎮 Testing 2-player game...");

    // Create contexts
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
      // Create game
      console.log("📺 Creating game...");
      const roomCode = await createGame(tvPage);
      console.log(`✅ Room code: ${roomCode}`);

      // Join 2 players
      console.log("👤 Player 1 joining...");
      await joinGame(player1Page, roomCode, "Player 1");
      console.log("✅ Player 1 joined");

      console.log("👤 Player 2 joining...");
      await joinGame(player2Page, roomCode, "Player 2");
      console.log("✅ Player 2 joined");

      // Verify TV shows 2 players
      await tvPage.waitForTimeout(500);
      const playerCount = await tvPage.locator('#tv-player-count').textContent();
      expect(playerCount).toBe('2');
      console.log("✅ TV shows 2 players");

      // Start game
      console.log("🎯 Starting game...");
      await startGame(tvPage);
      console.log("✅ Game started");

      // Verify both players see the question
      await expect(player1Page.getByTestId("question-text")).toBeVisible();
      await expect(player2Page.getByTestId("question-text")).toBeVisible();
      console.log("✅ Both players see question");

      // Play through 3 questions
      for (let i = 1; i <= 3; i++) {
        console.log(`\n❓ Question ${i}/3`);

        const currentQ = await tvPage.getByTestId("question-text").textContent();

        // Both players answer in parallel
        await Promise.all([
          answerQuestion(player1Page, 0),
          answerQuestion(player2Page, 1),
        ]);

        console.log("✅ Both players answered");

        // Wait for auto-advance (except on last question)
        if (i < 3) {
          console.log("⏳ Waiting for auto-advance...");
          await waitForNextQuestion(tvPage, currentQ, 20000);
          console.log("✅ Advanced to next question");
        }
      }

      console.log("\n✅ ✅ ✅ 2-PLAYER TEST PASSED! ✅ ✅ ✅");
      console.log("🎉 Your game works perfectly with 2 players!");

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
