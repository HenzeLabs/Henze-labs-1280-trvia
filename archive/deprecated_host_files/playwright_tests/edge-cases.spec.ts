import { test, expect } from '@playwright/test';
import { TriviaSession, resolveDeviceProfile } from './support/triviaSession';

test.describe('Multiplayer Edge Cases', () => {
  test.setTimeout(300_000);

  test('rejects late joiners once the game starts', async ({ browser }, testInfo) => {
    const profile = resolveDeviceProfile(testInfo.project.name);
    const session = await TriviaSession.launch(browser, {
      hostName: `LateJoin-${testInfo.project.name}`,
      playerNames: ['Alpha', 'Beta'],
      profile,
    });

    const lateContext = await browser.newContext({ viewport: profile.playerViewport });
    const latePage = await lateContext.newPage();
    try {
      await session.startGame();
      await latePage.goto('/join');
      await latePage.fill('#room-code', session.roomCode);
      await latePage.fill('#player-name', 'TooLate');
      await latePage.click('#join-game-btn');

      await expect(latePage.locator('#join-error')).toHaveText(/already started/i);
      await expect(session.hostPage.locator('#players-ul li')).toHaveCount(2);
    } finally {
      await lateContext.close();
      await session.teardown();
    }
  });

  test('player can reconnect mid-round without losing context', async ({ browser }, testInfo) => {
    const profile = resolveDeviceProfile(testInfo.project.name);
    const session = await TriviaSession.launch(browser, {
      hostName: `Reconnect-${testInfo.project.name}`,
      playerNames: ['Nova', 'Quinn', 'Rory'],
      profile,
    });

    let reconnectContext;
    try {
      await session.startGame();
      const question = await session.waitForNextQuestion();
      await session.broadcastSync(question);

      const target = session.players[0];
      const targetId = target.id;
      await target.context.close();
      session.players = session.players.filter(player => player.id !== targetId);

      reconnectContext = await browser.newContext({ viewport: profile.playerViewport });
      const reconnectPage = await reconnectContext.newPage();
      await reconnectPage.goto(`/player/${targetId}`);
      await reconnectPage.waitForSelector('#question-screen', { timeout: 15_000 });
      const bannerText = (await reconnectPage.locator('#status-banner').textContent()) ?? '';
      expect(bannerText.toLowerCase()).not.toContain('error');

      await reconnectContext.close();
    } finally {
      if (reconnectContext && reconnectContext.isClosed() === false) {
        await reconnectContext.close();
      }
      await session.teardown();
    }
  });

  test('simultaneous answers update the TV board in sync', async ({ browser }, testInfo) => {
    const profile = resolveDeviceProfile(testInfo.project.name);
    const session = await TriviaSession.launch(browser, {
      hostName: `Simul-${testInfo.project.name}`,
      playerNames: ['Ava', 'Blake', 'Cruz', 'Dee'],
      profile,
    });

    try {
      await session.startGame();
      const question = await session.waitForNextQuestion();
      await session.broadcastSync(question);

      const correctIndex = question.answers.findIndex(ans => ans === question.correct_answer);
      await Promise.all(
        session.players.map(async player => {
          const buttons = player.page.locator('.answer-btn');
          await buttons.first().waitFor({ state: 'visible', timeout: 10_000 });
          await buttons.nth(correctIndex).click();
        })
      );

      await session.waitForAllPlayersAnswered();
      await session.hostPage.locator('#reveal-answer-btn').click({ force: true });
      await session.hostPage.waitForTimeout(750);

      const answeredIndicators = await session.tvPage.locator('#tv-answer-status .answered').count();
      expect(answeredIndicators).toBe(session.players.length);
    } finally {
      await session.teardown();
    }
  });

  test('scoreboard maintains ties without crashing rankings', async ({ browser }, testInfo) => {
    const profile = resolveDeviceProfile(testInfo.project.name);
    const session = await TriviaSession.launch(browser, {
      hostName: `Tie-${testInfo.project.name}`,
      playerNames: ['Echo', 'Fae', 'Gage', 'Hex'],
      profile,
    });

    try {
      await session.startGame();
      const question = await session.waitForNextQuestion();
      await session.broadcastSync(question);

      const wrongAnswer = question.answers.find(ans => ans !== question.correct_answer) ?? question.answers[0];
      await Promise.all(
        session.players.map(async player => {
          const buttons = player.page.locator('.answer-btn');
          await buttons.first().waitFor({ state: 'visible', timeout: 10_000 });
          const index = question.answers.findIndex(ans => ans === wrongAnswer);
          await buttons.nth(index >= 0 ? index : 0).click();
        })
      );

      await session.waitForAllPlayersAnswered();
      await session.hostPage.locator('#reveal-answer-btn').click({ force: true });
      await session.hostPage.waitForTimeout(750);

      const leaderboard = await session.fetchLeaderboard();
      const scores = leaderboard.map(entry => entry.score);
      expect(new Set(scores).size).toBe(1);
      leaderboard.forEach((entry, index) => {
        expect(entry.rank).toBe(index + 1);
      });
    } finally {
      await session.teardown();
    }
  });

  test('ghosts cannot answer normal questions and stay out of later minigames', async ({ browser }, testInfo) => {
    const profile = resolveDeviceProfile(testInfo.project.name);
    const session = await TriviaSession.launch(browser, {
      hostName: `Ghost-${testInfo.project.name}`,
      playerNames: ['Ivy', 'Jace', 'Kira', 'Luz'],
      profile,
    });

    try {
      await session.startGame();

      // First question: split answers to trigger a minigame
      const initialQuestion = await session.waitForNextQuestion();
      await session.broadcastSync(initialQuestion);
      await session.answerQuestionSplit(initialQuestion);
      await session.waitForAllPlayersAnswered();
      await session.hostPage.locator('#reveal-answer-btn').click({ force: true });
      await session.hostPage.waitForTimeout(750);
      await session.hostPage.locator('#next-question-btn').click({ force: true });

      const minigameQuestion = await session.waitForNextQuestion();
      expect(minigameQuestion.phase).toBe('minigame');

      const targets = await session.hostPage.evaluate(() => {
        const dashboard = (window as any).hostDashboard;
        return dashboard?.minigameTargets ?? [];
      });
      expect(targets.length).toBeGreaterThan(0);

      await session.handleMinigame(minigameQuestion);
      const afterFirstMinigame = await session.fetchLeaderboard();
      const ghostEntry = afterFirstMinigame.find(entry => entry.status === 'ghost');
      expect(ghostEntry).toBeDefined();

      const ghostPlayer = session.players.find(player => player.id === ghostEntry!.player_id);
      expect(ghostPlayer).toBeDefined();

      const followUpQuestion = await session.waitForNextQuestion();
      expect(followUpQuestion.phase).toBe('question');
      await session.broadcastSync(followUpQuestion);

      const ghostButtons = ghostPlayer!.page.locator('.answer-btn');
      await ghostButtons.first().waitFor({ state: 'visible', timeout: 10_000 });
      expect(await ghostButtons.first().isEnabled()).toBeFalsy();

      const alivePlayers = session.players.filter(player => player.id !== ghostEntry!.player_id);
      const wrongAnswer = followUpQuestion.answers.find(ans => ans !== followUpQuestion.correct_answer) ?? followUpQuestion.answers[0];
      await Promise.all(
        alivePlayers.map(async player => {
          const buttons = player.page.locator('.answer-btn');
          await buttons.first().waitFor({ state: 'visible', timeout: 10_000 });
          const index = followUpQuestion.answers.findIndex(ans => ans === wrongAnswer);
          await buttons.nth(index >= 0 ? index : 0).click();
        })
      );

      await session.waitForAllPlayersAnswered();
      await session.hostPage.locator('#reveal-answer-btn').click({ force: true });
      await session.hostPage.waitForTimeout(750);
      await session.hostPage.locator('#next-question-btn').click({ force: true });

      const secondMinigame = await session.waitForNextQuestion();
      expect(secondMinigame.phase).toBe('minigame');
      const secondTargets = await session.hostPage.evaluate(() => {
        const dashboard = (window as any).hostDashboard;
        return dashboard?.minigameTargets ?? [];
      });
      expect(secondTargets).not.toContain(ghostEntry!.player_id);
    } finally {
      await session.teardown();
    }
  });
});
