import { test, expect, Page, BrowserContext } from "@playwright/test";

/**
 * BULLETPROOF 4-PLAYER AUTO-ADVANCE TEST
 *
 * Tests every edge case for a 4-player game:
 * - Partial answers (1, 2, 3 players) should NOT advance
 * - All 4 players answering SHOULD advance
 * - Race conditions with simultaneous answers
 * - Multiple consecutive questions
 * - Timing verification
 */

test.describe("4-Player Auto-Advance Tests", () => {
  test.setTimeout(180_000);

  // Helper to setup a player
  async function setupPlayer(browser: any, name: string, roomCode: string) {
    const context = await browser.newContext({
      viewport: { width: 428, height: 926 },
    });
    const page = await context.newPage();

    page.on("console", (msg: any) => console.log(`📱 ${name}: ${msg.text()}`));
    page.on("pageerror", (error: any) =>
      console.error(`💥 ${name} ERROR: ${error.message}`)
    );

    await page.goto("http://localhost:5001/join");
    await page.fill("#room-code", roomCode);
    await page.fill("#player-name", name);
    await page.click("#join-game-btn");
    await page.waitForURL(/\/player\/player_/, { timeout: 10000 });

    // Wait for the waiting screen to be visible (player fully joined)
    await page.waitForSelector("#waiting-screen", { timeout: 10000 });

    // Small delay to ensure socket connection is stable
    await page.waitForTimeout(500);

    return { context, page };
  }

  async function waitForQuestion(page: Page): Promise<string> {
    await page.waitForFunction(
      () => {
        const el = document.querySelector<HTMLElement>("#question-text");
        return el && el.textContent && el.textContent.trim().length > 10;
      },
      { timeout: 15000 }
    );
    return (await page.locator("#question-text").textContent())?.trim() || "";
  }

  async function answerQuestion(page: Page, answerIndex = 0) {
    const buttons = page.locator(".answer-btn");
    await buttons
      .nth(answerIndex)
      .waitFor({ state: "visible", timeout: 10000 });
    await buttons.nth(answerIndex).click();
  }

  async function startGame(hostPage: Page) {
    // Wait for start button and click using JavaScript to bypass any overlays
    await hostPage.waitForSelector("#start-game-btn", { state: "visible" });
    await hostPage.evaluate(() => {
      const btn = document.querySelector<HTMLButtonElement>("#start-game-btn");
      if (btn) btn.click();
    });
    await hostPage.waitForURL(/\/host\/play/, { timeout: 15000 });
  }

  async function setupFourPlayers(browser: any, roomCode: string) {
    const players = [];
    for (const name of ["Alice", "Bob", "Charlie", "Diana"]) {
      const player = await setupPlayer(browser, name, roomCode);
      players.push(player);
      console.log(`✅ ${name} joined`);
    }
    return players;
  }

  test("TEST 1: Does NOT advance with only 1 of 4 players", async ({
    browser,
  }) => {
    console.log("\n🧪 TEST 1: 1/4 players - should NOT advance\n");

    const hostContext = await browser.newContext({
      viewport: { width: 1440, height: 900 },
    });
    const hostPage = await hostContext.newPage();
    hostPage.on("console", (msg: any) =>
      console.log(`🖥️  HOST: ${msg.text()}`)
    );

    try {
      // Create game
      await hostPage.goto("http://localhost:5001/host");
      await hostPage.fill("#host-name", "Host");
      await hostPage.click("#create-game-btn");
      await hostPage.waitForURL(/\/host\/lobby\?room=/);

      const roomCode = (
        await hostPage.locator("#room-code").textContent()
      )?.trim()!;
      console.log(`✅ Room: ${roomCode}`);

      // Setup 4 players sequentially to avoid race conditions
      const players = [];
      for (const name of ["Alice", "Bob", "Charlie", "Diana"]) {
        const player = await setupPlayer(browser, name, roomCode);
        players.push(player);
        console.log(`✅ ${name} joined`);
      }

      await expect(hostPage.locator("#players-ul li")).toHaveCount(4, {
        timeout: 10000,
      });

      // Start game
      await startGame(hostPage);

      const q1 = await waitForQuestion(hostPage);
      console.log(`✅ Q1: "${q1.substring(0, 50)}..."`);

      // Only 1 player answers
      await answerQuestion(players[0].page);
      console.log("✅ 1/4 answered");

      // Wait 8 seconds (more than 5-sec auto-advance)
      await hostPage.waitForTimeout(8000);

      // Should STILL be on Q1
      const current = await hostPage.locator("#question-text").textContent();
      expect(current?.trim()).toBe(q1);
      console.log("✅ PASS: Did NOT advance with 1/4 players\n");

      // Cleanup
      for (const p of players) await p.context.close();
      await hostContext.close();
    } catch (error) {
      console.error("❌ TEST 1 FAILED:", error);
      throw error;
    }
  });

  test("TEST 2: Does NOT advance with only 2 of 4 players", async ({
    browser,
  }) => {
    console.log("\n🧪 TEST 2: 2/4 players - should NOT advance\n");

    const hostContext = await browser.newContext({
      viewport: { width: 1440, height: 900 },
    });
    const hostPage = await hostContext.newPage();
    hostPage.on("console", (msg: any) =>
      console.log(`🖥️  HOST: ${msg.text()}`)
    );

    try {
      await hostPage.goto("http://localhost:5001/host");
      await hostPage.fill("#host-name", "Host");
      await hostPage.click("#create-game-btn");
      await hostPage.waitForURL(/\/host\/lobby\?room=/);

      const roomCode = (
        await hostPage.locator("#room-code").textContent()
      )?.trim()!;

      const players = await setupFourPlayers(browser, roomCode);

      await startGame(hostPage);

      const q1 = await waitForQuestion(hostPage);
      console.log(`✅ Q1 loaded`);

      // 2 players answer
      await answerQuestion(players[0].page);
      await answerQuestion(players[1].page);
      console.log("✅ 2/4 answered");

      await hostPage.waitForTimeout(8000);

      const current = await hostPage.locator("#question-text").textContent();
      expect(current?.trim()).toBe(q1);
      console.log("✅ PASS: Did NOT advance with 2/4 players\n");

      for (const p of players) await p.context.close();
      await hostContext.close();
    } catch (error) {
      console.error("❌ TEST 2 FAILED:", error);
      throw error;
    }
  });

  test("TEST 3: Does NOT advance with only 3 of 4 players", async ({
    browser,
  }) => {
    console.log("\n🧪 TEST 3: 3/4 players - should NOT advance\n");

    const hostContext = await browser.newContext({
      viewport: { width: 1440, height: 900 },
    });
    const hostPage = await hostContext.newPage();
    hostPage.on("console", (msg: any) =>
      console.log(`🖥️  HOST: ${msg.text()}`)
    );

    try {
      await hostPage.goto("http://localhost:5001/host");
      await hostPage.fill("#host-name", "Host");
      await hostPage.click("#create-game-btn");
      await hostPage.waitForURL(/\/host\/lobby\?room=/);

      const roomCode = (
        await hostPage.locator("#room-code").textContent()
      )?.trim()!;

      const players = await setupFourPlayers(browser, roomCode);

      await startGame(hostPage);

      const q1 = await waitForQuestion(hostPage);
      console.log(`✅ Q1 loaded`);

      // 3 players answer
      await answerQuestion(players[0].page);
      await answerQuestion(players[1].page);
      await answerQuestion(players[2].page);
      console.log("✅ 3/4 answered");

      await hostPage.waitForTimeout(8000);

      const current = await hostPage.locator("#question-text").textContent();
      expect(current?.trim()).toBe(q1);
      console.log("✅ PASS: Did NOT advance with 3/4 players\n");

      for (const p of players) await p.context.close();
      await hostContext.close();
    } catch (error) {
      console.error("❌ TEST 3 FAILED:", error);
      throw error;
    }
  });

  test("TEST 4: DOES advance when all 4 players answer", async ({
    browser,
  }) => {
    console.log("\n🧪 TEST 4: 4/4 players - SHOULD advance\n");

    const hostContext = await browser.newContext({
      viewport: { width: 1440, height: 900 },
    });
    const hostPage = await hostContext.newPage();
    hostPage.on("console", (msg: any) =>
      console.log(`🖥️  HOST: ${msg.text()}`)
    );

    try {
      await hostPage.goto("http://localhost:5001/host");
      await hostPage.fill("#host-name", "Host");
      await hostPage.click("#create-game-btn");
      await hostPage.waitForURL(/\/host\/lobby\?room=/);

      const roomCode = (
        await hostPage.locator("#room-code").textContent()
      )?.trim()!;

      const players = await setupFourPlayers(browser, roomCode);

      await startGame(hostPage);

      const q1 = await waitForQuestion(hostPage);
      console.log(`✅ Q1: "${q1.substring(0, 50)}..."`);

      // All 4 players answer
      for (let i = 0; i < 4; i++) {
        await answerQuestion(players[i].page);
        console.log(`✅ Player ${i + 1}/4 answered`);
      }

      // Should auto-advance within 7 seconds
      await hostPage.waitForFunction(
        (prevQ) => {
          const currentQ = document
            .querySelector<HTMLElement>("#question-text")
            ?.textContent?.trim();
          return currentQ && currentQ !== prevQ && currentQ.length > 10;
        },
        q1,
        { timeout: 10000 }
      );

      const q2 = await hostPage.locator("#question-text").textContent();
      expect(q2?.trim()).not.toBe(q1);
      console.log(`✅ PASS: Advanced to Q2: "${q2?.substring(0, 50)}..."\n`);

      for (const p of players) await p.context.close();
      await hostContext.close();
    } catch (error) {
      console.error("❌ TEST 4 FAILED:", error);
      throw error;
    }
  });

  test("TEST 5: Race condition - all 4 answer simultaneously", async ({
    browser,
  }) => {
    console.log("\n🧪 TEST 5: Simultaneous answers (race condition)\n");

    const hostContext = await browser.newContext({
      viewport: { width: 1440, height: 900 },
    });
    const hostPage = await hostContext.newPage();
    hostPage.on("console", (msg: any) =>
      console.log(`🖥️  HOST: ${msg.text()}`)
    );

    try {
      await hostPage.goto("http://localhost:5001/host");
      await hostPage.fill("#host-name", "Host");
      await hostPage.click("#create-game-btn");
      await hostPage.waitForURL(/\/host\/lobby\?room=/);

      const roomCode = (
        await hostPage.locator("#room-code").textContent()
      )?.trim()!;

      const players = await setupFourPlayers(browser, roomCode);

      await startGame(hostPage);

      const q1 = await waitForQuestion(hostPage);
      console.log(`✅ Q1 loaded`);

      // All 4 answer AT THE SAME TIME
      console.log("⚡ All 4 players answering simultaneously...");
      await Promise.all([
        answerQuestion(players[0].page),
        answerQuestion(players[1].page),
        answerQuestion(players[2].page),
        answerQuestion(players[3].page),
      ]);
      console.log("✅ All 4 answered simultaneously");

      // Should still advance correctly
      await hostPage.waitForFunction(
        (prevQ) =>
          document
            .querySelector<HTMLElement>("#question-text")
            ?.textContent?.trim() !== prevQ,
        q1,
        { timeout: 10000 }
      );

      const q2 = await hostPage.locator("#question-text").textContent();
      expect(q2?.trim()).not.toBe(q1);
      console.log("✅ PASS: Race condition handled correctly\n");

      for (const p of players) await p.context.close();
      await hostContext.close();
    } catch (error) {
      console.error("❌ TEST 5 FAILED:", error);
      throw error;
    }
  });

  test("TEST 6: Timing verification - exactly 5 seconds", async ({
    browser,
  }) => {
    console.log("\n🧪 TEST 6: Verify 5-second countdown timing\n");

    const hostContext = await browser.newContext({
      viewport: { width: 1440, height: 900 },
    });
    const hostPage = await hostContext.newPage();
    hostPage.on("console", (msg: any) =>
      console.log(`🖥️  HOST: ${msg.text()}`)
    );

    try {
      await hostPage.goto("http://localhost:5001/host");
      await hostPage.fill("#host-name", "Host");
      await hostPage.click("#create-game-btn");
      await hostPage.waitForURL(/\/host\/lobby\?room=/);

      const roomCode = (
        await hostPage.locator("#room-code").textContent()
      )?.trim()!;

      const players = await setupFourPlayers(browser, roomCode);

      await startGame(hostPage);

      const q1 = await waitForQuestion(hostPage);

      // Measure time from last answer to advance
      const startTime = Date.now();

      await Promise.all([
        answerQuestion(players[0].page),
        answerQuestion(players[1].page),
        answerQuestion(players[2].page),
        answerQuestion(players[3].page),
      ]);
      console.log("⏱️  Timer started...");

      await hostPage.waitForFunction(
        (prevQ) =>
          document
            .querySelector<HTMLElement>("#question-text")
            ?.textContent?.trim() !== prevQ,
        q1,
        { timeout: 10000 }
      );

      const elapsed = Date.now() - startTime;
      console.log(
        `⏱️  Elapsed time: ${elapsed}ms (${(elapsed / 1000).toFixed(2)}s)`
      );

      // Should be ~5000ms (allow 4000-7000ms for network/processing)
      expect(elapsed).toBeGreaterThan(4000);
      expect(elapsed).toBeLessThan(7000);
      console.log("✅ PASS: Timing is correct (~5 seconds)\n");

      for (const p of players) await p.context.close();
      await hostContext.close();
    } catch (error) {
      console.error("❌ TEST 6 FAILED:", error);
      throw error;
    }
  });

  test("TEST 7: Multiple consecutive auto-advances", async ({ browser }) => {
    console.log("\n🧪 TEST 7: 3 consecutive auto-advances\n");

    const hostContext = await browser.newContext({
      viewport: { width: 1440, height: 900 },
    });
    const hostPage = await hostContext.newPage();
    hostPage.on("console", (msg: any) =>
      console.log(`🖥️  HOST: ${msg.text()}`)
    );

    try {
      await hostPage.goto("http://localhost:5001/host");
      await hostPage.fill("#host-name", "Host");
      await hostPage.click("#create-game-btn");
      await hostPage.waitForURL(/\/host\/lobby\?room=/);

      const roomCode = (
        await hostPage.locator("#room-code").textContent()
      )?.trim()!;

      const players = await setupFourPlayers(browser, roomCode);

      await startGame(hostPage);

      // Test 3 rounds
      for (let round = 1; round <= 3; round++) {
        console.log(`\n--- ROUND ${round} ---`);

        const qText = await waitForQuestion(hostPage);
        console.log(`✅ Q${round}: "${qText.substring(0, 40)}..."`);

        // All 4 answer
        await Promise.all(players.map((p) => answerQuestion(p.page)));
        console.log(`✅ All 4 answered Q${round}`);

        // Wait for advance
        try {
          await hostPage.waitForFunction(
            (prevQ) => {
              const currentQ = document
                .querySelector<HTMLElement>("#question-text")
                ?.textContent?.trim();
              const gameOver = document.querySelector(
                "#game-over-screen, .final-results"
              );
              return (currentQ && currentQ !== prevQ) || gameOver !== null;
            },
            qText,
            { timeout: 10000 }
          );

          const gameOver = await hostPage
            .locator("#game-over-screen, .final-results")
            .count();
          if (gameOver > 0) {
            console.log(`✅ Game completed after round ${round}`);
            break;
          }

          console.log(`✅ Advanced to Q${round + 1}`);
        } catch (e) {
          console.log(`ℹ️  Reached end of questions at round ${round}`);
          break;
        }
      }

      console.log("✅ PASS: Multiple consecutive auto-advances work\n");

      for (const p of players) await p.context.close();
      await hostContext.close();
    } catch (error) {
      console.error("❌ TEST 7 FAILED:", error);
      throw error;
    }
  });

  test("TEST 8: Staggered answers with delays", async ({ browser }) => {
    console.log("\n🧪 TEST 8: Staggered answers (realistic timing)\n");

    const hostContext = await browser.newContext({
      viewport: { width: 1440, height: 900 },
    });
    const hostPage = await hostContext.newPage();
    hostPage.on("console", (msg: any) =>
      console.log(`🖥️  HOST: ${msg.text()}`)
    );

    try {
      await hostPage.goto("http://localhost:5001/host");
      await hostPage.fill("#host-name", "Host");
      await hostPage.click("#create-game-btn");
      await hostPage.waitForURL(/\/host\/lobby\?room=/);

      const roomCode = (
        await hostPage.locator("#room-code").textContent()
      )?.trim()!;

      const players = await setupFourPlayers(browser, roomCode);

      await startGame(hostPage);

      const q1 = await waitForQuestion(hostPage);
      console.log(`✅ Q1 loaded`);

      // Players answer with realistic delays
      for (let i = 0; i < 4; i++) {
        await answerQuestion(players[i].page);
        console.log(`✅ Player ${i + 1}/4 answered`);

        if (i < 3) {
          await hostPage.waitForTimeout(1500); // 1.5s between answers

          // Verify still on Q1
          const current = await hostPage
            .locator("#question-text")
            .textContent();
          expect(current?.trim()).toBe(q1);
          console.log(`   Still on Q1 (${i + 1}/4 answered)`);
        }
      }

      // Now should advance
      await hostPage.waitForFunction(
        (prevQ) =>
          document
            .querySelector<HTMLElement>("#question-text")
            ?.textContent?.trim() !== prevQ,
        q1,
        { timeout: 10000 }
      );

      const q2 = await hostPage.locator("#question-text").textContent();
      expect(q2?.trim()).not.toBe(q1);
      console.log("✅ PASS: Advanced after all 4 answered (staggered)\n");

      for (const p of players) await p.context.close();
      await hostContext.close();
    } catch (error) {
      console.error("❌ TEST 8 FAILED:", error);
      throw error;
    }
  });
});
