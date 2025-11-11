/**
 * v1.7 Content Audit – Automated Checklist
 *
 * This Playwright spec mirrors the manual checklist at
 * docs/audits/V1.7_MANUAL_TEST_CHECKLIST.md. It spins up a full TV + 3 player
 * session, captures every question payload, and asserts that:
 *   • The new tame poll questions appear in the mix
 *   • At least 2 personalized questions are delivered per game
 *   • Shock-focused sex trivia questions surface
 *   • Regular trivia pulls from a diverse category pool
 *   • Receipt/poll text never leaks raw PII
 *
 * IMPORTANT: The Flask-SocketIO/eventlet server must be running in the foreground
 * (`python3 run_server.py`) before executing this test. This spec only validates
 * content once the real game server is live.
 *
 * Run with:
 *   npx playwright test v17-content-audit.spec.ts --project=chromium --headed
 */

import { test, expect, Page, BrowserContext } from "@playwright/test";
import {
  answerQuestion,
  createGame,
  getCurrentQuestion,
  joinGame,
  startGame,
  waitForNextQuestion,
} from "./support/test-utils";

type CapturedQuestion = {
  question_type?: string;
  category?: string;
  question_text: string;
  difficulty?: number;
};

const TAME_POLL_QUESTIONS = new Set([
  "Who's most likely to binge-watch an entire series in one night?",
  "Who's most likely to forget someone's name right after being introduced?",
  "Who's most likely to text 'lol' but not actually laugh?",
  "Who's most likely to take a selfie at an inappropriate time?",
  "Who's most likely to leave someone on read for days?",
  "Who's most likely to show up late to everything?",
  "Who's most likely to spend way too much money on food delivery?",
  "Who's most likely to overshare on social media?",
  "Who's most likely to buy something they don't need because it was on sale?",
  "Who's most likely to start a conversation at 2am?",
  "Who's most likely to accidentally like an old Instagram photo while stalking?",
  "Who's most likely to take forever to respond to texts?",
  "Who's most likely to cancel plans last minute?",
  "Who's most likely to embarrass themselves in public?",
  "Who's most likely to sing in the shower way too loud?",
]);

const SEX_SLANG_KEYWORDS = [
  "dtf",
  "sneaky link",
  "bbc",
  "body count",
  "situationship",
  "walk of shame",
  "netflix and chill",
  "hookup",
];

const PII_PATTERNS = [
  /\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b/, // Phone numbers
  /\b\(\d{3}\)\s?\d{3}[-.\s]?\d{4}\b/, // Alt phone format
  /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b/, // Emails
  /\b\d{5}(?:-\d{4})?\b/, // Zip codes
];

async function attachQuestionLogger(page: Page) {
  await page.waitForFunction(
    () => typeof (window as any).player !== "undefined",
    null,
    { timeout: 10_000 }
  );

  await page.evaluate(() => {
    const w = window as any;
    const dashboard = w.player;
    if (!dashboard || typeof dashboard.displayQuestion !== "function") {
      throw new Error("Player dashboard not initialized");
    }

    const clonedQuestions: CapturedQuestion[] = [];
    w.__questionLog = clonedQuestions;

    const originalDisplay = dashboard.displayQuestion.bind(dashboard);
    dashboard.displayQuestion = function patchedDisplay(question: any) {
      const clone =
        typeof structuredClone === "function"
          ? structuredClone(question)
          : JSON.parse(JSON.stringify(question));
      clonedQuestions.push(clone);
      return originalDisplay(question);
    };
  });
}

async function getCapturedQuestion(page: Page, index: number) {
  await page.waitForFunction(
    (expectedIndex: number) => {
      const log = (window as any).__questionLog;
      return Array.isArray(log) && log.length >= expectedIndex;
    },
    index + 1,
    { timeout: 30_000 }
  );

  const question = await page.evaluate(
    (i: number) => {
      const log = (window as any).__questionLog || [];
      return log[i] ?? null;
    },
    index
  );

  if (!question) {
    throw new Error(`Question index ${index} was not captured`);
  }

  return question as CapturedQuestion;
}

test.describe("🎯 v1.7 Content Audit", () => {
  test.setTimeout(900_000); // 15 minutes to allow full game flow

  test("automatically validates the manual checklist", async ({ browser }) => {
    const tvContext = await browser.newContext({
      viewport: { width: 1280, height: 720 },
    });
    const tvPage = await tvContext.newPage();

    const playerContexts: BrowserContext[] = [];
    const playerPages: Page[] = [];
    const playerNames = ["LaurenBot", "BennyBot", "GinaBot"];

    for (let i = 0; i < playerNames.length; i++) {
      const context = await browser.newContext({
        viewport: { width: 428, height: 926 },
      });
      playerContexts.push(context);
      playerPages.push(await context.newPage());
    }

    try {
      const roomCode = await createGame(tvPage);

      for (let i = 0; i < playerPages.length; i++) {
        await joinGame(playerPages[i], roomCode, playerNames[i]);
      }

      // Track question payloads from the first player
      await attachQuestionLogger(playerPages[0]);

      await startGame(tvPage);

      const targetQuestions = 15;
      const capturedQuestions: CapturedQuestion[] = [];

      for (let idx = 0; idx < targetQuestions; idx++) {
        const currentQuestionText = await getCurrentQuestion(tvPage);
        const questionData = await getCapturedQuestion(playerPages[0], idx);
        capturedQuestions.push(questionData);

        for (let p = 0; p < playerPages.length; p++) {
          await answerQuestion(playerPages[p], (idx + p) % 4);
        }

        if (idx < targetQuestions - 1) {
          await waitForNextQuestion(tvPage, currentQuestionText, 45_000);
        }
      }

      expect(capturedQuestions.length).toBeGreaterThanOrEqual(targetQuestions);

      const pollQuestions = capturedQuestions.filter(
        (q) => q.question_type === "poll"
      );
      expect(pollQuestions.length).toBeGreaterThan(0);
      expect(
        pollQuestions.some((q) => TAME_POLL_QUESTIONS.has(q.question_text))
      ).toBeTruthy();

      const personalizedCount = capturedQuestions.filter((q) =>
        q.question_type?.startsWith("personalized")
      ).length;
      expect(personalizedCount).toBeGreaterThanOrEqual(2);

      const sexTrivia = capturedQuestions.filter(
        (q) =>
          q.question_type === "trivia" &&
          SEX_SLANG_KEYWORDS.some((keyword) =>
            (q.question_text || "")
              .toLocaleLowerCase()
              .includes(keyword.toLocaleLowerCase())
          )
      );
      expect(sexTrivia.length).toBeGreaterThan(0);

      const triviaCategories = new Set(
        capturedQuestions
          .filter((q) => q.question_type === "trivia")
          .map((q) => q.category || "UNKNOWN")
      );
      expect(triviaCategories.size).toBeGreaterThanOrEqual(4);

      const piiViolations = capturedQuestions.filter((q) =>
        PII_PATTERNS.some((pattern) => pattern.test(q.question_text || ""))
      );
      expect(piiViolations).toHaveLength(0);
    } finally {
      await Promise.all([
        tvContext.close(),
        ...playerContexts.map((ctx) => ctx.close()),
      ]);
    }
  });
});
