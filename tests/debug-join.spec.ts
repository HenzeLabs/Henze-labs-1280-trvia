/**
 * Debug test to diagnose player join issues
 */

import { test, expect } from "@playwright/test";
import { createGame, joinGame } from "./support/test-utils";

test.describe("Debug Join Flow", () => {
  test.setTimeout(120000);

  test("diagnose player join issue", async ({ browser }) => {
    // Create TV context
    const tvContext = await browser.newContext({
      viewport: { width: 1280, height: 720 },
    });
    const tvPage = await tvContext.newPage();

    // Enable console logging
    tvPage.on("console", (msg) => console.log(`[TV Console] ${msg.text()}`));
    tvPage.on("pageerror", (err) => console.error(`[TV Error] ${err.message}`));

    // Create player context
    const playerContext = await browser.newContext({
      viewport: { width: 428, height: 926 },
    });
    const playerPage = await playerContext.newPage();

    // Enable console logging
    playerPage.on("console", (msg) =>
      console.log(`[Player Console] ${msg.text()}`)
    );
    playerPage.on("pageerror", (err) =>
      console.error(`[Player Error] ${err.message}`)
    );

    try {
      console.log("🎮 Creating game...");
      const roomCode = await createGame(tvPage);
      console.log(`✅ Game created with code: ${roomCode}`);

      // Take screenshot of TV
      await tvPage.screenshot({ path: "test-results/tv-after-create.png" });

      console.log("👤 Joining as player...");
      await joinGame(playerPage, roomCode, "DebugPlayer");
      console.log("✅ Player joined successfully!");

      // Take screenshots
      await tvPage.screenshot({ path: "test-results/tv-after-join.png" });
      await playerPage.screenshot({
        path: "test-results/player-after-join.png",
      });

      // Check if start button is enabled
      const startBtn = tvPage.getByTestId("start-game-btn");
      const isEnabled = await startBtn.isEnabled();
      console.log(`Start button enabled: ${isEnabled}`);

      expect(isEnabled).toBe(true);
    } finally {
      await tvContext.close();
      await playerContext.close();
    }
  });
});
