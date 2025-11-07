import { test, expect } from '@playwright/test';
import { TriviaSession, resolveDeviceProfile } from './support/triviaSession';

test.describe('Full Game Parity', () => {
  test.setTimeout(600_000); // Allow up to 10 minutes for the exhaustive flow

  test('plays a complete deck with Jackbox-style pacing', async ({ browser }, testInfo) => {
    const profile = resolveDeviceProfile(testInfo.project.name);
    const session = await TriviaSession.launch(browser, {
      hostName: `Host-${testInfo.project.name}`,
      playerNames: ['Lauren', 'Benny', 'Gina', 'Ian'],
      profile,
      log: message => console.log(`[${testInfo.project.name}] ${message}`),
    });

    try {
      await session.playFullGame();

      const metrics = session.getMetrics();
      const questionTypes = metrics.questionTypes;
      const categories = metrics.categories;
      const questionBroadcastDurations = metrics.timings['questionBroadcast'] ?? [];

      expect(metrics.totalQuestions).toBeGreaterThanOrEqual(15);
      expect(metrics.sawMinigame).toBeTruthy();
      expect(metrics.minigameCount).toBeGreaterThan(0);
      expect(metrics.ghostRoster.length).toBeGreaterThan(0);

      expect(metrics.sawFinalSprint).toBeTruthy();
      expect(metrics.finalSprintQuestions).toBeGreaterThan(0);

      expect(questionTypes).toEqual(
        expect.arrayContaining(['receipts', 'roast', 'most_likely', 'trivia', 'poll'])
      );

      expect(categories).toEqual(
        expect.arrayContaining(['KILLING FLOOR', 'SEXY TIME TRIVIA', 'GENERAL KNOWLEDGE'])
      );

      expect(questionBroadcastDurations.length).toBeGreaterThan(0);
      const worstBroadcast = Math.max(...questionBroadcastDurations);
      expect(worstBroadcast).toBeLessThan(3_000);

      expect(metrics.scoreboardSnapshots.length).toBeGreaterThan(5);

      const finalLeaderboard = metrics.finalLeaderboard;
      expect(finalLeaderboard).not.toBeNull();
      expect(finalLeaderboard!.length).toBe(4);
      finalLeaderboard!.forEach((entry, index) => {
        expect(entry.rank).toBe(index + 1);
        expect(typeof entry.score).toBe('number');
      });
    } finally {
      await session.teardown();
    }
  });
});
