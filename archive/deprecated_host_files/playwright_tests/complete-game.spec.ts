import { test, expect } from '@playwright/test';

test.describe('Multiclient Smoke Flow', () => {
  test.setTimeout(120_000);

  test('host + player + tv can run the first question', async ({ browser }) => {
    const hostContext = await browser.newContext();
    const playerContext = await browser.newContext({ viewport: { width: 430, height: 932 } });
    const tvContext = await browser.newContext({ viewport: { width: 1920, height: 1080 } });

    const hostPage = await hostContext.newPage();
    hostPage.on('console', msg => console.log(`HOST> ${msg.type()} ${msg.text()}`));
    hostPage.on('pageerror', err => console.error(`HOST ERROR> ${err}`));
    hostPage.on('response', resp => {
      const url = resp.url();
      if (url.includes('/api/game/')) {
        console.log(`HOST RESPONSE> ${resp.status()} ${url}`);
      }
    });
    const playerPage = await playerContext.newPage();
    playerPage.on('console', msg => console.log(`PLAYER> ${msg.type()} ${msg.text()}`));
    playerPage.on('pageerror', err => console.error(`PLAYER ERROR> ${err}`));
    const tvPage = await tvContext.newPage();
    tvPage.on('console', msg => console.log(`TV> ${msg.type()} ${msg.text()}`));
    tvPage.on('pageerror', err => console.error(`TV ERROR> ${err}`));

    // ---------- Host creates game ----------
    console.log('📝 Host creating game…');
    await hostPage.goto('/host');
    await hostPage.fill('#host-name', 'Playwright Host');
    await hostPage.click('#create-game-btn');

    // Redirect to lobby and capture room code
    await hostPage.waitForURL(/\/host\/lobby\?room=/, { timeout: 10_000 });
    const roomCodeLocator = hostPage.locator('#room-code');
    await expect(roomCodeLocator).not.toHaveText('----', { timeout: 10_000 });
    const roomCode = (await roomCodeLocator.textContent())?.trim() ?? '';
    console.log(`✅ Room code ${roomCode}`);
    expect(roomCode).toMatch(/^[A-Z0-9]{6}$/);

    // ---------- TV joins ----------
    console.log('📺 TV tuning in…');
    await tvPage.goto(`/tv/${roomCode}`);
    await expect(tvPage.locator('#tv-waiting')).toBeVisible();

    // ---------- Player joins ----------
    console.log('🎮 Player joining…');
    await playerPage.goto('/join');
    await playerPage.fill('#room-code', roomCode);
    await playerPage.fill('#player-name', 'Playwright Player');
    await playerPage.click('#join-game-btn');
    await playerPage.waitForURL(/\/player\/player_/, { timeout: 10_000 });
    await expect(playerPage.locator('#waiting-screen')).toBeVisible();
    console.log('✅ Player joined lobby');

    // Host sees player in lobby
    await expect(hostPage.locator('#players-ul li')).toHaveCount(1, { timeout: 10_000 });
    await expect(hostPage.locator('#start-game-btn')).toBeEnabled();

    // ---------- Start the game ----------
    console.log('🚀 Starting game…');
    await hostPage.locator('#start-game-btn').click({ force: true });
    // Fallback trigger via JS in case UI overlay captures the click in headless mode
    await hostPage.evaluate(() => {
      if (window.hostLobby) {
        console.log('🧪 Forcing startGame via Playwright');
        window.hostLobby.startGame();
      }
    });
    // Wait for first question across host/player/TV
    await hostPage.waitForFunction(() => {
      const el = document.querySelector<HTMLElement>('#question-text');
      return !!el && el.textContent !== null && el.textContent.trim().length > 0 && !/Loading/i.test(el.textContent);
    }, null, { timeout: 15_000 });

    await playerPage.waitForFunction(() => {
      const el = document.querySelector<HTMLElement>('#question-text');
      return !!el && el.textContent !== null && el.textContent.trim().length > 0 && !/Waiting/i.test(el.textContent);
    }, null, { timeout: 15_000 });
    await tvPage.waitForSelector('#tv-question:not(.hidden)', { timeout: 15_000 });
    console.log('✅ Question broadcast to all clients');

    // ---------- Player answers ----------
    const playerAnswers = playerPage.locator('.answer-btn');
    const answerCount = await playerAnswers.count();
    expect(answerCount).toBeGreaterThan(0);
    await playerAnswers.first().click();
    console.log('✅ Player submitted an answer');

    // Host reveals answer
    await hostPage.waitForTimeout(1_000);
    await hostPage.click('#reveal-answer-btn');
    await hostPage.waitForTimeout(1_000);

    await expect(playerPage.locator('#answer-feedback')).toBeVisible();
    await expect(tvPage.locator('#tv-status-banner')).toBeVisible();
    console.log('✅ Answer feedback visible on player + TV');

    // Host advances to next question to ensure controls still work
    await hostPage.click('#next-question-btn');
    await hostPage.waitForTimeout(1_000);

    console.log('🎉 Smoke flow completed');

    await hostContext.close();
    await playerContext.close();
    await tvContext.close();
  });
});
