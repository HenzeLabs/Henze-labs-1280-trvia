// Host Dashboard JavaScript

class HostDashboard {
  constructor() {
    this.socket = null;
    this.roomCode = null;
    this.gameState = "setup"; // setup, lobby, playing, finished
    this.currentQuestion = null;
    this.timer = null;
    this.timeRemaining = 30;

    this.init();
  }

  init() {
    this.initializeSocket();
    this.bindEvents();
  }

  initializeSocket() {
    this.socket = io();

    this.socket.on("connect", () => {
      console.log("Connected to server");
    });

    this.socket.on("player_list_updated", (data) => {
      this.updatePlayersList(data.players);
    });

    this.socket.on("player_answered", (data) => {
      this.updatePlayerStatus(data);
    });

    this.socket.on("game_started", () => {
      this.startGamePlay();
    });

    this.socket.on("new_question", (data) => {
      this.displayQuestion(data.question);
    });

    this.socket.on("game_finished", (data) => {
      this.showGameResults(data.summary);
    });
  }

  bindEvents() {
    document.getElementById("create-game-btn").addEventListener("click", () => {
      this.createGame();
    });

    document.getElementById("start-game-btn").addEventListener("click", () => {
      this.startGame();
    });

    document
      .getElementById("reveal-answer-btn")
      .addEventListener("click", () => {
        this.revealAnswer();
      });

    document
      .getElementById("next-question-btn")
      .addEventListener("click", () => {
        this.nextQuestion();
      });

    document.getElementById("new-game-btn").addEventListener("click", () => {
      this.resetForNewGame();
    });
  }

  async createGame() {
    const hostName = app.getValue("host-name");
    if (!hostName.trim()) {
      app.showError("Please enter your name", "host-name");
      return;
    }

    try {
      const response = await app.apiCall("/game/create", {
        method: "POST",
        body: JSON.stringify({ host_name: hostName }),
      });

      if (response.success) {
        this.roomCode = response.room_code;
        this.showGameLobby();
        this.joinHostToRoom();
      } else {
        app.showError(response.message);
      }
    } catch (error) {
      app.showError("Failed to create game: " + error.message);
    }
  }

  showGameLobby() {
    app.hide("game-setup");
    app.show("game-lobby");
    app.setText("room-code", this.roomCode);
    this.gameState = "lobby";
    this.loadPlayers();
  }

  joinHostToRoom() {
    this.socket.emit("join_room", { room_code: this.roomCode });
  }

  async loadPlayers() {
    try {
      const response = await app.apiCall(`/game/stats/${this.roomCode}`);
      document.getElementById("player-count").textContent =
        response.total_players || 0;

      // Enable start button if there are players
      const startBtn = document.getElementById("start-game-btn");
      startBtn.disabled = (response.total_players || 0) === 0;
    } catch (error) {
      console.error("Error loading players:", error);
    }
  }

  updatePlayersList(players) {
    const playersList = document.getElementById("players-ul");
    if (playersList) {
      playersList.innerHTML = "";

      players.forEach((player) => {
        const li = document.createElement("li");
        li.textContent = `${player.name} (${player.score} pts)`;
        playersList.appendChild(li);
      });
    }

    // Update player count
    const playerCountElement = document.getElementById("player-count");
    if (playerCountElement) {
      playerCountElement.textContent = players.length;
    }

    // Enable start button if there are players and we're in lobby
    const startBtn = document.getElementById("start-game-btn");
    if (startBtn && this.gameState === "lobby") {
      startBtn.disabled = players.length === 0;
    }

    console.log("Updated players list:", players);
  }

  async startGame() {
    try {
      const response = await app.apiCall(`/game/start/${this.roomCode}`, {
        method: "POST",
      });

      if (response.success) {
        this.startGamePlay();
      } else {
        app.showError(response.message);
      }
    } catch (error) {
      app.showError("Failed to start game: " + error.message);
    }
  }

  startGamePlay() {
    app.hide("game-lobby");
    app.show("game-play");
    this.gameState = "playing";
    this.loadCurrentQuestion();
    this.startLeaderboardUpdates();
  }

  async loadCurrentQuestion() {
    try {
      const response = await app.apiCall(`/game/question/${this.roomCode}`);
      if (response.success) {
        this.displayQuestion(response.question);
      } else {
        app.showError(response.message);
      }
    } catch (error) {
      app.showError("Failed to load question: " + error.message);
    }
  }

  displayQuestion(question) {
    this.currentQuestion = question;

    app.setText("question-category", question.category);
    app.setText("question-text", question.question_text);
    app.setText("question-context", question.context);

    // Display answer options
    const answersGrid = document.getElementById("answers-grid");
    answersGrid.innerHTML = "";

    question.answers.forEach((answer, index) => {
      const answerDiv = document.createElement("div");
      answerDiv.className = "answer-btn";
      answerDiv.textContent = `${String.fromCharCode(65 + index)}) ${answer}`;
      answersGrid.appendChild(answerDiv);
    });

    // Start timer
    this.timeRemaining = question.time_remaining || 30;
    this.startTimer();

    // Reset buttons
    document.getElementById("reveal-answer-btn").disabled = false;
    document.getElementById("next-question-btn").disabled = true;

    // Reset player status
    this.resetPlayerStatus();
  }

  startTimer() {
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
    app.setText("time-remaining", app.formatTime(this.timeRemaining));
  }

  revealAnswer() {
    if (this.timer) {
      clearInterval(this.timer);
    }

    // Highlight correct answer
    const answersGrid = document.getElementById("answers-grid");
    const answerBtns = answersGrid.children;

    for (let i = 0; i < answerBtns.length; i++) {
      const btn = answerBtns[i];
      const answerText = btn.textContent.substring(3); // Remove "A) " prefix

      if (answerText === this.currentQuestion.correct_answer) {
        btn.classList.add("correct");
      } else {
        btn.classList.add("incorrect");
      }
    }

    document.getElementById("reveal-answer-btn").disabled = true;
    document.getElementById("next-question-btn").disabled = false;
  }

  async nextQuestion() {
    try {
      const response = await app.apiCall(`/game/next/${this.roomCode}`, {
        method: "POST",
      });

      if (response.success) {
        if (response.game_finished) {
          this.showGameResults(response.summary);
        } else {
          // New question will be loaded via socket event
        }
      } else {
        app.showError(response.message);
      }
    } catch (error) {
      app.showError("Failed to advance to next question: " + error.message);
    }
  }

  showGameResults(summary) {
    app.hide("game-play");
    app.show("game-results");
    this.gameState = "finished";

    // Display final leaderboard
    const leaderboard = document.getElementById("final-leaderboard");
    leaderboard.innerHTML = "";

    summary.leaderboard.forEach((player, index) => {
      const playerDiv = document.createElement("div");
      playerDiv.className = `leaderboard-item ${
        index === 0
          ? "first"
          : index === 1
          ? "second"
          : index === 2
          ? "third"
          : ""
      }`;
      playerDiv.innerHTML = `
                <span>${player.rank}. ${player.name}</span>
                <span>${player.score} pts</span>
            `;
      leaderboard.appendChild(playerDiv);
    });

    // Display game summary
    const summaryStats = document.getElementById("game-summary-stats");
    summaryStats.innerHTML = `
            <p><strong>Winner:</strong> ${summary.winner.name} with ${summary.winner.score} points!</p>
            <p><strong>Total Players:</strong> ${summary.total_players}</p>
            <p><strong>Questions:</strong> ${summary.total_questions}</p>
            <p><strong>Average Score:</strong> ${summary.average_score}</p>
            <p><strong>Game Duration:</strong> ${summary.game_duration} minutes</p>
            <p><strong>Roast Level:</strong> ${summary.roast_level} 🔥</p>
        `;
  }

  startLeaderboardUpdates() {
    // Update leaderboard every 3 seconds
    const updateLeaderboard = async () => {
      if (this.gameState === "playing") {
        try {
          const response = await app.apiCall(
            `/game/leaderboard/${this.roomCode}`
          );
          this.updateLeaderboard(response.leaderboard);
        } catch (error) {
          console.error("Error updating leaderboard:", error);
        }

        setTimeout(updateLeaderboard, 3000);
      }
    };

    updateLeaderboard();
  }

  updateLeaderboard(leaderboard) {
    const container = document.getElementById("current-leaderboard");
    container.innerHTML = "";

    leaderboard.forEach((player, index) => {
      const playerDiv = document.createElement("div");
      playerDiv.className = `leaderboard-item ${
        index === 0
          ? "first"
          : index === 1
          ? "second"
          : index === 2
          ? "third"
          : ""
      }`;
      playerDiv.innerHTML = `
                <span>${player.rank}. ${player.name}</span>
                <span>${player.score} pts</span>
            `;
      container.appendChild(playerDiv);
    });
  }

  updatePlayerStatus(data) {
    // Update UI to show which players have answered
    // This could be implemented to show checkmarks next to player names
  }

  resetPlayerStatus() {
    // Reset any UI indicators for player answers
    document.getElementById("answered-count").textContent = "0";
  }

  resetForNewGame() {
    app.hide("game-results");
    app.show("game-setup");
    this.gameState = "setup";
    this.roomCode = null;
    this.currentQuestion = null;

    // Clear form
    app.setValue("host-name", "");

    // Reset UI
    document.getElementById("current-leaderboard").innerHTML = "";
  }
}

// Initialize when page loads
document.addEventListener("DOMContentLoaded", () => {
  new HostDashboard();
});
