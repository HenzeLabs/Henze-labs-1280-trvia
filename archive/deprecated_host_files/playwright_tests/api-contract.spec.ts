import { test, expect } from '@playwright/test';

test.use({ baseURL: 'http://localhost:5001' });

test.describe('Backend Contract', () => {
  test('game lifecycle endpoints return expected payloads', async ({ request }) => {
    const createStart = Date.now();
    const createResponse = await request.post('/api/game/create', {
      data: { host_name: 'Contract Host', num_questions: 5 },
    });
    const createDuration = Date.now() - createStart;

    expect(createResponse.ok()).toBeTruthy();
    const createBody = await createResponse.json();
    expect(createBody.success).toBeTruthy();
    expect(createBody.room_code).toMatch(/^[A-Z0-9]{6}$/);
    expect(createBody.host_token).toHaveLength(32);
    expect(createDuration).toBeLessThan(2_000);

    const roomCode: string = createBody.room_code;
    const hostToken: string = createBody.host_token;

    const joinPromises = ['Ana', 'Beck', 'Cato'].map(name =>
      request.post('/api/game/join', {
        data: { room_code: roomCode, player_name: name },
      })
    );
    const joinResponses = await Promise.all(joinPromises);
    joinResponses.forEach(resp => expect(resp.ok()).toBeTruthy());

    const startResponse = await request.post(`/api/game/start/${roomCode}`);
    expect(startResponse.ok()).toBeTruthy();

    const unauthorized = await request.get(`/api/game/question/${roomCode}/host`);
    expect(unauthorized.status()).toBe(403);

    const hostQuestionResponse = await request.get(`/api/game/question/${roomCode}/host`, {
      headers: { 'X-Host-Token': hostToken },
    });
    expect(hostQuestionResponse.ok()).toBeTruthy();
    const hostQuestionBody = await hostQuestionResponse.json();
    expect(hostQuestionBody.success).toBeTruthy();

    const question = hostQuestionBody.question;
    expect(question).toMatchObject({
      category: expect.any(String),
      question_type: expect.any(String),
      question_text: expect.any(String),
      correct_answer: expect.any(String),
      answers: expect.any(Array),
    });
    expect(question.answers.length).toBeGreaterThanOrEqual(4);
    expect(question.answers).toContain(question.correct_answer);

    const leaderboardResponse = await request.get(`/api/game/leaderboard/${roomCode}`);
    expect(leaderboardResponse.ok()).toBeTruthy();
    const leaderboardBody = await leaderboardResponse.json();
    expect(Array.isArray(leaderboardBody.leaderboard)).toBeTruthy();
    expect(leaderboardBody.leaderboard.length).toBe(3);
    leaderboardBody.leaderboard.forEach((entry: any, index: number) => {
      expect(entry).toMatchObject({
        name: expect.any(String),
        score: expect.any(Number),
        rank: index + 1,
        player_id: expect.any(String),
        status: expect.stringMatching(/alive|ghost/),
      });
    });
  });
});
