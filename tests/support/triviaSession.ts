import { Browser, BrowserContext, Page, expect } from "@playwright/test";

export interface DeviceProfile {
  hostViewport?: { width: number; height: number };
  tvViewport?: { width: number; height: number };
  playerViewport?: { width: number; height: number };
  network?: {
    offline?: boolean;
    latency: number;
    downloadThroughput: number;
    uploadThroughput: number;
  };
  cpuSlowdown?: number;
}

const DEFAULT_PROFILE: DeviceProfile = {
  hostViewport: { width: 1440, height: 900 },
  tvViewport: { width: 1920, height: 1080 },
  playerViewport: { width: 428, height: 926 },
};

const PROFILE_MATRIX: Record<string, DeviceProfile> = {
  "chromium-desktop": {
    ...DEFAULT_PROFILE,
    network: {
      latency: 35,
      downloadThroughput: 10 * 1024 * 1024,
      uploadThroughput: 5 * 1024 * 1024,
    },
  },
  "chromium-tablet": {
    hostViewport: { width: 1280, height: 800 },
    tvViewport: { width: 1920, height: 1080 },
    playerViewport: { width: 820, height: 1180 },
    network: {
      latency: 120,
      downloadThroughput: 3 * 1024 * 1024,
      uploadThroughput: 1.5 * 1024 * 1024,
    },
  },
  "chromium-low-end": {
    hostViewport: { width: 1280, height: 720 },
    tvViewport: { width: 1600, height: 900 },
    playerViewport: { width: 375, height: 667 },
    network: {
      latency: 200,
      downloadThroughput: 1.2 * 1024 * 1024,
      uploadThroughput: 512 * 1024,
    },
    cpuSlowdown: 3,
  },
};

export function resolveDeviceProfile(projectName: string): DeviceProfile {
  return PROFILE_MATRIX[projectName] ?? DEFAULT_PROFILE;
}

export interface PlayerClient {
  name: string;
  context: BrowserContext;
  page: Page;
  id: string;
  status: "alive" | "ghost";
}

export interface SessionMetrics {
  totalQuestions: number;
  minigameCount: number;
  pollCount: number;
  finalSprintQuestions: number;
  questionTypes: Set<string>;
  categories: Set<string>;
  sawMinigame: boolean;
  sawFinalSprint: boolean;
  timings: Record<string, number[]>;
  scoreboardSnapshots: Array<Record<string, number>>;
  ghostRoster: Set<string>;
  finalLeaderboard?: Array<{ name: string; score: number; rank: number }>;
}

interface TriviaSessionOptions {
  hostName?: string;
  playerNames?: string[];
  profile?: DeviceProfile;
  log?: (message: string) => void;
}

interface QuestionWithAnswer {
  id: number;
  category: string;
  question_type: string;
  question_text: string;
  answers: string[];
  correct_answer: string;
  context?: string;
  phase: string;
  sprint_goal?: number;
  sprint_positions?: Record<string, number>;
  targets?: string[];
}

export class TriviaSession {
  static async launch(
    browser: Browser,
    options: TriviaSessionOptions = {}
  ): Promise<TriviaSession> {
    const session = new TriviaSession(browser, options);
    await session.bootstrap();
    return session;
  }

  readonly browser: Browser;
  readonly options: TriviaSessionOptions;
  readonly profile: DeviceProfile;
  readonly metrics: SessionMetrics = {
    totalQuestions: 0,
    minigameCount: 0,
    pollCount: 0,
    finalSprintQuestions: 0,
    questionTypes: new Set(),
    categories: new Set(),
    sawMinigame: false,
    sawFinalSprint: false,
    timings: {},
    scoreboardSnapshots: [],
    ghostRoster: new Set(),
  };

  hostContext!: BrowserContext;
  hostPage!: Page;
  tvContext!: BrowserContext;
  tvPage!: Page;
  players: PlayerClient[] = [];
  roomCode = "";
  private lastQuestionSignature: string | null = null;
  private cleanupCallbacks: Array<() => Promise<void>> = [];

  private constructor(browser: Browser, options: TriviaSessionOptions) {
    this.browser = browser;
    this.options = options;
    const profileOverride =
      options.profile ?? resolveDeviceProfile("chromium-desktop");
    this.profile = { ...DEFAULT_PROFILE, ...profileOverride };
  }

  private log(message: string) {
    if (this.options.log) {
      this.options.log(message);
    }
  }

  private async bootstrap() {
    await this.setupHost();
    await this.setupTv();
    const playerNames = this.options.playerNames ?? [
      "Alice",
      "Bob",
      "Charlie",
      "Diana",
    ];
    for (const name of playerNames) {
      await this.addPlayer(name);
    }
  }

  async setupHost() {
    this.hostContext = await this.browser.newContext({
      viewport: this.profile.hostViewport ?? DEFAULT_PROFILE.hostViewport,
    });
    this.cleanupCallbacks.push(() => this.hostContext.close());

    this.hostPage = await this.hostContext.newPage();
    await this.enableDiagnostics(this.hostPage, "HOST");
    await this.hostPage.goto("/host");
    await this.hostPage.fill(
      "#host-name",
      this.options.hostName ?? "Playwright Host"
    );
    await this.hostPage.click("#create-game-btn");

    await this.hostPage.waitForURL(/\/host\/lobby\?room=/, { timeout: 15_000 });
    const roomCodeText =
      (await this.hostPage.locator("#room-code").textContent())?.trim() ?? "";
    expect(roomCodeText).toMatch(/^[A-Z0-9]{6}$/);
    this.roomCode = roomCodeText;
    this.log(`Room code ${this.roomCode}`);

    await this.hostPage.waitForSelector("#players-ul", {
      state: "attached",
      timeout: 10_000,
    });
  }

  async setupTv() {
    this.tvContext = await this.browser.newContext({
      viewport: this.profile.tvViewport ?? DEFAULT_PROFILE.tvViewport,
    });
    this.cleanupCallbacks.push(() => this.tvContext.close());

    this.tvPage = await this.tvContext.newPage();
    await this.enableDiagnostics(this.tvPage, "TV");
    await this.tvPage.goto(`/tv/${this.roomCode}`);
    await this.tvPage.waitForSelector("#tv-waiting", { timeout: 10_000 });
  }

  async addPlayer(name: string) {
    const playerViewport = this.profile.playerViewport ?? DEFAULT_PROFILE.playerViewport!;
    const context = await this.browser.newContext({
      viewport: playerViewport,
      isMobile: playerViewport.width <= 500,
    });
    this.cleanupCallbacks.push(() => context.close());
    const page = await context.newPage();
    await this.enableDiagnostics(page, name.toUpperCase());
    await page.goto("/join");
    await page.fill("#room-code", this.roomCode);
    await page.fill("#player-name", name);
    await Promise.all([
      page.waitForURL(/\/player\/player_/i, { timeout: 15_000 }),
      page.click("#join-game-btn"),
    ]);

    await page.waitForSelector("#waiting-screen", { timeout: 10_000 });
    const url = new URL(page.url());
    const playerId = url.pathname.split("/").pop() ?? "";
    expect(playerId).toMatch(/^player_/);

    this.players.push({ name, context, page, id: playerId, status: "alive" });
    await this.waitForLobbyCount(this.players.length);

    // CRITICAL: Wait for player's WebSocket to be fully connected and synced
    // This ensures the player will receive game_started event when we start
    await page.waitForFunction(
      () => {
        const player = (window as any).player;
        return player && player.socket && player.socket.connected;
      },
      { timeout: 10_000 }
    );

    // Give socket a moment to process any pending events
    await page.waitForTimeout(500);
  }

  private async waitForLobbyCount(count: number) {
    await expect(this.hostPage.locator("#players-ul li")).toHaveCount(count, {
      timeout: 10_000,
    });
  }

  async startGame() {
    const startButton = this.hostPage.locator("#start-game-btn");
    await expect(startButton).toBeEnabled({ timeout: 10_000 });

    // Click start button and force via JS as fallback
    await startButton.click({ force: true });

    // Fallback trigger via JS in case UI overlay captures click
    await this.hostPage.evaluate(() => {
      const lobby = (window as any).hostLobby;
      if (lobby?.startGame) {
        console.log("🧪 Forcing startGame via Playwright");
        lobby.startGame();
      }
    });

    // Wait for navigation to play page
    await this.hostPage.waitForURL(/\/host\/play/i, { timeout: 20_000 });

    // Wait for host page JavaScript to load (either hostDashboard or hostGamePlay)
    await this.hostPage.waitForFunction(
      () => {
        const dashboard = (window as any).hostDashboard;
        const gameplay = (window as any).hostGamePlay;
        return dashboard || gameplay;
      },
      { timeout: 20_000 }
    );

    // Wait for first question to load on host
    await this.hostPage.waitForFunction(
      () => {
        const el = document.querySelector<HTMLElement>("#question-text");
        return (
          !!el &&
          el.textContent !== null &&
          el.textContent.trim().length > 0 &&
          !/Loading/i.test(el.textContent)
        );
      },
      { timeout: 20_000 }
    );

    // CRITICAL: Wait for all players to receive the game_started event and first question
    // This ensures no player is left on the waiting screen
    await Promise.all(
      this.players.map((player) =>
        player.page.waitForFunction(
          () => {
            const questionScreen = document.querySelector("#question-screen");
            const questionText =
              document.querySelector<HTMLElement>("#question-text");
            const questionVisible =
              questionScreen &&
              window.getComputedStyle(questionScreen).display !== "none";
            const hasText =
              questionText &&
              questionText.textContent &&
              questionText.textContent.trim().length > 0;
            return questionVisible && hasText;
          },
          { timeout: 20_000 }
        )
      )
    );

    this.log("✅ Game started successfully");
  }

  async waitForPhase(phases: string[], timeout = 15_000): Promise<string> {
    const handle = await this.hostPage.waitForFunction(
      (targetPhases) => {
        const gameplay = (window as any).hostGamePlay;
        if (!gameplay) return null;
        const current = gameplay.currentPhase || gameplay.phase;
        if (!current) return null;
        if (targetPhases.includes(current)) {
          return current;
        }
        if (
          targetPhases.includes("finished") &&
          gameplay.gameState === "finished"
        ) {
          return "finished";
        }
        return null;
      },
      phases,
      { timeout }
    );

    const result = await handle.jsonValue();
    return result as string;
  }

  async waitForNextQuestion(): Promise<QuestionWithAnswer> {
    const handle = await this.hostPage.waitForFunction(
      (previousSignature) => {
        const gameplay = (window as any).hostGamePlay;
        if (!gameplay || !gameplay.currentQuestion) {
          return null;
        }
        const question = gameplay.currentQuestion;
        const currentPhase =
          gameplay.currentPhase ||
          gameplay.phase ||
          question.phase ||
          "question";
        if (!(question as any).__pwSignature) {
          const extra =
            currentPhase === "minigame"
              ? (gameplay.minigameTargets || []).join(",")
              : currentPhase === "final_sprint"
              ? JSON.stringify(question.sprint_positions || {})
              : question.context || "";
          (question as any).__pwSignature = `${question.id ?? "na"}|${
            question.question_text
          }|${currentPhase}|${
            question.answers?.join("|") ?? ""
          }|${extra}|${Date.now()}`;
        }
        const signature = (question as any).__pwSignature as string;
        if (signature === previousSignature) {
          return null;
        }
        return { signature, phase: currentPhase };
      },
      this.lastQuestionSignature,
      { timeout: 25_000 }
    );

    const data = await handle.jsonValue();
    if (!data || typeof data !== 'object' || !('signature' in data) || !('phase' in data)) {
      throw new Error('Failed to get question data from browser');
    }

    const questionSignature = data.signature as string;
    this.lastQuestionSignature = questionSignature;

    const question = await this.fetchHostQuestionWithAnswer();
    question.phase = (data.phase as string) ?? question.phase;

    this.metrics.totalQuestions += 1;
    this.metrics.questionTypes.add(question.question_type);
    if (question.category) {
      this.metrics.categories.add(question.category);
    }

    return question;
  }

  async fetchHostQuestionWithAnswer(): Promise<QuestionWithAnswer> {
    const question = await this.hostPage.evaluate(async (roomCode: string) => {
      const response = await (window as any).app.apiCall(
        `/game/question/${roomCode}/host`
      );
      return response.question;
    }, this.roomCode);

    return question as QuestionWithAnswer;
  }

  async broadcastSync(question: QuestionWithAnswer, timeout = 20_000) {
    const start = Date.now();

    // Host and TV should already have the question displayed
    await this.hostPage.waitForFunction(
      (text) => {
        const el = document.querySelector<HTMLElement>("#question-text");
        return el && el.textContent && el.textContent.trim() === text;
      },
      question.question_text,
      { timeout }
    );

    await this.tvPage.waitForSelector("#tv-question:not(.hidden)", { timeout });

    // Wait for players to receive the question via WebSocket and display it
    // Check that question text has updated (works for both initial load and subsequent questions)
    await Promise.all(
      this.players.map((player) =>
        player.page.waitForFunction(
          (expectedText) => {
            const questionScreen = document.querySelector("#question-screen");
            const questionText =
              document.querySelector<HTMLElement>("#question-text");

            // Question screen must be visible
            const questionVisible =
              questionScreen &&
              window.getComputedStyle(questionScreen).display !== "none";

            // Question text must match the expected question
            const textMatches =
              questionText &&
              questionText.textContent &&
              questionText.textContent.trim() === expectedText;

            return questionVisible && textMatches;
          },
          question.question_text,
          { timeout }
        )
      )
    );

    this.recordTiming("questionBroadcast", Date.now() - start);
  }

  async answerQuestionSplit(question: QuestionWithAnswer) {
    const correctIndex = question.answers.findIndex(
      (ans) => ans === question.correct_answer
    );
    expect(correctIndex).toBeGreaterThanOrEqual(0);

    const fallbackWrong =
      question.answers.find((ans) => ans !== question.correct_answer) ??
      question.answers[0];

    for (let i = 0; i < this.players.length; i++) {
      const player = this.players[i];
      const buttons = player.page.locator(".answer-btn");
      await buttons.first().waitFor({ state: "visible", timeout: 10_000 });
      const targetAnswer =
        i % 2 === 0 ? question.correct_answer : fallbackWrong;
      const answerIndex = question.answers.findIndex(
        (ans) => ans === targetAnswer
      );
      const button = buttons.nth(answerIndex >= 0 ? answerIndex : 0);

      if (!(await button.isEnabled())) {
        // Ghosts cannot answer normal questions; assert disabled state
        const bannerText = await player.page
          .locator("#status-banner")
          .textContent();
        expect(bannerText ?? "").toContain("ghost");
        continue;
      }

      await button.click();
    }
  }

  async handlePoll(question: QuestionWithAnswer) {
    this.metrics.pollCount += 1;
    for (let i = 0; i < this.players.length; i++) {
      const player = this.players[i];
      const buttons = player.page.locator(".answer-btn");
      await buttons.first().waitFor({ state: "visible", timeout: 10_000 });
      const button = buttons.nth(i % Math.max(1, await buttons.count()));
      await button.click();
    }
  }

  async waitForAllPlayersAnswered(timeout = 10_000) {
    // Wait for host to detect all players have answered
    await this.hostPage.waitForFunction(
      () => {
        const gameplay = (window as any).hostGamePlay;
        return gameplay && gameplay.allAnswered === true;
      },
      { timeout }
    );
  }

  async waitForAutoAdvance() {
    // Game automatically advances after all players answer (5 second countdown)
    // Wait for the host's allAnswered flag to clear (indicates question has advanced)
    this.log('⏳ Waiting for automatic game progression...');

    await this.hostPage.waitForFunction(
      () => {
        const gameplay = (window as any).hostGamePlay;
        // Wait for allAnswered to be reset to false (new question loaded)
        return gameplay && gameplay.allAnswered === false;
      },
      { timeout: 10_000 }
    );

    // Capture leaderboard snapshot after auto-advance
    const leaderboard = await this.fetchLeaderboard();
    this.metrics.scoreboardSnapshots.push(this.mapScores(leaderboard));
  }

  async handleMinigame(question: QuestionWithAnswer) {
    this.metrics.sawMinigame = true;
    this.metrics.minigameCount += 1;

    const targets = await this.hostPage.evaluate(() => {
      const gameplay = (window as any).hostGamePlay;
      return gameplay?.minigameTargets ?? [];
    });

    expect(targets.length).toBeGreaterThan(0);

    for (const player of this.players) {
      const isTarget = targets.includes(player.id);
      const buttons = player.page.locator(".answer-btn");
      await buttons.first().waitFor({ state: "visible", timeout: 10_000 });
      if (!isTarget) {
        expect(await buttons.first().isEnabled()).toBeFalsy();
        continue;
      }

      const safeAnswer = question.correct_answer;
      const sacrificial =
        question.answers.find((ans) => ans !== safeAnswer) ??
        question.answers[0];
      const index = question.answers.findIndex((ans) => ans === sacrificial);
      await buttons.nth(index >= 0 ? index : 0).click();
    }

    await this.hostPage.waitForSelector("#minigame-results ul li", {
      timeout: 20_000,
    });
    const leaderboard = await this.fetchLeaderboard();
    leaderboard
      .filter((entry) => entry.status === "ghost")
      .forEach((entry) => this.metrics.ghostRoster.add(entry.name));

    await expect(this.hostPage.locator("#next-question-btn")).toBeEnabled({
      timeout: 10_000,
    });
    await this.hostPage.locator("#next-question-btn").click({ force: true });
  }

  async handleFinalSprint(initialQuestion: QuestionWithAnswer) {
    this.metrics.sawFinalSprint = true;
    let currentQuestion: QuestionWithAnswer | null = initialQuestion;
    let finished = false;

    while (!finished && currentQuestion) {
      if (currentQuestion.phase !== "final_sprint") {
        currentQuestion = await this.waitForNextQuestion();
        continue;
      }

      this.metrics.finalSprintQuestions += 1;
      await this.broadcastSync(currentQuestion);

      // TypeScript safety: currentQuestion is guaranteed to be non-null here due to while loop condition
      const question = currentQuestion;
      const answerIndex = question.answers.findIndex(
        (ans) => ans === question.correct_answer
      );
      expect(answerIndex).toBeGreaterThanOrEqual(0);

      await Promise.all(
        this.players.map(async (player) => {
          const buttons = player.page.locator(".answer-btn");
          await buttons.first().waitFor({ state: "visible", timeout: 10_000 });
          const target = buttons.nth(answerIndex);
          await target.click();
        })
      );

      await this.hostPage.waitForSelector("#final-sprint-status ul li", {
        timeout: 10_000,
      });
      await this.hostPage.waitForTimeout(750);

      finished = await this.hostPage.evaluate(() => {
        const gameplay = (window as any).hostGamePlay;
        return gameplay?.gameState === "finished";
      });

      if (!finished) {
        currentQuestion = await this.waitForNextQuestion();
      }
    }

    await this.captureFinalLeaderboard();
  }

  async captureFinalLeaderboard() {
    const summary = await this.hostPage.evaluate(async (roomCode: string) => {
      const response = await (window as any).app.apiCall(
        `/game/leaderboard/${roomCode}`
      );
      return response.leaderboard;
    }, this.roomCode);

    if (Array.isArray(summary)) {
      this.metrics.finalLeaderboard = summary.map((entry: any) => ({
        name: entry.name,
        score: entry.score,
        rank: entry.rank,
      }));
    }
  }

  async fetchLeaderboard(): Promise<
    Array<{
      player_id: string;
      name: string;
      score: number;
      status: string;
      rank: number;
    }>
  > {
    const leaderboard = await this.hostPage.evaluate(
      async (roomCode: string) => {
        const response = await (window as any).app.apiCall(
          `/game/leaderboard/${roomCode}`
        );
        return response.leaderboard;
      },
      this.roomCode
    );

    return leaderboard as Array<{
      player_id: string;
      name: string;
      score: number;
      status: string;
      rank: number;
    }>;
  }

  private mapScores(
    entries: Array<{ player_id: string; score: number }>
  ): Record<string, number> {
    return entries.reduce<Record<string, number>>((acc, entry) => {
      acc[entry.player_id] = entry.score;
      return acc;
    }, {});
  }

  async playFullGame() {
    await this.startGame();

    let gameFinished = false;
    while (!gameFinished) {
      const question = await this.waitForNextQuestion();
      if (question.phase === "final_sprint") {
        await this.handleFinalSprint(question);
        gameFinished = true;
        break;
      }

      await this.broadcastSync(question);

      if (question.phase === "minigame") {
        await this.handleMinigame(question);
        continue;
      }

      if (question.question_type === "poll") {
        await this.handlePoll(question);
      } else {
        await this.answerQuestionSplit(question);
      }

      await this.waitForAllPlayersAnswered();
      await this.waitForAutoAdvance();

      gameFinished = await this.hostPage.evaluate(() => {
        const gameplay = (window as any).hostGamePlay;
        return gameplay?.gameState === "finished";
      });
    }

    await this.tvPage.waitForSelector("#tv-leaderboard:not(.hidden)", {
      timeout: 20_000,
    });
  }

  recordTiming(metric: string, value: number) {
    if (!this.metrics.timings[metric]) {
      this.metrics.timings[metric] = [];
    }
    this.metrics.timings[metric].push(value);
  }

  async enableDiagnostics(page: Page, label: string) {
    page.on("console", (msg) =>
      this.log(`${label}> ${msg.type()}: ${msg.text()}`)
    );
    page.on("pageerror", (error) => this.log(`${label} ERROR> ${error}`));

    if (this.profile.network || this.profile.cpuSlowdown) {
      await this.applyEnvironment(page, this.profile);
    }
  }

  private async applyEnvironment(page: Page, profile: DeviceProfile) {
    const browserName = page.context().browser()?.browserType().name();
    if (browserName !== "chromium") {
      return;
    }

    const client = await page.context().newCDPSession(page);
    if (profile.network) {
      const {
        offline = false,
        latency,
        downloadThroughput,
        uploadThroughput,
      } = profile.network;
      await client.send("Network.enable");
      await client.send("Network.emulateNetworkConditions", {
        offline,
        latency,
        downloadThroughput,
        uploadThroughput,
      });
    }

    if (profile.cpuSlowdown && profile.cpuSlowdown > 1) {
      await client.send("Emulation.setCPUThrottlingRate", {
        rate: profile.cpuSlowdown,
      });
    }
  }

  getMetrics() {
    return {
      totalQuestions: this.metrics.totalQuestions,
      minigameCount: this.metrics.minigameCount,
      pollCount: this.metrics.pollCount,
      finalSprintQuestions: this.metrics.finalSprintQuestions,
      sawMinigame: this.metrics.sawMinigame,
      sawFinalSprint: this.metrics.sawFinalSprint,
      questionTypes: Array.from(this.metrics.questionTypes),
      categories: Array.from(this.metrics.categories),
      timings: this.metrics.timings,
      scoreboardSnapshots: this.metrics.scoreboardSnapshots,
      ghostRoster: Array.from(this.metrics.ghostRoster),
      finalLeaderboard: this.metrics.finalLeaderboard ?? null,
    };
  }

  async teardown() {
    while (this.cleanupCallbacks.length) {
      const cleanup = this.cleanupCallbacks.pop();
      if (cleanup) {
        await cleanup().catch(() => {});
      }
    }
  }
}
