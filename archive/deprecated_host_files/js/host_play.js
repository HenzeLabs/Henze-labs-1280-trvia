// Host Game Play JavaScript

class HostGamePlay {
  constructor() {
    this.socket = null;
    this.roomCode = null;
    this.currentQuestion = null;
    this.timer = null;
    this.timeRemaining = 30;
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

    console.log('🎮 Game play initialized with room code:', this.roomCode);

    // Display room code
    document.getElementById('room-code-display').textContent = this.roomCode;

    // Initialize socket
    this.initializeSocket();

    // Bind events
    this.bindEvents();

    // Join host to the room
    this.joinHostToRoom();

    // Load first question
    this.loadCurrentQuestion();

    // Start leaderboard updates
    this.startLeaderboardUpdates();
  }

  initializeSocket() {
    this.socket = io();

    this.socket.on('connect', () => {
      console.log('✅ Connected to server');
    });

    this.socket.on('new_question', (data) => {
      console.log('📝 New question received:', data);
      this.displayQuestion(data.question);
    });

    this.socket.on('player_answered', (data) => {
      console.log('✅ Player answered:', data);
      this.updatePlayerStatus(data);
    });

    this.socket.on('game_finished', (data) => {
      console.log('🏁 Game finished!', data);
      alert('Game Over! Redirecting to results...');
      window.location.href = `/host/results?room=${this.roomCode}`;
    });

    this.socket.on('all_players_answered', (data) => {
      console.log('⏩ All players answered:', data);

      // Stop the question timer to prevent race condition with auto-advance
      if (this.timer) {
        clearInterval(this.timer);
        this.timer = null;
        console.log('⏸️  Question timer stopped - waiting for auto-advance');
      }

      // Show banner that game is auto-advancing
      const banner = document.createElement('div');
      banner.className = 'auto-advance-banner';
      banner.textContent = 'All players answered! Next question loading in 5 seconds...';
      banner.style.cssText = 'position: fixed; top: 20px; left: 50%; transform: translateX(-50%); background: #4CAF50; color: white; padding: 15px 30px; border-radius: 8px; z-index: 1000; font-weight: bold;';
      document.body.appendChild(banner);
      setTimeout(() => banner.remove(), 5000);
    });
  }

  bindEvents() {
    const revealBtn = document.getElementById('reveal-answer-btn');
    if (revealBtn) {
      revealBtn.addEventListener('click', () => {
        this.revealAnswer();
      });
    }

    const nextBtn = document.getElementById('next-question-btn');
    if (nextBtn) {
      nextBtn.addEventListener('click', () => {
        this.nextQuestion();
      });
    }
  }

  joinHostToRoom() {
    console.log('🔌 Joining room:', this.roomCode);
    this.socket.emit('join_room', { room_code: this.roomCode });
  }

  async loadCurrentQuestion() {
    try {
      console.log('📥 Loading current question...');
      const response = await app.apiCall(`/game/question/${this.roomCode}/host`);

      if (response.success) {
        console.log('✅ Question loaded:', response.question);
        this.displayQuestion(response.question);
      } else {
        console.error('❌ Error loading question:', response.message);
        app.showError(response.message);
      }
    } catch (error) {
      console.error('❌ Error loading question:', error);
      app.showError('Failed to load question: ' + error.message);
    }
  }

  displayQuestion(question) {
    console.log('🎯 Displaying question:', question);
    this.currentQuestion = question;

    // Set question text
    document.getElementById('question-category').textContent = question.category || 'Roast Session';
    document.getElementById('question-text').textContent = question.question_text;
    document.getElementById('question-context').textContent = question.context || 'Context will appear here...';

    // Display answer options
    const answersGrid = document.getElementById('answers-grid');
    answersGrid.innerHTML = '';

    if (question.answers && question.answers.length > 0) {
      question.answers.forEach((answer, index) => {
        const answerDiv = document.createElement('div');
        answerDiv.className = 'answer-option';
        answerDiv.textContent = `${String.fromCharCode(65 + index)}) ${answer}`;
        answersGrid.appendChild(answerDiv);
      });
    }

    // Start timer
    this.timeRemaining = question.time_remaining || 30;
    this.startTimer();

    // Reset buttons
    document.getElementById('reveal-answer-btn').disabled = false;
    document.getElementById('next-question-btn').disabled = true;

    // Reset player status
    this.resetPlayerStatus();
  }

  startTimer() {
    // Clear any existing timer
    if (this.timer) {
      clearInterval(this.timer);
    }

    this.updateTimerDisplay();

    this.timer = setInterval(() => {
      this.timeRemaining--;
      this.updateTimerDisplay();

      if (this.timeRemaining <= 0) {
        clearInterval(this.timer);
        this.revealAnswer();
      }
    }, 1000);
  }

  updateTimerDisplay() {
    const timerElement = document.getElementById('time-remaining');
    if (timerElement) {
      timerElement.textContent = this.timeRemaining;
    }
  }

  async revealAnswer() {
    console.log('🔍 Revealing answer...');

    if (this.timer) {
      clearInterval(this.timer);
    }

    // Fetch voting stats
    try {
      const response = await app.apiCall(`/game/reveal/${this.roomCode}`);
      const stats = response.stats;

      // Highlight answers and show voting percentages
      const answersGrid = document.getElementById('answers-grid');
      const answerBtns = answersGrid.children;

      for (let i = 0; i < answerBtns.length; i++) {
        const btn = answerBtns[i];
        const answerText = btn.textContent.substring(3); // Remove "A) " prefix

        // Find vote data for this answer
        const voteData = stats.answer_breakdown?.find(a => a.answer === answerText);

        if (answerText === response.correct_answer) {
          btn.classList.add('correct');
          console.log('✅ Correct answer:', answerText);
        } else {
          btn.classList.add('incorrect');
        }

        // Add voting percentage
        if (voteData) {
          const percentage = voteData.percentage;
          const count = voteData.count;
          const voters = voteData.voters.join(', ');

          btn.innerHTML = `
            ${String.fromCharCode(65 + i)}) ${answerText}
            <div style="font-size: 14px; margin-top: 5px; opacity: 0.8;">
              ${percentage}% (${count} ${count === 1 ? 'vote' : 'votes'})
              ${voters ? `<br>${voters}` : ''}
            </div>
          `;
        }
      }

      document.getElementById('reveal-answer-btn').disabled = true;
      document.getElementById('next-question-btn').disabled = false;
    } catch (error) {
      console.error('❌ Error revealing answer:', error);
      // Fall back to basic reveal
      const answersGrid = document.getElementById('answers-grid');
      const answerBtns = answersGrid.children;

      for (let i = 0; i < answerBtns.length; i++) {
        const btn = answerBtns[i];
        const answerText = btn.textContent.substring(3);

        if (answerText === this.currentQuestion.correct_answer) {
          btn.classList.add('correct');
        } else {
          btn.classList.add('incorrect');
        }
      }

      document.getElementById('reveal-answer-btn').disabled = true;
      document.getElementById('next-question-btn').disabled = false;
    }
  }

  async nextQuestion() {
    console.log('⏭️ Loading next question...');

    try {
      const response = await app.apiCall(`/game/next/${this.roomCode}`, {
        method: 'POST',
      });

      if (response.success) {
        if (response.game_finished) {
          console.log('🏁 Game finished!');
          alert('Game Over! Final scores will be shown.');
          window.location.href = `/host/results?room=${this.roomCode}`;
        } else {
          console.log('✅ Next question will be loaded via socket');
          // New question will be loaded via socket event
        }
      } else {
        app.showError(response.message);
      }
    } catch (error) {
      console.error('❌ Error advancing to next question:', error);
      app.showError('Failed to advance to next question: ' + error.message);
    }
  }

  startLeaderboardUpdates() {
    // Update leaderboard every 3 seconds
    const updateLeaderboard = async () => {
      try {
        const response = await app.apiCall(`/game/leaderboard/${this.roomCode}`);
        this.updateLeaderboard(response.leaderboard);
      } catch (error) {
        console.error('❌ Error updating leaderboard:', error);
      }

      // Continue updating
      setTimeout(updateLeaderboard, 3000);
    };

    updateLeaderboard();
  }

  updateLeaderboard(leaderboard) {
    const container = document.getElementById('current-leaderboard');
    if (!container) return;

    container.innerHTML = '';

    leaderboard.forEach((player, index) => {
      const playerDiv = document.createElement('div');
      playerDiv.className = `leaderboard-item ${index === 0 ? 'rank-1' : ''}`;
      playerDiv.innerHTML = `
        <span>${player.rank}. ${player.name}</span>
        <span>${player.score} pts</span>
      `;
      container.appendChild(playerDiv);
    });
  }

  updatePlayerStatus(data) {
    // Update UI to show which players have answered
    console.log('Player status update:', data);

    // Update answered count via stats
    this.updateAnsweredCount();
  }

  async updateAnsweredCount() {
    try {
      const response = await app.apiCall(`/game/stats/${this.roomCode}`);
      const answeredCount = document.getElementById('answered-count');
      if (answeredCount) {
        answeredCount.textContent = response.players_answered || 0;
      }
    } catch (error) {
      console.error('Error updating answered count:', error);
    }
  }

  resetPlayerStatus() {
    // Reset any UI indicators for player answers
    const answeredCount = document.getElementById('answered-count');
    if (answeredCount) {
      answeredCount.textContent = '0';
    }
  }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
  window.hostGamePlay = new HostGamePlay();
  console.log('🚀 HostGamePlay created and available globally');
});
