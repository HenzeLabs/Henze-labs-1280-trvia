import { test, expect } from '@playwright/test';

test.describe('Simple Auto-Advance Test', () => {
  test.setTimeout(120_000); // 2 minutes should be plenty

  test('verifies auto-advance works after all players answer', async ({ browser }) => {
    // Create 3 browser contexts: 1 host + 2 players
    const hostContext = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const player1Context = await browser.newContext({ viewport: { width: 428, height: 926 } });
    const player2Context = await browser.newContext({ viewport: { width: 428, height: 926 } });

    const hostPage = await hostContext.newPage();
    const player1Page = await player1Context.newPage();
    const player2Page = await player2Context.newPage();

    // Enable console logging
    hostPage.on('console', msg => console.log(`HOST: ${msg.text()}`));
    player1Page.on('console', msg => console.log(`PLAYER1: ${msg.text()}`));
    player2Page.on('console', msg => console.log(`PLAYER2: ${msg.text()}`));

    try {
      // Step 1: Host creates game
      console.log('Step 1: Host creating game...');
      await hostPage.goto('http://localhost:5001/host');
      await hostPage.fill('#host-name', 'TestHost');
      await hostPage.click('#create-game-btn');
      await hostPage.waitForURL(/\/host\/lobby\?room=/);

      const roomCode = (await hostPage.locator('#room-code').textContent())?.trim();
      console.log(`Room code: ${roomCode}`);
      expect(roomCode).toMatch(/^[A-Z0-9]{6}$/);

      // Step 2: Player 1 joins
      console.log('Step 2: Player 1 joining...');
      await player1Page.goto('http://localhost:5001/join');
      await player1Page.fill('#room-code', roomCode!);
      await player1Page.fill('#player-name', 'Alice');
      await player1Page.click('#join-game-btn');
      await player1Page.waitForURL(/\/player\/player_/);
      await player1Page.waitForSelector('#waiting-screen');

      // Step 3: Player 2 joins
      console.log('Step 3: Player 2 joining...');
      await player2Page.goto('http://localhost:5001/join');
      await player2Page.fill('#room-code', roomCode!);
      await player2Page.fill('#player-name', 'Bob');
      await player2Page.click('#join-game-btn');
      await player2Page.waitForURL(/\/player\/player_/);
      await player2Page.waitForSelector('#waiting-screen');

      // Wait for lobby to show 2 players
      await expect(hostPage.locator('#players-ul li')).toHaveCount(2, { timeout: 10_000 });

      // Step 4: Start game
      console.log('Step 4: Starting game...');
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

      // Wait for players to receive first question
      await Promise.all([
        player1Page.waitForFunction(
          () => {
            const el = document.querySelector<HTMLElement>('#question-text');
            return el && el.textContent && el.textContent.trim().length > 0;
          },
          { timeout: 15_000 }
        ),
        player2Page.waitForFunction(
          () => {
            const el = document.querySelector<HTMLElement>('#question-text');
            return el && el.textContent && el.textContent.trim().length > 0;
          },
          { timeout: 15_000 }
        )
      ]);

      console.log('✅ Question 1 loaded on all clients');

      // Get the question text for tracking
      const question1Text = await hostPage.locator('#question-text').textContent();
      console.log(`Question 1: ${question1Text?.substring(0, 50)}...`);

      // Step 5: Both players answer
      console.log('Step 5: Players answering question 1...');

      // Player 1 answers
      const player1Buttons = player1Page.locator('.answer-btn');
      await player1Buttons.first().waitFor({ state: 'visible', timeout: 10_000 });
      await player1Buttons.first().click();
      console.log('Player 1 answered');

      // Player 2 answers
      const player2Buttons = player2Page.locator('.answer-btn');
      await player2Buttons.first().waitFor({ state: 'visible', timeout: 10_000 });
      await player2Buttons.first().click();
      console.log('Player 2 answered');

      // Step 6: Wait for "all players answered" message
      console.log('Step 6: Waiting for all players answered notification...');
      await hostPage.waitForFunction(
        () => {
          const gameplay = (window as any).hostGamePlay;
          return gameplay && gameplay.allAnswered === true;
        },
        { timeout: 10_000 }
      );
      console.log('✅ All players answered flag detected');

      // Step 7: Wait for auto-advance (5 seconds + buffer)
      console.log('Step 7: Waiting for auto-advance (5 second countdown)...');

      // Wait for the question text to change (indicates new question loaded)
      await hostPage.waitForFunction(
        (previousText) => {
          const el = document.querySelector<HTMLElement>('#question-text');
          const currentText = el?.textContent?.trim();
          return currentText && currentText !== previousText && currentText.length > 0;
        },
        question1Text?.trim(),
        { timeout: 15_000 } // 5 seconds for countdown + 10 seconds buffer
      );

      const question2Text = await hostPage.locator('#question-text').textContent();
      console.log(`✅ Auto-advance succeeded! Question 2: ${question2Text?.substring(0, 50)}...`);

      // Verify new question is different
      expect(question2Text).not.toBe(question1Text);

      console.log('\n🎉 SUCCESS: Auto-advance mechanism is working!');

    } finally {
      // Cleanup
      await hostContext.close();
      await player1Context.close();
      await player2Context.close();
    }
  });
});
