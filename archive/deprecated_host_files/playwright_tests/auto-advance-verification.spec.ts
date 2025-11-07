import { test, expect } from '@playwright/test';

/**
 * Comprehensive Auto-Advance Verification Test
 *
 * This test verifies that the auto-advance mechanism:
 * 1. Only triggers when ALL alive players have answered
 * 2. Takes exactly 5 seconds after the last player answers
 * 3. Handles race conditions (simultaneous answers)
 * 4. Works across multiple consecutive questions
 * 5. Works with staggered answer timing
 */

test.describe('Auto-Advance Verification', () => {
  test.setTimeout(180_000); // 3 minutes for all 8 tests

  test('comprehensive auto-advance behavior', async ({ browser }) => {
    const BASE_URL = 'http://localhost:5001';

    // Helper to create a game with N players
    async function createGame(playerCount: number) {
      const hostContext = await browser.newContext({ viewport: { width: 1440, height: 900 } });
      const hostPage = await hostContext.newPage();

      // Create game
      await hostPage.goto(`${BASE_URL}/host`);
      await hostPage.fill('#host-name', 'TestHost');
      await hostPage.click('#create-game-btn');
      await hostPage.waitForURL(/\/host\/lobby\?room=/);

      const roomCode = (await hostPage.locator('#room-code').textContent())?.trim() || '';
      expect(roomCode).toMatch(/^[A-Z0-9]{6}$/);

      // Add players
      const players = [];
      for (let i = 0; i < playerCount; i++) {
        const playerContext = await browser.newContext({ viewport: { width: 428, height: 926 } });
        const playerPage = await playerContext.newPage();

        await playerPage.goto(`${BASE_URL}/join`);
        await playerPage.fill('#room-code', roomCode);
        await playerPage.fill('#player-name', `Player${i + 1}`);
        await playerPage.click('#join-game-btn');
        await playerPage.waitForURL(/\/player\/player_/);
        await playerPage.waitForSelector('#waiting-screen');

        players.push({ context: playerContext, page: playerPage });
      }

      // Wait for all players to show in lobby
      await expect(hostPage.locator('#players-ul li')).toHaveCount(playerCount, { timeout: 10_000 });

      // Start game
      await hostPage.click('#start-game-btn');
      await hostPage.waitForURL(/\/host\/play/);

      // Wait for first question to load
      await hostPage.waitForFunction(
        () => {
          const el = document.querySelector<HTMLElement>('#question-text');
          return el && el.textContent && el.textContent.trim().length > 0;
        },
        { timeout: 15_000 }
      );

      // Wait for all players to receive first question
      await Promise.all(
        players.map(p => p.page.waitForFunction(
          () => {
            const el = document.querySelector<HTMLElement>('#question-text');
            return el && el.textContent && el.textContent.trim().length > 0;
          },
          { timeout: 15_000 }
        ))
      );

      return { hostContext, hostPage, players, roomCode };
    }

    // Helper to get current question text
    async function getQuestionText(page: any): Promise<string> {
      return (await page.locator('#question-text').textContent())?.trim() || '';
    }

    // Helper to answer for a player
    async function answerQuestion(playerPage: any) {
      const buttons = playerPage.locator('.answer-btn');
      await buttons.first().waitFor({ state: 'visible', timeout: 10_000 });
      await buttons.first().click();
    }

    // ===== TEST 1: 1/4 players - Does NOT advance =====
    console.log('\n🧪 TEST 1: 1/4 players answered - should NOT auto-advance');
    const test1Start = Date.now();
    const game1 = await createGame(4);
    const question1Initial = await getQuestionText(game1.hostPage);

    // Only player 1 answers
    await answerQuestion(game1.players[0].page);

    // Wait 13 seconds - should NOT advance
    await new Promise(resolve => setTimeout(resolve, 13000));
    const question1After = await getQuestionText(game1.hostPage);
    expect(question1After).toBe(question1Initial);
    console.log(`✅ TEST 1 PASSED: Question did not advance (${(Date.now() - test1Start) / 1000}s)`);

    // Cleanup
    await game1.hostContext.close();
    for (const p of game1.players) await p.context.close();


    // ===== TEST 2: 2/4 players - Does NOT advance =====
    console.log('\n🧪 TEST 2: 2/4 players answered - should NOT auto-advance');
    const test2Start = Date.now();
    const game2 = await createGame(4);
    const question2Initial = await getQuestionText(game2.hostPage);

    // Players 1 and 2 answer
    await answerQuestion(game2.players[0].page);
    await answerQuestion(game2.players[1].page);

    // Wait 13 seconds - should NOT advance
    await new Promise(resolve => setTimeout(resolve, 13000));
    const question2After = await getQuestionText(game2.hostPage);
    expect(question2After).toBe(question2Initial);
    console.log(`✅ TEST 2 PASSED: Question did not advance (${(Date.now() - test2Start) / 1000}s)`);

    // Cleanup
    await game2.hostContext.close();
    for (const p of game2.players) await p.context.close();


    // ===== TEST 3: 3/4 players - Does NOT advance =====
    console.log('\n🧪 TEST 3: 3/4 players answered - should NOT auto-advance');
    const test3Start = Date.now();
    const game3 = await createGame(4);
    const question3Initial = await getQuestionText(game3.hostPage);

    // Players 1, 2, and 3 answer
    await answerQuestion(game3.players[0].page);
    await answerQuestion(game3.players[1].page);
    await answerQuestion(game3.players[2].page);

    // Wait 13 seconds - should NOT advance
    await new Promise(resolve => setTimeout(resolve, 13000));
    const question3After = await getQuestionText(game3.hostPage);
    expect(question3After).toBe(question3Initial);
    console.log(`✅ TEST 3 PASSED: Question did not advance (${(Date.now() - test3Start) / 1000}s)`);

    // Cleanup
    await game3.hostContext.close();
    for (const p of game3.players) await p.context.close();


    // ===== TEST 4: 4/4 players - DOES advance =====
    console.log('\n🧪 TEST 4: 4/4 players answered - SHOULD auto-advance');
    const test4Start = Date.now();
    const game4 = await createGame(4);
    const question4Initial = await getQuestionText(game4.hostPage);

    // All 4 players answer
    for (const player of game4.players) {
      await answerQuestion(player.page);
    }

    // Wait for "all players answered" notification
    await game4.hostPage.waitForFunction(
      () => {
        const gameplay = (window as any).hostGamePlay;
        return gameplay && gameplay.allAnswered === true;
      },
      { timeout: 10_000 }
    );

    // Wait for auto-advance (should happen ~5 seconds after last answer)
    await game4.hostPage.waitForFunction(
      (previousText) => {
        const el = document.querySelector<HTMLElement>('#question-text');
        const currentText = el?.textContent?.trim();
        return currentText && currentText !== previousText && currentText.length > 0;
      },
      question4Initial,
      { timeout: 10_000 }
    );

    const question4After = await getQuestionText(game4.hostPage);
    expect(question4After).not.toBe(question4Initial);
    console.log(`✅ TEST 4 PASSED: Question advanced automatically (${(Date.now() - test4Start) / 1000}s)`);

    // Cleanup
    await game4.hostContext.close();
    for (const p of game4.players) await p.context.close();


    // ===== TEST 5: Race condition - simultaneous answers =====
    console.log('\n🧪 TEST 5: All players answer simultaneously');
    const test5Start = Date.now();
    const game5 = await createGame(4);
    const question5Initial = await getQuestionText(game5.hostPage);

    // All players answer at the same time
    await Promise.all(game5.players.map(p => answerQuestion(p.page)));

    // Should still advance properly
    await game5.hostPage.waitForFunction(
      (previousText) => {
        const el = document.querySelector<HTMLElement>('#question-text');
        const currentText = el?.textContent?.trim();
        return currentText && currentText !== previousText && currentText.length > 0;
      },
      question5Initial,
      { timeout: 10_000 }
    );

    const question5After = await getQuestionText(game5.hostPage);
    expect(question5After).not.toBe(question5Initial);
    console.log(`✅ TEST 5 PASSED: Handled simultaneous answers (${(Date.now() - test5Start) / 1000}s)`);

    // Cleanup
    await game5.hostContext.close();
    for (const p of game5.players) await p.context.close();


    // ===== TEST 6: Timing verification - exactly 5 seconds =====
    console.log('\n🧪 TEST 6: Verify 5-second countdown timing');
    const test6Start = Date.now();
    const game6 = await createGame(2); // Use fewer players for faster test
    const question6Initial = await getQuestionText(game6.hostPage);

    // Record when last player answers
    await answerQuestion(game6.players[0].page);
    const lastAnswerTime = Date.now();
    await answerQuestion(game6.players[1].page);

    // Wait for auto-advance
    await game6.hostPage.waitForFunction(
      (previousText) => {
        const el = document.querySelector<HTMLElement>('#question-text');
        const currentText = el?.textContent?.trim();
        return currentText && currentText !== previousText && currentText.length > 0;
      },
      question6Initial,
      { timeout: 10_000 }
    );

    const advanceTime = Date.now();
    const timingDifference = (advanceTime - lastAnswerTime) / 1000;

    // Should be approximately 5 seconds (allow 4.5-6.0 range for network latency)
    expect(timingDifference).toBeGreaterThan(4.5);
    expect(timingDifference).toBeLessThan(6.0);
    console.log(`✅ TEST 6 PASSED: Auto-advance took ${timingDifference.toFixed(2)}s (${(Date.now() - test6Start) / 1000}s total)`);

    // Cleanup
    await game6.hostContext.close();
    for (const p of game6.players) await p.context.close();


    // ===== TEST 7: Multiple consecutive auto-advances =====
    console.log('\n🧪 TEST 7: Multiple consecutive auto-advances');
    const test7Start = Date.now();
    const game7 = await createGame(2);

    // Go through 3 questions
    for (let i = 0; i < 3; i++) {
      const questionBefore = await getQuestionText(game7.hostPage);

      // All players answer
      for (const player of game7.players) {
        await answerQuestion(player.page);
      }

      // Wait for auto-advance
      await game7.hostPage.waitForFunction(
        (previousText) => {
          const el = document.querySelector<HTMLElement>('#question-text');
          const currentText = el?.textContent?.trim();
          return currentText && currentText !== previousText && currentText.length > 0;
        },
        questionBefore,
        { timeout: 10_000 }
      );

      const questionAfter = await getQuestionText(game7.hostPage);
      expect(questionAfter).not.toBe(questionBefore);
      console.log(`  ✓ Question ${i + 1} → ${i + 2} advanced`);
    }

    console.log(`✅ TEST 7 PASSED: 3 consecutive auto-advances worked (${(Date.now() - test7Start) / 1000}s)`);

    // Cleanup
    await game7.hostContext.close();
    for (const p of game7.players) await p.context.close();


    // ===== TEST 8: Staggered answers with delays =====
    console.log('\n🧪 TEST 8: Staggered answers with delays');
    const test8Start = Date.now();
    const game8 = await createGame(3);
    const question8Initial = await getQuestionText(game8.hostPage);

    // Player 1 answers
    await answerQuestion(game8.players[0].page);
    await new Promise(resolve => setTimeout(resolve, 2000)); // 2 second delay

    // Player 2 answers
    await answerQuestion(game8.players[1].page);
    await new Promise(resolve => setTimeout(resolve, 2000)); // 2 second delay

    // Player 3 answers - this should trigger the 5-second countdown
    const lastAnswerTime8 = Date.now();
    await answerQuestion(game8.players[2].page);

    // Wait for auto-advance
    await game8.hostPage.waitForFunction(
      (previousText) => {
        const el = document.querySelector<HTMLElement>('#question-text');
        const currentText = el?.textContent?.trim();
        return currentText && currentText !== previousText && currentText.length > 0;
      },
      question8Initial,
      { timeout: 10_000 }
    );

    const advanceTime8 = Date.now();
    const timingFromLast = (advanceTime8 - lastAnswerTime8) / 1000;

    // Should still be ~5 seconds from the LAST answer, not the first
    expect(timingFromLast).toBeGreaterThan(4.5);
    expect(timingFromLast).toBeLessThan(6.0);
    console.log(`✅ TEST 8 PASSED: Staggered answers, advanced ${timingFromLast.toFixed(2)}s after last answer (${(Date.now() - test8Start) / 1000}s total)`);

    // Cleanup
    await game8.hostContext.close();
    for (const p of game8.players) await p.context.close();


    console.log('\n🎉 ALL 8 TESTS PASSED!');
  });
});
