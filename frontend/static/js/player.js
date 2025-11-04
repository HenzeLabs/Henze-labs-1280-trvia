// Player Dashboard JavaScript

class PlayerDashboard {
  constructor() {
    this.socket = null;
    this.playerId = PLAYER_ID; // From template
    this.roomCode = null;
    this.gameState = "waiting"; // waiting, playing, finished
    this.currentQuestion = null;
    this.hasAnswered = false;

    this.init();
  }

  init() {
    this.initializeSocket();
    this.loadGameInfo();
  }

  initializeSocket() {
    this.socket = io();

    this.socket.on("connect", () => {
      console.log("Player connected to server");
      if (this.roomCode) {
        console.log("Joining room:", this.roomCode);
        this.joinRoom();
      } else {
        console.log("No room code available yet");
      }
    });

    this.socket.on("game_started", () => {
      console.log("Game started event received");
      this.onGameStarted();
    });

    this.socket.on("new_question", (data) => {
      console.log("New question received:", data);
      this.displayQuestion(data.question);
    });

    this.socket.on("game_finished", (data) => {
      console.log("Game finished event received");
      this.showFinalResults(data.summary);
    });

    this.socket.on("player_list_updated", (data) => {
      console.log("Player list updated:", data);
      this.updatePlayerInfo(data.players);
    });
  }

  async loadGameInfo() {
    try {
      console.log("Loading game info for player:", this.playerId);
      // Get the player's session info
      const session = await this.getPlayerSession();
      console.log("Player session:", session);
      if (session) {
        this.roomCode = session.room_code;
        console.log("Room code set to:", this.roomCode);
        app.setText("room-code-display", this.roomCode);
        this.joinRoom();
      } else {
        console.log("No session found for player");
      }
    } catch (error) {
      console.error("Error loading game info:", error);
      this.showError("Failed to load game information");
    }
  }

  async getPlayerSession() {
    // This would need to be implemented in the backend
    // For now, we'll extract from URL or use a different approach
    const pathParts = window.location.pathname.split("/");
    if (pathParts.length >= 3 && pathParts[1] === "player") {
      // Try to get session info via API call
      try {
        const response = await app.apiCall(
          `/game/player-session/${this.playerId}`
        );
        return response.session;
      } catch (error) {
        console.error("Could not get player session:", error);
        return null;
      }
    }
    return null;
  }

  joinRoom() {
    if (this.roomCode) {
      console.log("Emitting join_room event:", {
        room_code: this.roomCode,
        player_id: this.playerId,
      });
      this.socket.emit("join_room", {
        room_code: this.roomCode,
        player_id: this.playerId,
      });
    } else {
      console.log("Cannot join room - no room code");
    }
  }

  onGameStarted() {
    this.gameState = "playing";
    app.hide("waiting-screen");
    app.show("question-screen");
  }

  displayQuestion(question) {
    this.currentQuestion = question;
    this.hasAnswered = false;

    app.setText("question-category", question.category);
    app.setText("question-text", question.question_text);

    // Update question counter
    app.setText("current-question-num", question.id + 1);

    // Clear previous answers
    const answersContainer = document.getElementById("mobile-answers");
    answersContainer.innerHTML = "";

    // Create answer buttons
    question.answers.forEach((answer, index) => {
      const button = document.createElement("button");
      button.className = "answer-btn mobile-answer";
      button.textContent = `${String.fromCharCode(65 + index)}) ${answer}`;
      button.onclick = () => this.submitAnswer(answer);
      answersContainer.appendChild(button);
    });

    // Start timer
    this.timeRemaining = question.time_remaining || 30;
    this.startTimer();

    // Show question screen, hide feedback
    app.show("question-screen");
    app.hide("waiting-next");
    app.hide("answer-feedback");
  }

  startTimer() {
    this.updateTimerDisplay();

    this.timer = setInterval(() => {
      this.timeRemaining--;
      this.updateTimerDisplay();

      if (this.timeRemaining <= 0) {
        clearInterval(this.timer);
        if (!this.hasAnswered) {
          this.showTimeUp();
        }
      }
    }, 1000);
  }

  updateTimerDisplay() {
    app.setText("time-remaining", this.timeRemaining);
  }

  async submitAnswer(answer) {
    if (this.hasAnswered) return;

    this.hasAnswered = true;

    // Disable all answer buttons
    const answerButtons = document.querySelectorAll(".answer-btn");
    answerButtons.forEach((btn) => (btn.disabled = true));

    try {
      const response = await app.apiCall("/game/answer", {
        method: "POST",
        body: JSON.stringify({
          player_id: this.playerId,
          answer: answer,
        }),
      });

      this.showAnswerFeedback(response);
      this.updateScore(response.total_score);
    } catch (error) {
      console.error("Error submitting answer:", error);
      this.showError("Failed to submit answer");
    }
  }

  showAnswerFeedback(response) {
    const feedbackDiv = document.getElementById("answer-feedback");
    const messageDiv = document.getElementById("feedback-message");
    const pointsDiv = document.getElementById("points-earned");

    if (response.is_correct) {
      messageDiv.textContent = `✅ Correct! "${response.correct_answer}"`;
      messageDiv.className = "correct-feedback";
      pointsDiv.textContent = `+${response.points_earned} points!`;
    } else {
      messageDiv.textContent = `❌ Wrong! Correct answer: "${response.correct_answer}"`;
      messageDiv.className = "incorrect-feedback";
      pointsDiv.textContent = "No points";
    }

    app.show("answer-feedback");

    // Show waiting screen after 3 seconds
    setTimeout(() => {
      this.showWaitingNext();
    }, 3000);
  }

  showWaitingNext() {
    app.hide("question-screen");
    app.show("waiting-next");
  }

  showTimeUp() {
    const feedbackDiv = document.getElementById("answer-feedback");
    const messageDiv = document.getElementById("feedback-message");
    const pointsDiv = document.getElementById("points-earned");

    messageDiv.textContent = `⏰ Time's up!`;
    messageDiv.className = "timeout-feedback";
    pointsDiv.textContent = "No points";

    app.show("answer-feedback");

    setTimeout(() => {
      this.showWaitingNext();
    }, 2000);
  }

  updateScore(newScore) {
    app.setText("current-score", newScore);
    app.setText("player-score", `${newScore} pts`);
  }

  updatePlayerInfo(players) {
    // Find this player in the list and update rank
    const thisPlayer = players.find((p) => p.id === this.playerId);
    if (thisPlayer) {
      app.setText("current-rank", thisPlayer.rank || "-");
    }
  }

  showFinalResults(summary) {
    app.hide("question-screen");
    app.hide("waiting-next");
    app.show("final-results");

    // Find this player's final position
    const thisPlayer = summary.leaderboard.find((p) => p.id === this.playerId);
    if (thisPlayer) {
      app.setText("final-rank", `#${thisPlayer.rank}`);
      app.setText("final-score", `${thisPlayer.score} points`);
    }

    // Show final leaderboard
    const leaderboard = document.getElementById("player-final-leaderboard");
    leaderboard.innerHTML = "";

    summary.leaderboard.forEach((player, index) => {
      const playerDiv = document.createElement("div");
      playerDiv.className = `leaderboard-item ${
        player.id === this.playerId ? "current-player" : ""
      }`;
      playerDiv.innerHTML = `
                <span>${player.rank}. ${player.name}</span>
                <span>${player.score} pts</span>
            `;
      leaderboard.appendChild(playerDiv);
    });
  }

  showError(message) {
    // Create or update error display
    let errorDiv = document.getElementById("player-error");
    if (!errorDiv) {
      errorDiv = document.createElement("div");
      errorDiv.id = "player-error";
      errorDiv.className = "error-message";
      document.querySelector(".container").appendChild(errorDiv);
    }

    errorDiv.textContent = message;
    errorDiv.classList.remove("hidden");

    // Hide after 5 seconds
    setTimeout(() => {
      errorDiv.classList.add("hidden");
    }, 5000);
  }
}

// Initialize when page loads
document.addEventListener("DOMContentLoaded", () => {
  new PlayerDashboard();
});
