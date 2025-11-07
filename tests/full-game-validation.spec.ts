/**
 * 🎮 Full Game Validation - Complete End-to-End Test
 *
 * Simulates a real party game with:
 * - 1 TV display
 * - 4 players on separate phones
 * - Complete game from start to finish
 * - Validation of all UI states and game logic
 * - Detailed reporting of any issues
 *
 * Run with: npx playwright test full-game-validation.spec.ts --headed
 */

import { test, expect, Page, BrowserContext } from "@playwright/test";
import {
  createGame,
  joinGame,
  startGame,
  answerQuestion,
  waitForNextQuestion,
  getCurrentQuestion,
} from "./support/test-utils";

test.describe("🎮 Full Game Validation", () => {
  test.setTimeout(600000); // 10 minutes for complete game

  test("Complete 4-player game with TV validation", async ({ browser }) => {
    const issues: string[] = [];
    const warnings: string[] = [];

    console.log("\n" + "=".repeat(60));
    console.log("🎮 STARTING FULL GAME VALIDATION");
    console.log("=".repeat(60));

    // Create contexts for TV and 4 players
    const tvContext = await browser.newContext({
      viewport: { width: 1280, height: 720 }, // TV resolution
    });
    const player1Context = await browser.newContext({
      viewport: { width: 375, height: 812 }, // iPhone size
    });
    const player2Context = await browser.newContext({
      viewport: { width: 414, height: 896 }, // iPhone Pro size
    });
    const player3Context = await browser.newContext({
      viewport: { width: 360, height: 740 }, // Android size
    });
    const player4Context = await browser.newContext({
      viewport: { width: 393, height: 852 }, // iPhone 14 size
    });

    const tvPage = await tvContext.newPage();
    const player1Page = await player1Context.newPage();
    const player2Page = await player2Context.newPage();
    const player3Page = await player3Context.newPage();
    const player4Page = await player4Context.newPage();

    try {
      // ========================================
      // PHASE 1: Game Creation & Lobby
      // ========================================
      console.log("\n📺 PHASE 1: Creating Game on TV...");
      const roomCode = await createGame(tvPage);
      console.log(`✅ Game created with room code: ${roomCode}`);

      // Validate TV lobby screen
      console.log("\n🔍 Validating TV Lobby...");
      const tvTitle = await tvPage.getByTestId("tv-waiting").isVisible();
      if (!tvTitle) {
        issues.push("TV lobby screen not visible after game creation");
      }

      const tvRoomCodeDisplay = await tvPage.locator('.tv-room-code-badge-code').textContent();
      if (tvRoomCodeDisplay !== roomCode) {
        issues.push(`TV room code mismatch: expected ${roomCode}, got ${tvRoomCodeDisplay}`);
      }
      console.log(`✅ TV showing correct room code: ${roomCode}`);

      // Check QR code exists
      const qrCode = await tvPage.locator('#tv-qr-code').isVisible();
      if (!qrCode) {
        warnings.push("QR code not visible on TV lobby");
      } else {
        console.log("✅ QR code displayed on TV");
      }

      // Check player count shows 0
      const initialPlayerCount = await tvPage.locator('#tv-player-count').textContent();
      if (initialPlayerCount !== '0') {
        issues.push(`TV should show 0 players initially, shows: ${initialPlayerCount}`);
      }
      console.log("✅ TV shows 0 players initially");

      // ========================================
      // PHASE 2: Players Joining
      // ========================================
      console.log("\n👥 PHASE 2: Players Joining Game...");

      const players = [
        { page: player1Page, name: "Alice", context: player1Context },
        { page: player2Page, name: "Bob", context: player2Context },
        { page: player3Page, name: "Charlie", context: player3Context },
        { page: player4Page, name: "Diana", context: player4Context },
      ];

      for (let i = 0; i < players.length; i++) {
        const player = players[i];
        console.log(`\n  👤 ${player.name} joining...`);

        await joinGame(player.page, roomCode, player.name);

        // Validate player waiting screen
        const waitingScreen = await player.page.getByTestId("waiting-screen").isVisible();
        if (!waitingScreen) {
          issues.push(`${player.name}: Waiting screen not visible after joining`);
        }

        // Check room code visible on player screen
        const playerRoomCode = await player.page.getByTestId("room-code-display").textContent();
        if (playerRoomCode !== roomCode) {
          issues.push(`${player.name}: Room code mismatch - expected ${roomCode}, got ${playerRoomCode}`);
        }

        // Wait a moment for WebSocket update
        await tvPage.waitForTimeout(500);

        // Validate TV player count updated
        const currentPlayerCount = await tvPage.locator('#tv-player-count').textContent();
        const expectedCount = (i + 1).toString();
        if (currentPlayerCount !== expectedCount) {
          issues.push(`TV should show ${expectedCount} players after ${player.name} joined, shows: ${currentPlayerCount}`);
        } else {
          console.log(`  ✅ TV now shows ${expectedCount} player(s)`);
        }
      }

      console.log("\n✅ All 4 players joined successfully");

      // Validate start button enabled
      const startBtn = tvPage.getByTestId("start-game-btn");
      const isStartEnabled = await startBtn.isEnabled();
      if (!isStartEnabled) {
        issues.push("Start Game button should be enabled with 4 players");
      } else {
        console.log("✅ Start Game button is enabled");
      }

      // ========================================
      // PHASE 3: Starting Game
      // ========================================
      console.log("\n🎯 PHASE 3: Starting Game...");
      await startGame(tvPage);

      // Validate TV shows question
      await expect(tvPage.getByTestId("question-text")).toBeVisible({ timeout: 5000 });
      const tvQuestion1 = await tvPage.getByTestId("question-text").textContent();
      console.log(`✅ TV showing question: "${tvQuestion1?.substring(0, 60)}..."`);

      // Validate all players see question screen
      for (const player of players) {
        const questionVisible = await player.page.getByTestId("question-text").isVisible();
        if (!questionVisible) {
          issues.push(`${player.name}: Question screen not visible after game start`);
        }

        const playerQuestion = await player.page.getByTestId("question-text").textContent();
        if (playerQuestion !== tvQuestion1) {
          issues.push(`${player.name}: Question mismatch with TV`);
        }
      }
      console.log("✅ All players see the same question as TV");

      // ========================================
      // PHASE 4: Playing Through All 10 Questions
      // ========================================
      console.log("\n🎲 PHASE 4: Playing Through 10 Questions...");

      for (let questionNum = 1; questionNum <= 10; questionNum++) {
        console.log(`\n  ❓ Question ${questionNum}/10`);

        const currentTvQuestion = await tvPage.getByTestId("question-text").textContent();
        console.log(`     TV Question: "${currentTvQuestion?.substring(0, 50)}..."`);

        // All players answer in parallel (as fast as possible to avoid timer expiration)
        // In a real game, players click at different times, but we need to be fast in tests
        const answerPromises = players.map(async (player, i) => {
          try {
            // Validate player sees question
            const playerQuestion = await player.page.getByTestId("question-text").textContent();
            if (playerQuestion !== currentTvQuestion) {
              issues.push(`Q${questionNum}: ${player.name} question mismatch with TV`);
            }

            // Answer the question (random answer for variety)
            const answerIndex = i % 4; // Vary answers across players

            await answerQuestion(player.page, answerIndex);
            console.log(`     ✓ ${player.name} answered (choice ${answerIndex})`);

            return { player: player.name, success: true };
          } catch (error) {
            console.log(`     ❌ ${player.name} failed to answer: ${error}`);

            // DEBUG: Take screenshot and capture state
            await player.page.screenshot({ path: `test-results/debug-${player.name}-answer-failed.png` });

            const screenState = await player.page.getByTestId("question-screen").getAttribute("class");
            const containerState = await player.page.locator('#mobile-answers').getAttribute("class");
            const feedbackVisible = await player.page.getByTestId("answer-feedback").isVisible();
            const waitingVisible = await player.page.getByTestId("waiting-next").isVisible();
            console.log(`        question-screen classes: ${screenState}`);
            console.log(`        mobile-answers classes: ${containerState}`);
            console.log(`        answer-feedback visible: ${feedbackVisible}`);
            console.log(`        waiting-next visible: ${waitingVisible}`);

            issues.push(`Q${questionNum}: ${player.name} failed to answer - ${error}`);

            return { player: player.name, success: false, error: String(error) };
          }
        });

        // Wait for all players to finish answering
        const results = await Promise.all(answerPromises);

        // Check if any failed
        const failed = results.filter(r => !r.success);
        if (failed.length > 0) {
          console.log(`     ⚠️ ${failed.length} player(s) failed to answer`);
          break; // Stop if any player fails
        }

        console.log(`     ✅ All 4 players answered question ${questionNum}`);

        // If not last question, wait for next question
        if (questionNum < 10) {
          console.log(`     ⏳ Waiting for auto-advance to Q${questionNum + 1}...`);

          try {
            // Wait for TV to advance
            await waitForNextQuestion(tvPage, currentTvQuestion, 25000);

            // Validate all players also advanced
            for (const player of players) {
              const newQuestion = await player.page.getByTestId("question-text").textContent();
              if (newQuestion === currentTvQuestion) {
                warnings.push(`Q${questionNum}: ${player.name} didn't advance to next question`);
              }
            }

            console.log(`     ✅ Auto-advanced to question ${questionNum + 1}`);
          } catch (error) {
            issues.push(`Q${questionNum}: Failed to auto-advance to next question - ${error}`);
            break; // Stop if auto-advance fails
          }
        }
      }

      console.log("\n✅ Completed all 10 questions");

      // ========================================
      // PHASE 5: Final Results & Leaderboard
      // ========================================
      console.log("\n🏆 PHASE 5: Validating Final Results...");

      // Validate TV shows final leaderboard
      try {
        await expect(tvPage.locator('.tv-leaderboard')).toBeVisible({ timeout: 30000 });
        console.log("✅ TV showing final leaderboard");

        // Check leaderboard has 4 players
        const leaderboardItems = await tvPage.locator('.tv-leaderboard-item').count();
        if (leaderboardItems !== 4) {
          issues.push(`TV leaderboard should show 4 players, shows ${leaderboardItems}`);
        } else {
          console.log("✅ TV leaderboard shows all 4 players");
        }

        // Check winner highlighted
        const winner = await tvPage.locator('.tv-leaderboard-item.rank-1').isVisible();
        if (!winner) {
          warnings.push("Winner (rank-1) not visually highlighted on TV");
        } else {
          const winnerName = await tvPage.locator('.tv-leaderboard-item.rank-1 .tv-leaderboard-name').textContent();
          console.log(`✅ Winner highlighted: ${winnerName}`);
        }
      } catch (error) {
        issues.push(`TV final leaderboard not visible: ${error}`);
      }

      // Validate all players see final results
      for (const player of players) {
        try {
          await expect(player.page.getByTestId("final-results")).toBeVisible({ timeout: 30000 });

          const finalRank = await player.page.locator('#final-rank').textContent();
          const finalScore = await player.page.locator('#final-score').textContent();

          console.log(`  ✅ ${player.name}: Rank ${finalRank}, Score: ${finalScore}`);
        } catch (error) {
          issues.push(`${player.name}: Final results screen not visible`);
        }
      }

      // ========================================
      // FINAL REPORT
      // ========================================
      console.log("\n" + "=".repeat(60));
      console.log("📊 VALIDATION REPORT");
      console.log("=".repeat(60));

      if (issues.length === 0 && warnings.length === 0) {
        console.log("\n✅ ✅ ✅ ALL CHECKS PASSED! ✅ ✅ ✅");
        console.log("\n🎉 Your game is PERFECT and ready to play with friends!");
      } else {
        if (issues.length > 0) {
          console.log("\n❌ ISSUES FOUND:");
          issues.forEach((issue, i) => {
            console.log(`  ${i + 1}. ${issue}`);
          });
        }

        if (warnings.length > 0) {
          console.log("\n⚠️  WARNINGS (non-critical):");
          warnings.forEach((warning, i) => {
            console.log(`  ${i + 1}. ${warning}`);
          });
        }

        if (issues.length === 0) {
          console.log("\n✅ No critical issues! Warnings are minor and don't affect gameplay.");
        }
      }

      console.log("\n" + "=".repeat(60));

      // Fail test if there are critical issues
      if (issues.length > 0) {
        throw new Error(`Found ${issues.length} critical issue(s) - see report above`);
      }

    } finally {
      // Cleanup
      await tvPage.close();
      await player1Page.close();
      await player2Page.close();
      await player3Page.close();
      await player4Page.close();
      await tvContext.close();
      await player1Context.close();
      await player2Context.close();
      await player3Context.close();
      await player4Context.close();
    }
  });
});
