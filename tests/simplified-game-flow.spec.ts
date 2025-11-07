/**
 * Simplified smoke tests using stable test IDs and utilities
 * Quick, focused tests for rapid feedback
 */

import { test, expect } from "@playwright/test";
import {
  createGame,
  joinGame,
  startGame,
  getCurrentQuestion,
} from "./support/test-utils";

test.describe("Simplified Game Flow @smoke", () => {
  test.setTimeout(60000); // Shorter timeout for smoke tests

  test("should create a game and show TV waiting screen", async ({ page }) => {
    const roomCode = await createGame(page);

    // Verify we're on the TV page
    expect(page.url()).toContain(`/tv/${roomCode}`);

    // Check for TV waiting screen elements
    await expect(page.getByTestId("tv-room-code")).toHaveText(roomCode);

    // Check for Start Game button (should be disabled with 0 players)
    const startButton = page.getByTestId("start-game-btn");
    await expect(startButton).toBeVisible();
    await expect(startButton).toBeDisabled(); // No players yet

    console.log(`✅ Game created with room code: ${roomCode}`);
  });

  test("should allow one player to join and wait in lobby", async ({ browser }) => {
    const tvContext = await browser.newContext();
    const playerContext = await browser.newContext();

    const tvPage = await tvContext.newPage();
    const playerPage = await playerContext.newPage();

    try {
      // Create game on TV
      const roomCode = await createGame(tvPage);

      // Player joins
      await joinGame(playerPage, roomCode, "Alice");

      // Verify player is on waiting screen
      await expect(playerPage.getByTestId("waiting-screen")).toBeVisible();
      await expect(playerPage.getByTestId("room-code-display")).toHaveText(roomCode);

      // TV should now have Start button enabled (1 player joined)
      const startBtn = tvPage.getByTestId("start-game-btn");
      await expect(startBtn).toBeEnabled({ timeout: 5000 });

      console.log("✅ One player joined successfully");
    } finally {
      await tvPage.close();
      await playerPage.close();
      await tvContext.close();
      await playerContext.close();
    }
  });

  test("should allow multiple players to join", async ({ browser }) => {
    const tvContext = await browser.newContext();
    const player1Context = await browser.newContext();
    const player2Context = await browser.newContext();

    const tvPage = await tvContext.newPage();
    const player1Page = await player1Context.newPage();
    const player2Page = await player2Context.newPage();

    try {
      const roomCode = await createGame(tvPage);

      // Two players join
      await joinGame(player1Page, roomCode, "Alice");
      await joinGame(player2Page, roomCode, "Bob");

      // Both should be in waiting screen
      await expect(player1Page.getByTestId("waiting-screen")).toBeVisible();
      await expect(player2Page.getByTestId("waiting-screen")).toBeVisible();

      // TV start button should be enabled
      await expect(tvPage.getByTestId("start-game-btn")).toBeEnabled({ timeout: 5000 });

      console.log("✅ Multiple players joined successfully");
    } finally {
      await tvPage.close();
      await player1Page.close();
      await player2Page.close();
      await tvContext.close();
      await player1Context.close();
      await player2Context.close();
    }
  });

  test("should start game and show first question", async ({ browser }) => {
    const tvContext = await browser.newContext();
    const playerContext = await browser.newContext();

    const tvPage = await tvContext.newPage();
    const playerPage = await playerContext.newPage();

    try {
      // Setup: Create and join
      const roomCode = await createGame(tvPage);
      await joinGame(playerPage, roomCode, "TestPlayer");

      // Start game from TV
      await startGame(tvPage);

      // Verify question appears on both TV and player
      await expect(tvPage.getByTestId("question-text")).toBeVisible();
      await expect(playerPage.getByTestId("question-text")).toBeVisible();

      // Get question text to verify it's not empty
      const tvQuestion = await tvPage.getByTestId("question-text").textContent();
      const playerQuestion = await playerPage.getByTestId("question-text").textContent();

      expect(tvQuestion).toBeTruthy();
      expect(tvQuestion).toBe(playerQuestion); // Same question on both screens

      console.log(`✅ Game started with question: ${tvQuestion}`);
    } finally {
      await tvPage.close();
      await playerPage.close();
      await tvContext.close();
      await playerContext.close();
    }
  });

  test("should handle player answering a question", async ({ browser }) => {
    const tvContext = await browser.newContext();
    const playerContext = await browser.newContext();

    const tvPage = await tvContext.newPage();
    const playerPage = await playerContext.newPage();

    try {
      // Setup: Create, join, and start
      const roomCode = await createGame(tvPage);
      await joinGame(playerPage, roomCode, "TestPlayer");
      await startGame(tvPage);

      // Wait for question to be visible
      await expect(playerPage.getByTestId("question-text")).toBeVisible();

      // Find and click first answer
      const answers = playerPage.locator('[data-testid^="answer-"]');
      await expect(answers.first()).toBeVisible({ timeout: 10000 });
      await answers.first().click();

      // Verify answer was submitted
      await expect(playerPage.getByTestId("answer-submitted")).toBeVisible({ timeout: 5000 });

      console.log("✅ Player answered question successfully");
    } finally {
      await tvPage.close();
      await playerPage.close();
      await tvContext.close();
      await playerContext.close();
    }
  });
});
