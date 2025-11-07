// Host Results JavaScript

class HostResults {
  constructor() {
    this.roomCode = null;
    this.init();
  }

  init() {
    // Get room code from URL
    const urlParams = new URLSearchParams(window.location.search);
    this.roomCode = urlParams.get('room');

    if (!this.roomCode) {
      alert('No room code provided!');
      window.location.href = '/host';
      return;
    }

    console.log('🏆 Results page initialized with room code:', this.roomCode);

    // Display room code
    document.getElementById('room-code-display').textContent = this.roomCode;

    // Load game results
    this.loadResults();

    // Rotate roast messages
    this.rotateRoasts();
  }

  async loadResults() {
    try {
      // Fetch leaderboard
      const leaderboardResponse = await app.apiCall(`/game/leaderboard/${this.roomCode}`);
      const leaderboard = leaderboardResponse.leaderboard;

      // Fetch game stats
      const statsResponse = await app.apiCall(`/game/stats/${this.roomCode}`);
      const stats = statsResponse;

      if (leaderboard && leaderboard.length > 0) {
        this.displayPodium(leaderboard);
        this.displayFullLeaderboard(leaderboard);
        this.displayStats(stats, leaderboard);
      } else {
        console.error('No leaderboard data');
      }
    } catch (error) {
      console.error('❌ Error loading results:', error);
      app.showError('Failed to load results: ' + error.message);
    }
  }

  displayPodium(leaderboard) {
    const podiumContainer = document.getElementById('podium');
    podiumContainer.innerHTML = '';

    // Get top 3
    const top3 = leaderboard.slice(0, 3);

    // Podium order: 2nd, 1st, 3rd (visual arrangement)
    const podiumOrder = [1, 0, 2]; // Indices for 2nd, 1st, 3rd place

    podiumOrder.forEach(index => {
      if (top3[index]) {
        const player = top3[index];
        const position = document.createElement('div');
        position.className = `podium-position rank-${player.rank}`;

        const rankText = player.rank === 1 ? '#1' : player.rank === 2 ? '#2' : '#3';

        position.innerHTML = `
          <div class="podium-rank">${rankText}</div>
          <div class="podium-player">
            <div class="podium-player-name">${player.name}</div>
            <div class="podium-player-score">${player.score} pts</div>
          </div>
          <div class="podium-base">${this.getOrdinal(player.rank)} PLACE</div>
        `;

        podiumContainer.appendChild(position);

        // Animate entrance
        gsap.from(position, {
          opacity: 0,
          y: 50,
          duration: 0.8,
          delay: index * 0.2,
          ease: 'back.out(1.7)'
        });
      }
    });
  }

  displayFullLeaderboard(leaderboard) {
    const container = document.getElementById('full-leaderboard');
    container.innerHTML = '';

    leaderboard.forEach((player, index) => {
      const item = document.createElement('div');
      item.className = `leaderboard-item ${index < 3 ? `rank-${player.rank}` : ''}`;

      item.innerHTML = `
        <div class="player-info">
          <div class="player-rank">#${player.rank}</div>
          <div class="player-name">${player.name}</div>
        </div>
        <div class="player-score">${player.score} pts</div>
      `;

      container.appendChild(item);

      // Animate entrance
      gsap.from(item, {
        opacity: 0,
        x: -30,
        duration: 0.5,
        delay: 1.5 + (index * 0.1),
        ease: 'power2.out'
      });
    });
  }

  displayStats(stats, leaderboard) {
    // Calculate stats
    const totalPlayers = leaderboard.length;
    const totalQuestions = stats.total_questions || 0;
    const avgScore = leaderboard.length > 0
      ? Math.round(leaderboard.reduce((sum, p) => sum + p.score, 0) / leaderboard.length)
      : 0;

    // Estimate game duration (assuming ~2 min per question)
    const gameDuration = Math.ceil(totalQuestions * 2);

    // Update DOM
    document.getElementById('total-players').textContent = totalPlayers;
    document.getElementById('total-questions').textContent = totalQuestions;
    document.getElementById('game-duration').textContent = gameDuration;
    document.getElementById('avg-score').textContent = avgScore;

    // Animate stats
    gsap.from('.stat-value', {
      textContent: 0,
      duration: 1.5,
      delay: 2,
      ease: 'power1.out',
      snap: { textContent: 1 },
      stagger: 0.2
    });
  }

  getOrdinal(n) {
    const s = ['TH', 'ST', 'ND', 'RD'];
    const v = n % 100;
    return n + (s[(v - 20) % 10] || s[v] || s[0]);
  }

  rotateRoasts() {
    const roasts = [
      "Friendship destruction level: MAXIMUM",
      "Some of you really embarrassed yourselves tonight...",
      "The receipts don't lie",
      "One of you is going home a champion. The rest? Losers.",
      "That was absolutely savage. Time to unpack that trauma.",
      "Hope those friendships weren't too important",
      "Statistics show that someone cried during this game.",
      "Your group chat will never be the same again."
    ];

    let currentIndex = 0;
    const roastBar = document.getElementById('roast-bar');

    setInterval(() => {
      currentIndex = (currentIndex + 1) % roasts.length;
      gsap.to(roastBar, {
        opacity: 0,
        duration: 0.5,
        onComplete: () => {
          roastBar.textContent = roasts[currentIndex];
          gsap.to(roastBar, { opacity: 1, duration: 0.5 });
        }
      });
    }, 5000);
  }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
  window.hostResults = new HostResults();
  console.log('🚀 HostResults created and available globally');
});
