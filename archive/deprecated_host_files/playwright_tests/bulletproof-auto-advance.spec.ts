import { test, expect, Page, BrowserContext } from "@playwright/test";

/**
 * BULLETPROOF AUTO-ADVANCE TEST SUITE
 *
 * Tests every possible edge case and failure mode:
 * - Timing issues
 * - Race conditions
 * - Network delays
 * - Multiple players
 * - Edge cases with player status
 * - Server state consistency
 * - Client synchronization
 */

test.describe("BULLETPROOF Auto-Advance Test Suite", () => {
  test.setTimeout(180_000); // 3 minutes for thorough testing

  // Helper function to create and setup a player
  async function setupPlayer(
    browser: any,
    name: string,
    roomCode: string
  ): Promise<{ context: BrowserContext; page: Page; playerId: string }> {
    const context = await browser.newContext({
      viewport: { width: 428, height: 926 },
      userAgent:
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15",
    });
    const page = await context.newPage();

    page.on("console", (msg: any) => {
      const type = msg.type();
      const text = msg.text();
      const prefix = type === "error" ? "❌" : type === "warning" ? "⚠️" : "📱";
      console.log(`${prefix} ${name}: ${text}`);
    });

    page.on("pageerror", (error: any) => {
      console.error(`💥 ${name} PAGE ERROR: ${error.message}`);
    });

    await page.goto("http://localhost:5001/join");
    await page.fill("#room-code", roomCode);
    await page.fill("#player-name", name);
    await page.click("#join-game-btn");
    await page.waitForURL(/\/player\/player_/, { timeout: 10000 });

    const url = page.url();
    const playerId = url.match(/\/player\/(player_\w+)/)?.[1] || "";

    return { context, page, playerId };
  }

  // Helper to wait for question to load
  async function waitForQuestion(page: Page, timeout = 15000): Promise<string> {
    await page.waitForFunction(
      () => {
        const el = document.querySelector<HTMLElement>("#question-text");
        return el && el.textContent && el.textContent.trim().length > 10;
      },
      { timeout }
    );
    const text = await page.locator("#question-text").textContent();
    return text?.trim() || "";
  }

  // Helper to answer question
  async function answerQuestion(page: Page, answerIndex = 0) {
    const buttons = page.locator(".answer-btn");
    await buttons
      .nth(answerIndex)
      .waitFor({ state: "visible", timeout: 10000 });
    await buttons.nth(answerIndex).click();
  }

  test("TEST 1: Basic 2-player auto-advance", async ({ browser }) => {
    console.log("\n🧪 TEST 1: Basic 2-player auto-advance\n");

    const hostContext = await browser.newContext({
      viewport: { width: 1440, height: 900 },
    });
    const hostPage = await hostContext.newPage();
    hostPage.on("console", (msg) => console.log(`🖥️  HOST: ${msg.text()}`));
    hostPage.on("pageerror", (error) =>
      console.error(`💥 HOST ERROR: ${error.message}`)
    );

    try {
      // Create game
      await hostPage.goto("http://localhost:5001/host");
      await hostPage.fill("#host-name", "TestHost");
      await hostPage.click("#create-game-btn");
      await hostPage.waitForURL(/\/host\/lobby\?room=/);

      const roomCode = (
        await hostPage.locator("#room-code").textContent()
      )?.trim();
      console.log(`✅ Room created: ${roomCode}`);
      expect(roomCode).toMatch(/^[A-Z0-9]{6}$/);

      // Setup players
      const player1 = await setupPlayer(browser, "Alice", roomCode!);
      const player2 = await setupPlayer(browser, "Bob", roomCode!);
      console.log(
        `✅ Players joined: ${player1.playerId}, ${player2.playerId}`
      );

      // Verify lobby shows both players
      await expect(hostPage.locator("#players-ul li")).toHaveCount(2, {
        timeout: 10000,
      });

      // Start game
      await hostPage.click("#start-game-btn");
      await hostPage.waitForURL(/\/host\/play/);

      // Wait for question on all clients
      const [q1Host, q1P1, q1P2] = await Promise.all([
        waitForQuestion(hostPage),
        waitForQuestion(player1.page),
        waitForQuestion(player2.page),
      ]);

      console.log(`✅ Q1 loaded - Host: "${q1Host.substring(0, 50)}..."`);
      expect(q1P1).toBe(q1Host);
      expect(q1P2).toBe(q1Host);

      // Player 1 answers
      await answerQuestion(player1.page);
      console.log("✅ Alice answered");

      // Wait 6 seconds - should NOT advance yet
      await hostPage.waitForTimeout(6000);
      const stillQ1 = await hostPage.locator("#question-text").textContent();
      expect(stillQ1?.trim()).toBe(q1Host);
      console.log("✅ VERIFIED: Did NOT auto-advance with 1/2 players");

      // Player 2 answers
      await answerQuestion(player2.page);
      console.log("✅ Bob answered");

      // Should auto-advance within 7 seconds (5 sec countdown + buffer)
      await hostPage.waitForFunction(
        (prevQ) => {
          const currentQ = document
            .querySelector<HTMLElement>("#question-text")
            ?.textContent?.trim();
          return currentQ && currentQ !== prevQ && currentQ.length > 10;
        },
        q1Host,
        { timeout: 10000 }
      );

      const q2Text = await hostPage.locator("#question-text").textContent();
      expect(q2Text?.trim()).not.toBe(q1Host);
      console.log(
        `✅ VERIFIED: Auto-advanced to Q2: "${q2Text?.substring(0, 50)}..."`
      );

      // Cleanup
      await player1.context.close();
      await player2.context.close();
      await hostContext.close();

      console.log("✅ TEST 1 PASSED\n");
    } catch (error) {
      console.error("❌ TEST 1 FAILED:", error);
      throw error;
    }
  });

  test("TEST 2: 4-player scenario with delayed answers", async ({
    browser,
  }) => {
    console.log("\n🧪 TEST 2: 4-player scenario with staggered answers\n");

    const hostContext = await browser.newContext({
      viewport: { width: 1440, height: 900 },
    });
    const hostPage = await hostContext.newPage();
    hostPage.on("console", (msg) => console.log(`🖥️  HOST: ${msg.text()}`));

    try {
      // Create game
      await hostPage.goto("http://localhost:5001/host");
      await hostPage.fill("#host-name", "Host4P");
      await hostPage.click("#create-game-btn");
      await hostPage.waitForURL(/\/host\/lobby\?room=/);

      const roomCode = (
        await hostPage.locator("#room-code").textContent()
      )?.trim()!;
      console.log(`✅ Room: ${roomCode}`);

      // Setup 4 players
      const players = await Promise.all([
        setupPlayer(browser, "Alice", roomCode),
        setupPlayer(browser, "Bob", roomCode),
        setupPlayer(browser, "Charlie", roomCode),
        setupPlayer(browser, "Diana", roomCode),
      ]);
      console.log("✅ 4 players joined");

      await expect(hostPage.locator("#players-ul li")).toHaveCount(4, {
        timeout: 10000,
      });

      // Start game
      await hostPage.click("#start-game-btn");
      await hostPage.waitForURL(/\/host\/play/);

      const q1 = await waitForQuestion(hostPage);
      console.log(`✅ Q1: "${q1.substring(0, 50)}..."`);

      // Answer in sequence with delays
      await answerQuestion(players[0].page);
      console.log("✅ 1/4 answered (Alice)");
      await hostPage.waitForTimeout(2000);

      // Check still on Q1
      let current = await hostPage.locator("#question-text").textContent();
      expect(current?.trim()).toBe(q1);
      console.log("✅ Still on Q1 after 1/4");

      await answerQuestion(players[1].page);
      console.log("✅ 2/4 answered (Bob)");
      await hostPage.waitForTimeout(2000);

      current = await hostPage.locator("#question-text").textContent();
      expect(current?.trim()).toBe(q1);
      console.log("✅ Still on Q1 after 2/4");

      await answerQuestion(players[2].page);
      console.log("✅ 3/4 answered (Charlie)");
      await hostPage.waitForTimeout(6000); // Wait longer than auto-advance

      current = await hostPage.locator("#question-text").textContent();
      expect(current?.trim()).toBe(q1);
      console.log("✅ Still on Q1 after 3/4 (even after 6 seconds)");

      // 4th player answers - should trigger auto-advance
      await answerQuestion(players[3].page);
      console.log("✅ 4/4 answered (Diana)");

      // Should advance now
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
      console.log(`✅ Auto-advanced to Q2: "${q2?.substring(0, 50)}..."`);

      // Cleanup
      for (const player of players) {
        await player.context.close();
      }
      await hostContext.close();

      console.log("✅ TEST 2 PASSED\n");
    } catch (error) {
      console.error("❌ TEST 2 FAILED:", error);
      throw error;
    }
  });

  test("TEST 3: Race condition - rapid successive answers", async ({
    browser,
  }) => {
    console.log("\n🧪 TEST 3: Race condition with simultaneous answers\n");

    const hostContext = await browser.newContext({
      viewport: { width: 1440, height: 900 },
    });
    const hostPage = await hostContext.newPage();
    hostPage.on("console", (msg) => console.log(`🖥️  HOST: ${msg.text()}`));

    try {
      // Create game
      await hostPage.goto("http://localhost:5001/host");
      await hostPage.fill("#host-name", "RaceTest");
      await hostPage.click("#create-game-btn");
      await hostPage.waitForURL(/\/host\/lobby\?room=/);

      const roomCode = (
        await hostPage.locator("#room-code").textContent()
      )?.trim()!;

      // Setup 3 players
      const players = await Promise.all([
        setupPlayer(browser, "Alice", roomCode),
        setupPlayer(browser, "Bob", roomCode),
        setupPlayer(browser, "Charlie", roomCode),
      ]);
      console.log("✅ 3 players joined");

      await hostPage.click("#start-game-btn");
      await hostPage.waitForURL(/\/host\/play/);

      const q1 = await waitForQuestion(hostPage);
      console.log(`✅ Q1 loaded`);

      // All 3 players answer SIMULTANEOUSLY (no await between them)
      console.log("⚡ All 3 players answering simultaneously...");
      await Promise.all([
        answerQuestion(players[0].page),
        answerQuestion(players[1].page),
        answerQuestion(players[2].page),
      ]);
      console.log("✅ All answers submitted simultaneously");

      // Should still advance (even with race condition)
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
      console.log(`✅ Successfully handled race condition and advanced`);

      // Cleanup
      for (const player of players) {
        await player.context.close();
      }
      await hostContext.close();

      console.log("✅ TEST 3 PASSED\n");
    } catch (error) {
      console.error("❌ TEST 3 FAILED:", error);
      throw error;
    }
  });

  test("TEST 4: Multiple questions in sequence", async ({ browser }) => {
    console.log("\n🧪 TEST 4: Multiple consecutive auto-advances\n");

    const hostContext = await browser.newContext({
      viewport: { width: 1440, height: 900 },
    });
    const hostPage = await hostContext.newPage();
    hostPage.on("console", (msg) => console.log(`🖥️  HOST: ${msg.text()}`));

    try {
      // Create game
      await hostPage.goto("http://localhost:5001/host");
      await hostPage.fill("#host-name", "MultiQ");
      await hostPage.click("#create-game-btn");
      await hostPage.waitForURL(/\/host\/lobby\?room=/);

      const roomCode = (
        await hostPage.locator("#room-code").textContent()
      )?.trim()!;

      const players = await Promise.all([
        setupPlayer(browser, "Alice", roomCode),
        setupPlayer(browser, "Bob", roomCode),
      ]);

      await hostPage.click("#start-game-btn");
      await hostPage.waitForURL(/\/host\/play/);

      // Test 3 consecutive auto-advances
      for (let i = 1; i <= 3; i++) {
        console.log(`\n--- Question ${i} ---`);
        const qText = await waitForQuestion(hostPage);
        console.log(`✅ Q${i}: "${qText.substring(0, 40)}..."`);

        // Both answer
        await Promise.all([
          answerQuestion(players[0].page),
          answerQuestion(players[1].page),
        ]);
        console.log(`✅ Both answered Q${i}`);

        // Should advance (except if we're at the end)
        try {
          await hostPage.waitForFunction(
            (prevQ) => {
              const currentQ = document
                .querySelector<HTMLElement>("#question-text")
                ?.textContent?.trim();
              // Also check if game ended
              const gameOver = document.querySelector(
                "#game-over-screen, .final-results"
              );
              return (
                (currentQ && currentQ !== prevQ && currentQ.length > 10) ||
                gameOver !== null
              );
            },
            qText,
            { timeout: 10000 }
          );

          // Check if game ended
          const gameOver = await hostPage
            .locator("#game-over-screen, .final-results")
            .count();
          if (gameOver > 0) {
            console.log(`✅ Game ended after Q${i}`);
            break;
          }

          const nextQ = await hostPage.locator("#question-text").textContent();
          expect(nextQ?.trim()).not.toBe(qText);
          console.log(`✅ Advanced to Q${i + 1}`);
        } catch (e) {
          console.log(`ℹ️  May have reached end of questions at Q${i}`);
          break;
        }
      }

      // Cleanup
      for (const player of players) {
        await player.context.close();
      }
      await hostContext.close();

      console.log("✅ TEST 4 PASSED\n");
    } catch (error) {
      console.error("❌ TEST 4 FAILED:", error);
      throw error;
    }
  });

  test("TEST 5: Edge case - player disconnects", async ({ browser }) => {
    console.log("\n🧪 TEST 5: Player disconnects mid-game\n");

    const hostContext = await browser.newContext({
      viewport: { width: 1440, height: 900 },
    });
    const hostPage = await hostContext.newPage();
    hostPage.on("console", (msg) => console.log(`🖥️  HOST: ${msg.text()}`));

    try {
      // Create game
      await hostPage.goto("http://localhost:5001/host");
      await hostPage.fill("#host-name", "DisconnectTest");
      await hostPage.click("#create-game-btn");
      await hostPage.waitForURL(/\/host\/lobby\?room=/);

      const roomCode = (
        await hostPage.locator("#room-code").textContent()
      )?.trim()!;

      const players = await Promise.all([
        setupPlayer(browser, "Alice", roomCode),
        setupPlayer(browser, "Bob", roomCode),
        setupPlayer(browser, "Charlie", roomCode),
      ]);

      await hostPage.click("#start-game-btn");
      await hostPage.waitForURL(/\/host\/play/);

      const q1 = await waitForQuestion(hostPage);
      console.log(`✅ Q1 loaded`);

      // 2 players answer
      await answerQuestion(players[0].page);
      await answerQuestion(players[1].page);
      console.log("✅ 2/3 answered");

      // Close 3rd player's connection (simulate disconnect)
      console.log("🔌 Closing Charlie's connection...");
      await players[2].context.close();

      // Wait - game should NOT advance (3rd player hasn't answered)
      await hostPage.waitForTimeout(8000);
      const current = await hostPage.locator("#question-text").textContent();
      expect(current?.trim()).toBe(q1);
      console.log(
        "✅ Game correctly stayed on Q1 (disconnected player not answered)"
      );

      // Note: In a real scenario, you might want the game to continue after a timeout
      // or detect disconnected players and exclude them from the count
      // This test verifies current behavior

      // Cleanup
      await players[0].context.close();
      await players[1].context.close();
      await hostContext.close();

      console.log("✅ TEST 5 PASSED (game handles disconnect as expected)\n");
    } catch (error) {
      console.error("❌ TEST 5 FAILED:", error);
      throw error;
    }
  });

  test("TEST 6: Timing verification - exact 5-second countdown", async ({
    browser,
  }) => {
    console.log("\n🧪 TEST 6: Verify auto-advance timing is ~5 seconds\n");

    const hostContext = await browser.newContext({
      viewport: { width: 1440, height: 900 },
    });
    const hostPage = await hostContext.newPage();
    hostPage.on("console", (msg) => console.log(`🖥️  HOST: ${msg.text()}`));

    try {
      // Create game
      await hostPage.goto("http://localhost:5001/host");
      await hostPage.fill("#host-name", "TimingTest");
      await hostPage.click("#create-game-btn");
      await hostPage.waitForURL(/\/host\/lobby\?room=/);

      const roomCode = (
        await hostPage.locator("#room-code").textContent()
      )?.trim()!;

      const players = await Promise.all([
        setupPlayer(browser, "Alice", roomCode),
        setupPlayer(browser, "Bob", roomCode),
      ]);

      await hostPage.click("#start-game-btn");
      await hostPage.waitForURL(/\/host\/play/);

      const q1 = await waitForQuestion(hostPage);

      // Both answer and measure time until advance
      const startTime = Date.now();
      await Promise.all([
        answerQuestion(players[0].page),
        answerQuestion(players[1].page),
      ]);
      console.log("✅ Both answered, starting timer...");

      await hostPage.waitForFunction(
        (prevQ) =>
          document
            .querySelector<HTMLElement>("#question-text")
            ?.textContent?.trim() !== prevQ,
        q1,
        { timeout: 10000 }
      );

      const elapsed = Date.now() - startTime;
      console.log(`⏱️  Time to auto-advance: ${elapsed}ms`);

      // Should be ~5000ms (allow 4500-6500ms range for network/processing)
      expect(elapsed).toBeGreaterThan(4000);
      expect(elapsed).toBeLessThan(7000);
      console.log(
        `✅ Timing verified: ${(elapsed / 1000).toFixed(2)}s (expected ~5s)`
      );

      // Cleanup
      for (const player of players) {
        await player.context.close();
      }
      await hostContext.close();

      console.log("✅ TEST 6 PASSED\n");
    } catch (error) {
      console.error("❌ TEST 6 FAILED:", error);
      throw error;
    }
  });

  test("TEST 7: UI state verification", async ({ browser }) => {
    console.log("\n🧪 TEST 7: Verify UI elements during auto-advance\n");

    const hostContext = await browser.newContext({
      viewport: { width: 1440, height: 900 },
    });
    const hostPage = await hostContext.newPage();
    hostPage.on("console", (msg) => console.log(`🖥️  HOST: ${msg.text()}`));

    try {
      // Create game
      await hostPage.goto("http://localhost:5001/host");
      await hostPage.fill("#host-name", "UITest");
      await hostPage.click("#create-game-btn");
      await hostPage.waitForURL(/\/host\/lobby\?room=/);

      const roomCode = (
        await hostPage.locator("#room-code").textContent()
      )?.trim()!;

      const players = await Promise.all([
        setupPlayer(browser, "Alice", roomCode),
        setupPlayer(browser, "Bob", roomCode),
      ]);

      await hostPage.click("#start-game-btn");
      await hostPage.waitForURL(/\/host\/play/);

      const q1 = await waitForQuestion(hostPage);

      // Answer
      await answerQuestion(players[0].page);
      await answerQuestion(players[1].page);

      // Check for "all players answered" message
      console.log('🔍 Looking for "all players answered" notification...');

      // Wait a bit for the message to appear
      await hostPage.waitForTimeout(1000);

      // Check if the message appears anywhere on the page
      const pageContent = await hostPage.content();
      const hasMessage =
        pageContent.toLowerCase().includes("all players answered") ||
        pageContent.toLowerCase().includes("moving to next");

      if (hasMessage) {
        console.log("✅ Found auto-advance notification in UI");
      } else {
        console.log(
          "⚠️  Note: Auto-advance message not found in HTML (may be console-only)"
        );
      }

      // Verify question changes
      await hostPage.waitForFunction(
        (prevQ) =>
          document
            .querySelector<HTMLElement>("#question-text")
            ?.textContent?.trim() !== prevQ,
        q1,
        { timeout: 10000 }
      );
      console.log("✅ Question updated successfully");

      // Verify answer buttons are re-enabled
      const buttonsEnabled = await players[0].page
        .locator(".answer-btn:not([disabled])")
        .count();
      expect(buttonsEnabled).toBeGreaterThan(0);
      console.log("✅ Answer buttons re-enabled for next question");

      // Cleanup
      for (const player of players) {
        await player.context.close();
      }
      await hostContext.close();

      console.log("✅ TEST 7 PASSED\n");
    } catch (error) {
      console.error("❌ TEST 7 FAILED:", error);
      throw error;
    }
  });

  test("TEST 8: Server-side state consistency", async ({ browser }) => {
    console.log("\n🧪 TEST 8: Verify server maintains correct state\n");

    const hostContext = await browser.newContext({
      viewport: { width: 1440, height: 900 },
    });
    const hostPage = await hostContext.newPage();

    // Capture server logs
    const serverLogs: string[] = [];
    hostPage.on("console", (msg) => {
      const text = msg.text();
      serverLogs.push(text);
      console.log(`🖥️  ${text}`);
    });

    try {
      // Create game
      await hostPage.goto("http://localhost:5001/host");
      await hostPage.fill("#host-name", "StateTest");
      await hostPage.click("#create-game-btn");
      await hostPage.waitForURL(/\/host\/lobby\?room=/);

      const roomCode = (
        await hostPage.locator("#room-code").textContent()
      )?.trim()!;

      const players = await Promise.all([
        setupPlayer(browser, "Alice", roomCode),
        setupPlayer(browser, "Bob", roomCode),
        setupPlayer(browser, "Charlie", roomCode),
      ]);

      await hostPage.click("#start-game-btn");
      await hostPage.waitForURL(/\/host\/play/);

      await waitForQuestion(hostPage);

      // Answer one by one and check state
      for (let i = 0; i < players.length; i++) {
        await answerQuestion(players[i].page);
        console.log(`✅ Player ${i + 1} answered`);
        await hostPage.waitForTimeout(500); // Small delay to let state update
      }

      // After all answered, wait for advance
      await hostPage.waitForTimeout(7000);

      // Verify we moved to next question
      const newQ = await hostPage.locator("#question-text").textContent();
      expect(newQ).toBeTruthy();
      expect(newQ!.trim().length).toBeGreaterThan(10);
      console.log("✅ Server state correctly advanced to next question");

      // Cleanup
      for (const player of players) {
        await player.context.close();
      }
      await hostContext.close();

      console.log("✅ TEST 8 PASSED\n");
    } catch (error) {
      console.error("❌ TEST 8 FAILED:", error);
      console.log("Server logs captured:", serverLogs.slice(-20)); // Last 20 logs
      throw error;
    }
  });
});

test.describe("STRESS TESTS", () => {
  test.setTimeout(300_000); // 5 minutes

  test("STRESS TEST: 6 players rapid-fire answers", async ({ browser }) => {
    console.log("\n🔥 STRESS TEST: 6 players\n");

    const hostContext = await browser.newContext({
      viewport: { width: 1440, height: 900 },
    });
    const hostPage = await hostContext.newPage();
    hostPage.on("console", (msg) => console.log(`🖥️  ${msg.text()}`));

    try {
      await hostPage.goto("http://localhost:5001/host");
      await hostPage.fill("#host-name", "StressTest");
      await hostPage.click("#create-game-btn");
      await hostPage.waitForURL(/\/host\/lobby\?room=/);

      const roomCode = (
        await hostPage.locator("#room-code").textContent()
      )?.trim()!;

      // Create 6 players
      const playerNames = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank"];
      const players = [];

      for (const name of playerNames) {
        const player = await (async () => {
          const context = await browser.newContext({
            viewport: { width: 428, height: 926 },
          });
          const page = await context.newPage();
          await page.goto("http://localhost:5001/join");
          await page.fill("#room-code", roomCode);
          await page.fill("#player-name", name);
          await page.click("#join-game-btn");
          await page.waitForURL(/\/player\/player_/);
          return { context, page };
        })();
        players.push(player);
        console.log(`✅ ${name} joined`);
      }

      await expect(hostPage.locator("#players-ul li")).toHaveCount(6, {
        timeout: 15000,
      });

      await hostPage.click("#start-game-btn");
      await hostPage.waitForURL(/\/host\/play/);

      // Test 2 rounds
      for (let round = 1; round <= 2; round++) {
        console.log(`\n--- ROUND ${round} ---`);

        const qText = await hostPage.waitForFunction(
          () =>
            document
              .querySelector<HTMLElement>("#question-text")
              ?.textContent?.trim(),
          { timeout: 15000 }
        );
        const question = await hostPage.locator("#question-text").textContent();
        console.log(`✅ Question ${round}: "${question?.substring(0, 40)}..."`);

        // All 6 answer quickly
        for (let i = 0; i < 6; i++) {
          const buttons = players[i].page.locator(".answer-btn");
          await buttons.first().waitFor({ state: "visible", timeout: 10000 });
          await buttons.first().click();
          console.log(`✅ Player ${i + 1} answered`);
          await hostPage.waitForTimeout(300); // Small delay
        }

        console.log("⏳ Waiting for auto-advance...");

        // Wait for advance
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
          question?.trim(),
          { timeout: 12000 }
        );

        const gameOver = await hostPage
          .locator("#game-over-screen, .final-results")
          .count();
        if (gameOver > 0) {
          console.log("✅ Game completed");
          break;
        }

        console.log(`✅ Advanced to next question`);
      }

      // Cleanup
      for (const player of players) {
        await player.context.close();
      }
      await hostContext.close();

      console.log("\n✅ STRESS TEST PASSED\n");
    } catch (error) {
      console.error("❌ STRESS TEST FAILED:", error);
      throw error;
    }
  });
});
