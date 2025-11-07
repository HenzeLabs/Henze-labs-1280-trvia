/**
 * Complete game flow test using stable test IDs and utilities
 */

import { test, expect } from "@playwright/test";
import {
  createGame,
  joinGame,
  startGame,
  answerQuestion,
  waitForNextQuestion,
  getCurrentQuestion
} from "./support/test-utils";

test.describe("Complete Game Flow", () => {
  // Set longer timeout for multiplayer tests
  test.setTimeout(90000);

  test("should create game, join players, play through questions, and show results", async ({ browser }) => {
    // Create two contexts: one for TV/creator, one for joining player
    const tvContext = await browser.newContext();
    const playerContext = await browser.newContext();

    const tvPage = await tvContext.newPage();
    const playerPage = await playerContext.newPage();

    try {
      // Step 1: Create game from home page
      console.log("Creating game...");
      const roomCode = await createGame(tvPage);
      console.log(`Game created with room code: ${roomCode}`);

      // Verify TV page shows room code
      await expect(tvPage.getByTestId("tv-room-code")).toHaveText(roomCode);

      // Step 2: Join as a player
      console.log("Joining game as player...");
      await joinGame(playerPage, roomCode, "Test Player");

      // Verify player is in waiting screen
      await expect(playerPage.getByTestId("waiting-screen")).toBeVisible();
      await expect(playerPage.getByTestId("room-code-display")).toHaveText(roomCode);

      // Step 3: Start game (TV/creator starts)
      console.log("Starting game...");
      await startGame(tvPage);

      // Step 4: Wait for first question to appear on both screens
      await expect(tvPage.getByTestId("question-text")).toBeVisible({ timeout: 10000 });
      await expect(playerPage.getByTestId("question-text")).toBeVisible({ timeout: 10000 });

      // Step 5: Answer the question
      console.log("Answering first question...");
      await answerQuestion(playerPage, 0); // Answer A

      // Verify answer submitted
      await expect(playerPage.getByTestId("answer-submitted")).toBeVisible();

      // Step 6: Wait for auto-advance
      const firstQuestion = await getCurrentQuestion(playerPage);
      console.log(`First question: ${firstQuestion}`);

      // Wait for next question (auto-advance after 5 seconds)
      await waitForNextQuestion(playerPage, firstQuestion, 20000);

      console.log("✅ Game flow test passed - auto-advance working!");
    } finally {
      await tvPage.close();
      await playerPage.close();
      await tvContext.close();
      await playerContext.close();
    }
  });

  test("should handle multiple players answering simultaneously", async ({ browser }) => {
    const tvContext = await browser.newContext();
    const player1Context = await browser.newContext();
    const player2Context = await browser.newContext();

    const tvPage = await tvContext.newPage();
    const player1Page = await player1Context.newPage();
    const player2Page = await player2Context.newPage();

    try {
      // Create game
      const roomCode = await createGame(tvPage);

      // Join two players
      await joinGame(player1Page, roomCode, "Player 1");
      await joinGame(player2Page, roomCode, "Player 2");

      // Start game
      await startGame(tvPage);

      // Wait for question
      await expect(player1Page.getByTestId("question-text")).toBeVisible();
      await expect(player2Page.getByTestId("question-text")).toBeVisible();

      // Get current question before answering
      const currentQuestion = await getCurrentQuestion(player1Page);

      // Both players answer in parallel
      await Promise.all([answerQuestion(player1Page, 0), answerQuestion(player2Page, 1)]);

      // Verify both submitted
      await expect(player1Page.getByTestId("answer-submitted")).toBeVisible({ timeout: 5000 });
      await expect(player2Page.getByTestId("answer-submitted")).toBeVisible({ timeout: 5000 });

      // Wait for auto-advance (should happen after all players answer)
      await waitForNextQuestion(player1Page, currentQuestion, 10000);

      console.log("✅ Multiple player test passed - both players answered and game advanced!");
    } finally {
      await tvPage.close();
      await player1Page.close();
      await player2Page.close();
      await tvContext.close();
      await player1Context.close();
      await player2Context.close();
    }
  });

  test("should show final results after all questions", async ({ browser }) => {
    const tvContext = await browser.newContext();
    const playerContext = await browser.newContext();

    const tvPage = await tvContext.newPage();
    const playerPage = await playerContext.newPage();

    try {
      // Create and join
      const roomCode = await createGame(tvPage);
      await joinGame(playerPage, roomCode, "Test Player");

      // Start game
      await startGame(tvPage);

      // Answer all questions (10 questions for testing)
      for (let i = 0; i < 10; i++) {
        console.log(`Answering question ${i + 1}/10...`);

        // Wait for question to be visible
        await expect(playerPage.getByTestId("question-text")).toBeVisible({ timeout: 15000 });

        // Get current question text
        const currentQuestion = await getCurrentQuestion(playerPage);

        // Answer the question
        await answerQuestion(playerPage, 0);

        // For all but the last question, wait for next question
        if (i < 9) {
          await waitForNextQuestion(playerPage, currentQuestion, 15000);
        }
      }

      // After last question, check final results appear
      await expect(playerPage.getByTestId("final-results")).toBeVisible({ timeout: 20000 });
      await expect(playerPage.getByTestId("final-score")).toBeVisible();

      console.log("✅ Final results test passed - all 10 questions completed!");
    } finally {
      await tvPage.close();
      await playerPage.close();
      await tvContext.close();
      await playerContext.close();
    }
  });
});
