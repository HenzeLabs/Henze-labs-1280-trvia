/**
 * Four-player end-to-end flow that captures screenshots for each player and the TV.
 */

import { test, expect } from "@playwright/test";
import {
  createGame,
  joinGame,
  startGame,
  answerQuestion,
  waitForNextQuestion,
  getCurrentQuestion,
  captureScreenshot,
} from "./support/test-utils";
import { SessionLogger } from "./support/sessionLogger";

test.describe("Four Player Screenshot Run", () => {
  test.setTimeout(180_000);

  test("plays a full game with four players and captures screenshots", async ({ browser }) => {
    const tvContext = await browser.newContext({ viewport: { width: 1920, height: 1080 } });
    const playerContexts = await Promise.all(
      Array.from({ length: 4 }, () => browser.newContext({ viewport: { width: 414, height: 896 } }))
    );

    const tvPage = await tvContext.newPage();
    const playerPages = await Promise.all(playerContexts.map((ctx) => ctx.newPage()));

    const playerNames = ["Alex", "Blair", "Casey", "Drew"];
    const logger = new SessionLogger("four-player-screenshot");

    logger.attachPage(tvPage, "TV");
    playerPages.forEach((page, idx) => logger.attachPage(page, `Player-${idx + 1}`));

    try {
      // Create game and capture lobby
      const roomCode = await createGame(tvPage, "Host", logger);
      logger.info("spec", "Game created", { roomCode });
      await captureScreenshot(tvPage, `lobby-tv-${roomCode}`);

      // Join four players
      for (let i = 0; i < playerPages.length; i++) {
        await joinGame(playerPages[i], roomCode, playerNames[i], logger);
        logger.info("spec", "Player joined", { player: playerNames[i], index: i + 1 });
        await captureScreenshot(playerPages[i], `lobby-player-${i + 1}-${playerNames[i]}`);
      }

      // Start the game (TV)
      await startGame(tvPage, logger);
      logger.info("spec", "Game started");

      // Determine question count from TV (fallback to 10)
      const totalQuestionsText = await tvPage.getByTestId("tv-total-questions").textContent();
      const totalQuestions = parseInt(totalQuestionsText || "10", 10) || 10;

      for (let questionIndex = 1; questionIndex <= totalQuestions; questionIndex++) {
        // Wait for question on player 1 screen
        await expect(playerPages[0].getByTestId("question-text")).toBeVisible({ timeout: 20000 });

        const currentQuestionText = await getCurrentQuestion(playerPages[0]);

        // Capture TV + player views before answers
        await captureScreenshot(tvPage, `q${questionIndex}-tv`);
        await Promise.all(
          playerPages.map((page, idx) =>
            captureScreenshot(page, `q${questionIndex}-player${idx + 1}-prompt`)
          )
        );

        // All players answer (spread answers for variety)
        await Promise.all(
          playerPages.map((page, idx) => answerQuestion(page, (questionIndex + idx) % 4, logger))
        );
        logger.info("spec", "All players answered", { questionIndex });

        // Capture waiting state
        await Promise.all(
          playerPages.map((page, idx) =>
            captureScreenshot(page, `q${questionIndex}-player${idx + 1}-after`)
          )
        );

        if (questionIndex < totalQuestions) {
          await waitForNextQuestion(playerPages[0], currentQuestionText, 25000, logger);
        }
      }

      // Final results screenshots
      await Promise.all(
        playerPages.map(async (page, idx) => {
          await expect(page.getByTestId("final-results")).toBeVisible({ timeout: 30000 });
          await captureScreenshot(page, `final-player${idx + 1}-${playerNames[idx]}`);
        })
      );
      await captureScreenshot(tvPage, `final-tv-${roomCode}`);
    } finally {
      await tvPage.close();
      await tvContext.close();
      await Promise.all(
        playerPages.map((page) => page.close().catch(() => undefined))
      );
      await Promise.all(
        playerContexts.map((ctx) => ctx.close().catch(() => undefined))
      );
      await logger.save().catch((error) => {
        console.error("Failed to save session log", error);
      });
    }
  });
});
