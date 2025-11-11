/**
 * Test utilities and helpers for Playwright tests
 */

import { Page, expect } from "@playwright/test";
import { mkdir } from "fs/promises";
import path from "path";

const SCREENSHOT_DIR = path.join(process.cwd(), "test-results", "screenshots");

export interface StepLogger {
  info: (source: string, message: string, data?: Record<string, unknown>) => void;
}

function logStep(logger: StepLogger | undefined, source: string, message: string, data?: Record<string, unknown>) {
  logger?.info(source, message, data);
}

/**
 * Create a new game and return room code
 */
export async function createGame(page: Page, playerName: string = "Test Player", logger?: StepLogger): Promise<string> {
  await page.goto("/");
  logStep(logger, "createGame", "Navigated to home screen");

  const createBtn = page.getByTestId("create-game-btn");
  await expect(createBtn).toBeVisible({ timeout: 5000 });
  logStep(logger, "createGame", "Create button visible");
  await createBtn.click();
  logStep(logger, "createGame", "Create button clicked");

  // Wait for TV view redirect with timeout
  try {
    await page.waitForURL(/\/tv\/[A-Z0-9]{6}/, { timeout: 15000 });
  } catch (error) {
    await page.screenshot({ path: "test-results/create-game-failed.png" });
    const message = `Failed to redirect to TV view: ${error}`;
    logStep(logger, "createGame", message);
    throw new Error(message);
  }

  // Wait for network to settle
  await page.waitForLoadState("networkidle", { timeout: 10000 });

  // Extract room code from URL
  const url = page.url();
  const match = url.match(/\/tv\/([A-Z0-9]{6})/);

  if (!match) {
    await page.screenshot({ path: "test-results/no-room-code.png" });
    const message = `Failed to extract room code from URL: ${url}`;
    logStep(logger, "createGame", message);
    throw new Error(message);
  }

  const roomCode = match[1];

  // Verify room code is displayed on TV
  await expect(page.getByTestId("tv-room-code")).toHaveText(roomCode, { timeout: 5000 });
  logStep(logger, "createGame", "Room code confirmed on TV", { roomCode, playerName });

  return roomCode;
}

/**
 * Join a game as a player
 */
export async function joinGame(page: Page, roomCode: string, playerName: string, logger?: StepLogger): Promise<void> {
  await page.goto("/join");
  logStep(logger, "joinGame", "Navigated to join page", { playerName, roomCode });

  // Fill form
  const roomInput = page.getByTestId("room-code-input");
  const nameInput = page.getByTestId("player-name-input");
  const joinBtn = page.getByTestId("join-game-btn");

  await expect(roomInput).toBeVisible({ timeout: 5000 });
  await roomInput.fill(roomCode);
  await nameInput.fill(playerName);
  logStep(logger, "joinGame", "Filled join form", { playerName });
  await joinBtn.click();

  // Wait for player dashboard or error
  try {
    await page.waitForURL(/\/player\/.+/, { timeout: 10000 });
  } catch (error) {
    // Check if there's an error message
    const errorMsg = page.getByTestId("join-error");
    const isErrorVisible = await errorMsg.isVisible();

    if (isErrorVisible) {
      const errorText = await errorMsg.textContent();
      await page.screenshot({ path: "test-results/join-failed.png" });
      const message = `Failed to join game: ${errorText}`;
      logStep(logger, "joinGame", message);
      throw new Error(message);
    }

    throw error;
  }

  // Wait for lobby to load
  await expect(page.getByTestId("waiting-screen")).toBeVisible({ timeout: 5000 });
  logStep(logger, "joinGame", "Player reached waiting screen", { playerName, roomCode });
}

/**
 * Wait for WebSocket connection
 */
export async function waitForWebSocket(page: Page, timeout: number = 5000): Promise<void> {
  await page.waitForFunction(
    () => {
      // @ts-ignore
      return window.io && window.io.connected === true;
    },
    { timeout }
  );
}

/**
 * Wait for lobby to be ready before starting
 */
export async function waitForLobbyReady(page: Page): Promise<void> {
  // Wait for network to settle
  await page.waitForLoadState("networkidle", { timeout: 10000 });

  // Verify we're in waiting screen
  await expect(page.getByTestId("waiting-screen")).toBeVisible({ timeout: 10000 });

  // Verify room code is displayed
  const roomCodeEl = page.getByTestId("room-code-display");
  await expect(roomCodeEl).toBeVisible();
  await expect(roomCodeEl).toHaveText(/[A-Z0-9]{6}/);
}

/**
 * Start game from TV page (Jackbox style - TV has the start button)
 */
export async function startGame(page: Page, logger?: StepLogger): Promise<void> {
  // Wait for network to settle
  await page.waitForLoadState("networkidle", { timeout: 10000 });

  const startBtn = page.getByTestId("start-game-btn");

  // Check if button exists and is visible
  const isVisible = await startBtn.isVisible().catch(() => false);
  if (!isVisible) {
    await page.screenshot({ path: "test-results/start-game-missing.png" });
    const message = "Start game button not visible on TV page.";
    logStep(logger, "startGame", message);
    throw new Error(message);
  }

  // Wait for button to be enabled (needs at least 1 player)
  await expect(startBtn).toBeEnabled({ timeout: 10000 });
  logStep(logger, "startGame", "Start button enabled");

  await startBtn.click();
  logStep(logger, "startGame", "Start button clicked");

  // Wait for question to appear on TV
  const questionText = page.getByTestId("question-text");
  await expect(questionText).toBeVisible({ timeout: 15000 });
  await expect(questionText).not.toBeEmpty();
  logStep(logger, "startGame", "First question visible");
}

/**
 * Answer a question
 */
export async function answerQuestion(page: Page, answerIndex: number = 0, logger?: StepLogger): Promise<void> {
  // Wait for answers to be available
  const answers = page.locator('[data-testid^="answer-"]');
  await expect(answers.first()).toBeVisible({ timeout: 10000 });

  // Get specific answer button
  const answerBtn = answers.nth(answerIndex);
  await expect(answerBtn).toBeEnabled({ timeout: 5000 });
  await answerBtn.click();
  logStep(logger, "answerQuestion", "Answer clicked", { answerIndex });

  // Wait for answer submission confirmation (either waiting screen or next question)
  try {
    await expect(page.getByTestId("answer-submitted")).toBeVisible({ timeout: 5000 });
    logStep(logger, "answerQuestion", "Answer submitted confirmation shown");
  } catch (error) {
    // If answer-submitted doesn't appear, check if we moved to next question already
    const questionScreen = page.getByTestId("question-screen");
    const isQuestionVisible = await questionScreen.isVisible();

    if (!isQuestionVisible) {
      await page.screenshot({ path: "test-results/answer-submit-failed.png" });
      const message = "Failed to confirm answer submission";
      logStep(logger, "answerQuestion", message);
      throw new Error(message);
    }
    // If question screen is still visible, answer was submitted
    logStep(logger, "answerQuestion", "Answer accepted without transition");
  }
}

/**
 * Wait for all players to answer (checks banner or auto-advance)
 */
export async function waitForAllPlayersAnswered(page: Page, timeout: number = 30000): Promise<void> {
  // Wait for either the banner or the next question to appear
  try {
    await expect(page.getByTestId("all-answered-banner")).toBeVisible({ timeout: 10000 });
  } catch (error) {
    // If banner doesn't appear, game may have auto-advanced already
    // Check if we're on a new question
    const questionText = page.getByTestId("question-text");
    const isVisible = await questionText.isVisible();

    if (!isVisible) {
      throw new Error("Neither all-answered banner nor next question appeared");
    }
  }
}

/**
 * Wait for next question to appear (handles auto-advance)
 */
export async function waitForNextQuestion(page: Page, previousQuestionText: string, timeout: number = 15000, logger?: StepLogger): Promise<void> {
  // Use expect.poll for better race condition handling
  await expect
    .poll(async () => {
      const currentQuestion = await page.getByTestId("question-text").textContent();
      return currentQuestion !== previousQuestionText && currentQuestion && currentQuestion.length > 0;
    }, { timeout })
    .toBeTruthy();
  logStep(logger, "waitForNextQuestion", "Advanced to next question");
}

/**
 * Get current question text
 */
export async function getCurrentQuestion(page: Page): Promise<string> {
  const questionEl = page.getByTestId("question-text");
  return (await questionEl.textContent()) || "";
}

/**
 * Get player score
 */
export async function getPlayerScore(page: Page): Promise<number> {
  const scoreEl = page.getByTestId("player-score");
  const scoreText = await scoreEl.textContent();
  return parseInt(scoreText?.replace(/\D/g, "") || "0", 10);
}

/**
 * Mock WebSocket events for testing
 */
export async function mockWebSocketEvent(page: Page, eventName: string, data: any): Promise<void> {
  await page.evaluate(
    ({ event, payload }) => {
      // @ts-ignore
      if (window.socket && window.socket.emit) {
        // @ts-ignore
        window.socket.emit(event, payload);
      }
    },
    { event: eventName, payload: data }
  );
}

/**
 * Wait for navigation with retry
 */
export async function waitForNavigationWithRetry(
  page: Page,
  urlPattern: RegExp,
  maxRetries: number = 3
): Promise<void> {
  for (let i = 0; i < maxRetries; i++) {
    try {
      await page.waitForURL(urlPattern, { timeout: 10000 });
      return;
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await page.reload();
    }
  }
}

/**
 * Take screenshot with timestamp
 */
export async function takeTimestampedScreenshot(page: Page, name: string): Promise<void> {
  await mkdir(SCREENSHOT_DIR, { recursive: true });
  const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
  const filename = `${name}-${timestamp}.png`;
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, filename), fullPage: true });
}

/**
 * Capture a labelled screenshot (alias for takeTimestampedScreenshot)
 */
export async function captureScreenshot(page: Page, label: string): Promise<void> {
  await takeTimestampedScreenshot(page, label);
}
