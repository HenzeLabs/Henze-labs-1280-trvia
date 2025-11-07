import { test, expect } from "@playwright/test";

test.describe("Auto-Advance Fix Validation", () => {
  test.setTimeout(120_000);

  test("should NOT auto-advance when only ONE player answers", async ({
    browser,
  }) => {
    // Create 3 contexts: host + 2 players
    const hostContext = await browser.newContext({
      viewport: { width: 1440, height: 900 },
    });
    const player1Context = await browser.newContext({
      viewport: { width: 428, height: 926 },
    });
    const player2Context = await browser.newContext({
      viewport: { width: 428, height: 926 },
    });

    const hostPage = await hostContext.newPage();
    const player1Page = await player1Context.newPage();
    const player2Page = await player2Context.newPage();

    // Enable console logging for debugging
    hostPage.on("console", (msg) => console.log(`🖥️  HOST: ${msg.text()}`));
    player1Page.on("console", (msg) =>
      console.log(`👤 PLAYER1: ${msg.text()}`)
    );
    player2Page.on("console", (msg) =>
      console.log(`👤 PLAYER2: ${msg.text()}`)
    );

    try {
      // Step 1: Host creates game
      console.log("\n📍 Step 1: Host creating game...");
      await hostPage.goto("http://localhost:5001/host");
      await hostPage.fill("#host-name", "TestHost");
      await hostPage.click("#create-game-btn");
      await hostPage.waitForURL(/\/host\/lobby\?room=/);

      const roomCode = (
        await hostPage.locator("#room-code").textContent()
      )?.trim();
      console.log(`✅ Room created: ${roomCode}`);

      // Step 2: Players join
      console.log("\n📍 Step 2: Players joining...");

      await player1Page.goto("http://localhost:5001/join");
      await player1Page.fill("#room-code", roomCode!);
      await player1Page.fill("#player-name", "Alice");
      await player1Page.click("#join-game-btn");
      await player1Page.waitForURL(/\/player\/player_/);
      console.log("✅ Alice joined");

      await player2Page.goto("http://localhost:5001/join");
      await player2Page.fill("#room-code", roomCode!);
      await player2Page.fill("#player-name", "Bob");
      await player2Page.click("#join-game-btn");
      await player2Page.waitForURL(/\/player\/player_/);
      console.log("✅ Bob joined");

      await expect(hostPage.locator("#players-ul li")).toHaveCount(2, {
        timeout: 10_000,
      });

      // Step 3: Start game
      console.log("\n📍 Step 3: Starting game...");
      await hostPage.click("#start-game-btn");
      await hostPage.waitForURL(/\/host\/play/);

      // Wait for first question to load on all clients
      await Promise.all([
        hostPage.waitForFunction(
          () =>
            document
              .querySelector<HTMLElement>("#question-text")
              ?.textContent?.trim()?.length! > 0,
          { timeout: 15_000 }
        ),
        player1Page.waitForFunction(
          () =>
            document
              .querySelector<HTMLElement>("#question-text")
              ?.textContent?.trim()?.length! > 0,
          { timeout: 15_000 }
        ),
        player2Page.waitForFunction(
          () =>
            document
              .querySelector<HTMLElement>("#question-text")
              ?.textContent?.trim()?.length! > 0,
          { timeout: 15_000 }
        ),
      ]);

      const question1Text = await hostPage
        .locator("#question-text")
        .textContent();
      console.log(
        `✅ Question 1 loaded: "${question1Text?.substring(0, 60)}..."`
      );

      // Step 4: ONLY Player 1 answers (Player 2 waits)
      console.log("\n📍 Step 4: Only Alice answers (Bob waits)...");

      const player1Buttons = player1Page.locator(".answer-btn");
      await player1Buttons
        .first()
        .waitFor({ state: "visible", timeout: 10_000 });
      await player1Buttons.first().click();
      console.log("✅ Alice answered");

      // Step 5: Verify NO auto-advance happens
      console.log("\n📍 Step 5: Verifying game does NOT auto-advance...");

      // Wait 8 seconds (more than the 5-second auto-advance delay)
      await hostPage.waitForTimeout(8000);

      // Check that we're STILL on the same question
      const currentQuestionText = await hostPage
        .locator("#question-text")
        .textContent();
      console.log(
        `Current question: "${currentQuestionText?.substring(0, 60)}..."`
      );

      // ASSERT: Question should NOT have changed
      expect(currentQuestionText).toBe(question1Text);
      console.log("✅ PASS: Game did NOT auto-advance with only 1 answer");

      // Step 6: Now Player 2 answers - should trigger auto-advance
      console.log(
        "\n📍 Step 6: Bob now answers - should trigger auto-advance..."
      );

      const player2Buttons = player2Page.locator(".answer-btn");
      await player2Buttons
        .first()
        .waitFor({ state: "visible", timeout: 10_000 });
      await player2Buttons.first().click();
      console.log("✅ Bob answered");

      // Step 7: Wait for auto-advance to happen
      console.log(
        "\n📍 Step 7: Waiting for auto-advance (all players answered)..."
      );

      await hostPage.waitForFunction(
        (previousText) => {
          const el = document.querySelector<HTMLElement>("#question-text");
          const currentText = el?.textContent?.trim();
          return (
            currentText &&
            currentText !== previousText &&
            currentText.length > 0
          );
        },
        question1Text?.trim(),
        { timeout: 15_000 }
      );

      const question2Text = await hostPage
        .locator("#question-text")
        .textContent();
      console.log(
        `✅ Question 2 loaded: "${question2Text?.substring(0, 60)}..."`
      );

      // ASSERT: Question should have changed
      expect(question2Text).not.toBe(question1Text);
      console.log("✅ PASS: Game auto-advanced after ALL players answered");

      console.log("\n🎉 SUCCESS: Auto-advance fix validated!");
      console.log("   ✓ Does NOT advance with only 1 player answering");
      console.log("   ✓ DOES advance when all players answer");
    } finally {
      await hostContext.close();
      await player1Context.close();
      await player2Context.close();
    }
  });

  test("should handle 3+ players correctly", async ({ browser }) => {
    const hostContext = await browser.newContext({
      viewport: { width: 1440, height: 900 },
    });
    const player1Context = await browser.newContext({
      viewport: { width: 428, height: 926 },
    });
    const player2Context = await browser.newContext({
      viewport: { width: 428, height: 926 },
    });
    const player3Context = await browser.newContext({
      viewport: { width: 428, height: 926 },
    });

    const hostPage = await hostContext.newPage();
    const player1Page = await player1Context.newPage();
    const player2Page = await player2Context.newPage();
    const player3Page = await player3Context.newPage();

    hostPage.on("console", (msg) => console.log(`🖥️  HOST: ${msg.text()}`));

    try {
      // Create game
      console.log("\n📍 Creating game with 3 players...");
      await hostPage.goto("http://localhost:5001/host");
      await hostPage.fill("#host-name", "TestHost");
      await hostPage.click("#create-game-btn");
      await hostPage.waitForURL(/\/host\/lobby\?room=/);

      const roomCode = (
        await hostPage.locator("#room-code").textContent()
      )?.trim();

      // All 3 players join
      await player1Page.goto("http://localhost:5001/join");
      await player1Page.fill("#room-code", roomCode!);
      await player1Page.fill("#player-name", "Alice");
      await player1Page.click("#join-game-btn");
      await player1Page.waitForURL(/\/player\/player_/);

      await player2Page.goto("http://localhost:5001/join");
      await player2Page.fill("#room-code", roomCode!);
      await player2Page.fill("#player-name", "Bob");
      await player2Page.click("#join-game-btn");
      await player2Page.waitForURL(/\/player\/player_/);

      await player3Page.goto("http://localhost:5001/join");
      await player3Page.fill("#room-code", roomCode!);
      await player3Page.fill("#player-name", "Charlie");
      await player3Page.click("#join-game-btn");
      await player3Page.waitForURL(/\/player\/player_/);

      console.log("✅ 3 players joined");

      await expect(hostPage.locator("#players-ul li")).toHaveCount(3, {
        timeout: 10_000,
      });

      // Start game
      await hostPage.click("#start-game-btn");
      await hostPage.waitForURL(/\/host\/play/);

      await Promise.all([
        hostPage.waitForFunction(
          () =>
            document
              .querySelector<HTMLElement>("#question-text")
              ?.textContent?.trim()?.length! > 0,
          { timeout: 15_000 }
        ),
        player1Page.waitForFunction(
          () =>
            document
              .querySelector<HTMLElement>("#question-text")
              ?.textContent?.trim()?.length! > 0,
          { timeout: 15_000 }
        ),
        player2Page.waitForFunction(
          () =>
            document
              .querySelector<HTMLElement>("#question-text")
              ?.textContent?.trim()?.length! > 0,
          { timeout: 15_000 }
        ),
        player3Page.waitForFunction(
          () =>
            document
              .querySelector<HTMLElement>("#question-text")
              ?.textContent?.trim()?.length! > 0,
          { timeout: 15_000 }
        ),
      ]);

      const question1Text = await hostPage
        .locator("#question-text")
        .textContent();
      console.log("✅ Question 1 loaded on all 4 clients");

      // Only 2 players answer
      console.log("\n📍 Only 2 out of 3 players answer...");
      await player1Page.locator(".answer-btn").first().click();
      await player2Page.locator(".answer-btn").first().click();
      console.log("✅ 2/3 players answered");

      // Wait and verify NO auto-advance
      await hostPage.waitForTimeout(8000);
      const stillQuestion1 = await hostPage
        .locator("#question-text")
        .textContent();
      expect(stillQuestion1).toBe(question1Text);
      console.log("✅ PASS: Did NOT advance with 2/3 players");

      // 3rd player answers
      console.log("\n📍 3rd player answers...");
      await player3Page.locator(".answer-btn").first().click();
      console.log("✅ 3/3 players answered");

      // Should auto-advance now
      await hostPage.waitForFunction(
        (previousText) => {
          const currentText = document
            .querySelector<HTMLElement>("#question-text")
            ?.textContent?.trim();
          return (
            currentText &&
            currentText !== previousText &&
            currentText.length > 0
          );
        },
        question1Text?.trim(),
        { timeout: 15_000 }
      );

      const question2Text = await hostPage
        .locator("#question-text")
        .textContent();
      expect(question2Text).not.toBe(question1Text);
      console.log("✅ PASS: Auto-advanced after all 3 players answered");

      console.log("\n🎉 SUCCESS: 3-player scenario validated!");
    } finally {
      await hostContext.close();
      await player1Context.close();
      await player2Context.close();
      await player3Context.close();
    }
  });
});
