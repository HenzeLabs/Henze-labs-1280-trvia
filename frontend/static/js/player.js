// Player Dashboard JavaScript

class PlayerDashboard {
  constructor() {
    this.socket = null;
    this.playerId = PLAYER_ID; // From template
    this.roomCode = null;
    this.gameState = "waiting"; // waiting, playing, finished
    this.currentQuestion = null;
    this.hasAnswered = false;
    this.status = "alive";
    this.minigameTargets = [];
    this.finalSprintInfo = { positions: {}, goal: null };
    this.playerDirectory = {};
    this.isCreator = sessionStorage.getItem("is_creator") === "true";
    this.timer = null;
    this.answerButtons = [];
    this.selectedAnswer = null;
    this.overlayProgress = { answered: 0, total: 0 };
    this.overlayEl = null;
    this.overlayMessageEl = null;
    this.overlaySubtextEl = null;
    this.overlayResultEl = null;
    this.countdownTimeout = null;

    this.init();
  }

  init() {
    this.overlayEl = document.getElementById("waiting-next");
    this.overlayMessageEl = document.getElementById("overlay-message");
    this.overlaySubtextEl = document.getElementById("overlay-subtext");
    this.overlayResultEl = document.getElementById("last-answer-result");
    this.initializeSocket();
    this.loadGameInfo();
    this.bindEvents();
  }

  bindEvents() {
    // Start game button for creator
    const startBtn = document.getElementById("start-game-btn");
    if (startBtn) {
      startBtn.addEventListener("click", () => this.startGame());
    }
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

    this.socket.on("question_started", (data) => {
      console.log("Question started received:", data);
      this.displayQuestion(data.question);
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

    this.socket.on("minigame_started", (data) => {
      this.onMinigameStarted(data);
    });

    this.socket.on("minigame_results", (data) => {
      this.onMinigameResults(data);
    });

    this.socket.on("final_sprint_started", (data) => {
      this.onFinalSprintStarted(data);
    });

    this.socket.on("final_sprint_update", (data) => {
      this.onFinalSprintUpdate(data);
    });

    this.socket.on("final_sprint_waiting", () => {
      this.setStatusBanner("Waiting on the rest of the room...", "info");
    });

    this.socket.on("all_players_answered", (data) => {
      console.log("All players answered:", data);
      this.setStatusBanner("Everyone's in! Revealing answer...", "info");
      this.overlayProgress = {
        answered: data.answered,
        total: data.total,
      };
      this.showSubmissionOverlay("Everyone's in!", this.getOverlayProgressText());
      this.showCountdownBar((data && data.delay_ms) || 5000);
    });

    this.socket.on("answer_revealed", (data) => {
      console.log("Answer revealed for players:", data);
      this.onAnswerRevealed(data);
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

        // Show start button if creator
        if (this.isCreator) {
          const startBtn = document.getElementById("start-game-btn");
          if (startBtn) {
            startBtn.classList.remove("hidden");
          }
        }

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

  async startGame() {
    if (!this.isCreator) {
      console.log("Only creator can start the game");
      return;
    }

    try {
      const response = await app.apiCall(`/game/start/${this.roomCode}`, {
        method: "POST",
        body: JSON.stringify({
          player_id: this.playerId,
        }),
      });

      if (!response.success) {
        this.showError(response.message || "Failed to start game");
      }
    } catch (error) {
      console.error("Error starting game:", error);
      this.showError("Failed to start game");
    }
  }

  onGameStarted() {
    this.gameState = "playing";
    app.hide("waiting-screen");
    app.show("question-screen");

    // Show status bar and adjust layout
    const statusBar = document.querySelector(".status-bar");
    if (statusBar) {
      statusBar.classList.add("active");
    }
    document.body.classList.add("game-active");
  }

  clearPhaseUI() {
    [
      "status-banner",
      "minigame-panel",
      "minigame-results",
      "final-sprint-track",
    ].forEach((id) => app.hide(id));

    const resultsEl = document.getElementById("minigame-results");
    if (resultsEl) resultsEl.innerHTML = "";
  }

  setStatusBanner(message, variant = "info") {
    const banner = document.getElementById("status-banner");
    if (!banner) return;

    if (!message) {
      banner.className = "status-banner hidden";
      banner.textContent = "";
      return;
    }

    banner.textContent = message;
    banner.className = `status-banner status-${variant}`;
    app.show("status-banner");
  }

  showMinigameMessage(text) {
    const panel = document.getElementById("minigame-panel");
    const messageEl = document.getElementById("minigame-message");
    if (!panel || !messageEl) return;

    if (!text) {
      app.hide("minigame-panel");
      messageEl.textContent = "";
      return;
    }

    messageEl.textContent = text;
    app.show("minigame-panel");
  }

  renderMinigameResults(data) {
    const container = document.getElementById("minigame-results");
    if (!container) return;

    if (!data || !data.results) {
      container.innerHTML = "";
      app.hide("minigame-results");
      return;
    }

    const rows = data.results
      .map((entry) => {
        const mood = entry.survived ? "status-safe" : "status-dead";
        const text = entry.survived ? "SURVIVED" : "ELIMINATED";
        const choice = entry.choice ? ` (picked ${entry.choice})` : "";
        return `<li class="${mood}"><span>${entry.name}</span><span>${text}${choice}</span></li>`;
      })
      .join("");

    container.innerHTML = `
      <h4>Killing Floor Results</h4>
      <p>Safe chalice: <strong>${data.safe_answer || "??"}</strong></p>
      <ul>${rows}</ul>
    `;
    app.show("minigame-results");
  }

  updateFinalSprintTrack(positions = {}, goal = null) {
    this.finalSprintInfo = { positions, goal };
    const container = document.getElementById("final-sprint-track");
    if (!container) return;

    const entries = Object.entries(positions);
    if (!entries.length) {
      container.innerHTML = "";
      app.hide("final-sprint-track");
      return;
    }

    const items = entries
      .map(([playerId, progress]) => {
        const name = this.lookupPlayerName(playerId);
        const marker = playerId === this.playerId ? ">> " : "";
        return `<li><span>${marker}${name}</span><span>${progress}/${
          goal || "?"
        }</span></li>`;
      })
      .join("");

    container.innerHTML = `
      <h4>Final Sprint Progress</h4>
      <p>First to ${goal || "?"} correct answers escapes.</p>
      <ul>${items}</ul>
    `;
    app.show("final-sprint-track");
  }

  disableAnswerButtons() {
    document.querySelectorAll(".answer-btn").forEach((btn) => {
      btn.disabled = true;
    });
  }

  enableAnswerButtons() {
    document.querySelectorAll(".answer-btn").forEach((btn) => {
      btn.disabled = false;
    });
  }

  lookupPlayerName(playerId) {
    return this.playerDirectory[playerId] || playerId;
  }

  onMinigameStarted(data) {
    this.minigameTargets = data.targets || [];
    const isTarget = this.minigameTargets.includes(this.playerId);
    if (isTarget) {
      this.setStatusBanner(
        "Killing Floor! Pick wisely or become a ghost.",
        "warning"
      );
      this.showMinigameMessage("Tap a chalice before the timer ends.");
    } else {
      this.setStatusBanner("You're safe—watch the others risk it all.", "info");
      this.showMinigameMessage("Sit tight while the unlucky few choose.");
    }
  }

  onMinigameResults(data) {
    this.renderMinigameResults(data);
  }

  onFinalSprintStarted(data) {
    this.setStatusBanner(
      "Final sprint! Every correct answer moves you forward.",
      "info"
    );
    this.updateFinalSprintTrack(data.positions || {}, data.goal);
  }

  onFinalSprintUpdate(data) {
    if (data.positions) {
      this.updateFinalSprintTrack(data.positions, this.finalSprintInfo.goal);
    }

    if (data.winner_id) {
      if (data.winner_id === this.playerId) {
        this.setStatusBanner("You escaped! Legend status secured.", "info");
      } else {
        this.setStatusBanner("Final sprint complete!", "info");
      }
    }
  }

  displayQuestion(question) {
    this.clearTimer();
    this.clearCountdownBar();
    this.currentQuestion = question;
    this.hasAnswered = false;
    this.selectedAnswer = null;
    this.clearPhaseUI();
    this.hideSubmissionOverlay();
    this.answerButtons = [];
    const phase = question.phase || "question";

    this.minigameTargets = question.targets || this.minigameTargets;

    app.setText("question-category", question.category || "");
    app.setText("question-text", question.question_text || "");
    app.setText("current-question-num", (question.id ?? 0) + 1);
    if (question.total_questions !== undefined) {
      app.setText("total-questions", question.total_questions);
    }

    const answersContainer = document.getElementById("mobile-answers");
    answersContainer.innerHTML = "";

    const isGhost = this.status !== "alive";
    const isTarget = this.minigameTargets.includes(this.playerId);

    if (phase === "minigame") {
      if (isTarget) {
        this.setStatusBanner("Killing Floor! Pick a chalice.", "warning");
        this.showMinigameMessage(
          "Choose carefully—the wrong chalice turns you into a ghost."
        );
      } else {
        this.setStatusBanner(
          "Safe this round. Watch the chaos unfold.",
          "info"
        );
        this.showMinigameMessage(
          "You're not in danger. Let the others sweat it out."
        );
      }
    } else if (phase === "final_sprint") {
      this.setStatusBanner(
        "Final sprint! Every correct answer pulls you closer to the exit.",
        "info"
      );
      this.updateFinalSprintTrack(
        question.sprint_positions || {},
        question.sprint_goal
      );
    } else if (isGhost) {
      this.setStatusBanner(
        "You're a ghost now. Cheer or boo from the sidelines until the final sprint.",
        "warning"
      );
    } else {
      this.setStatusBanner("");
    }

    (question.answers || []).forEach((answer, index) => {
      const button = document.createElement("button");
      button.className = "answer-btn mobile-answer";
      button.textContent = `${String.fromCharCode(65 + index)}) ${answer}`;
      button.setAttribute("data-testid", `answer-${index}`); // Add test ID for Playwright
      button.dataset.answerValue = answer;

      const canAnswer =
        phase === "final_sprint" ||
        (!isGhost && (phase !== "minigame" || isTarget));

      if (canAnswer) {
        button.onclick = () => this.submitAnswer(answer);
      } else {
        button.disabled = true;
      }

      answersContainer.appendChild(button);
      this.answerButtons.push(button);
    });

    this.timeRemaining = question.time_remaining || 30;
    this.startTimer();

    app.show("question-screen");
    this.hideSubmissionOverlay();
    app.hide("answer-feedback");
  }

  startTimer() {
    // CRITICAL: Clear any existing timer to prevent accumulation
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = null;
    }
    
    this.updateTimerDisplay();

    this.timer = setInterval(() => {
      this.timeRemaining--;
      this.updateTimerDisplay();

      if (this.timeRemaining <= 0) {
        clearInterval(this.timer);
        this.timer = null;
        if (!this.hasAnswered) {
          this.showTimeUp();
        }
      }
    }, 1000);
  }

  updateTimerDisplay() {
    app.setText("time-remaining", this.timeRemaining);
  }

  clearTimer() {
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = null;
    }
  }

  async submitAnswer(answer) {
    if (this.hasAnswered) return;

    const phase = this.currentQuestion
      ? this.currentQuestion.phase || "question"
      : "question";
    const isTarget = (this.currentQuestion?.targets || []).includes(
      this.playerId
    );

    if (phase === "question" && this.status !== "alive") {
      this.showError(
        "Ghosts can't answer normal questions. Wait for the final sprint!"
      );
      return;
    }

    if (phase === "minigame" && !isTarget) {
      this.showError("You're safe this round—no need to answer.");
      return;
    }

    this.hasAnswered = true;
    this.disableAnswerButtons();
    this.markSelectedAnswer(answer);
    this.showSubmissionOverlay("Answer locked!", this.getOverlayProgressText());

    try {
      const response = await app.apiCall("/game/answer", {
        method: "POST",
        body: JSON.stringify({
          player_id: this.playerId,
          answer: answer,
        }),
      });

      if (response.phase === "minigame") {
        this.hideSubmissionOverlay();
        if (response.awaiting) {
          this.setStatusBanner(
            "Choice locked. Waiting for the other victims...",
            "warning"
          );
        }
        return;
      }

      if (response.phase === "final_sprint") {
        this.hideSubmissionOverlay();
        if (response.awaiting) {
          this.setStatusBanner(
            "Answer locked. Waiting on the rest of the room...",
            "info"
          );
        }
        if (response.question_complete && response.positions) {
          this.updateFinalSprintTrack(
            response.positions,
            this.finalSprintInfo.goal
          );
        }
        return;
      }

      this.showAnswerFeedback(response);
      if (typeof response.total_score === "number") {
        this.updateScore(response.total_score);
      }
    } catch (error) {
      console.error("Error submitting answer:", error);
      this.showError("Failed to submit answer");
      this.hasAnswered = false;
      this.enableAnswerButtons();
      this.hideSubmissionOverlay();
    }
  }

  showAnswerFeedback(response) {
    const feedbackDiv = document.getElementById("answer-feedback");
    const messageDiv = document.getElementById("feedback-message");
    const pointsDiv = document.getElementById("points-earned");

    // POLL QUESTIONS: Show vote recorded message
    if (response.is_poll) {
      messageDiv.textContent = `Vote recorded! Waiting for results...`;
      messageDiv.className = "poll-feedback";
      pointsDiv.textContent = "Scores calculated after everyone votes!";
    }
    // NORMAL QUESTIONS: Show correct/incorrect
    else if (response.is_correct) {
      messageDiv.textContent = `Correct! "${response.correct_answer}"`;
      messageDiv.className = "correct-feedback";
      pointsDiv.textContent = `+${response.points_earned} points!`;
    } else {
      messageDiv.textContent = `Wrong! Correct answer: "${response.correct_answer}"`;
      messageDiv.className = "incorrect-feedback";
      pointsDiv.textContent = "No points";
    }

    app.show("answer-feedback");

    this.showWaitingNext();
  }

  showWaitingNext() {
    this.showSubmissionOverlay("Answer submitted!", this.getOverlayProgressText());
  }

  showTimeUp() {
    this.clearTimer();
    const feedbackDiv = document.getElementById("answer-feedback");
    const messageDiv = document.getElementById("feedback-message");
    const pointsDiv = document.getElementById("points-earned");

    messageDiv.textContent = `Time's up!`;
    messageDiv.className = "timeout-feedback";
    pointsDiv.textContent = "No points";

    app.show("answer-feedback");

    this.showSubmissionOverlay("Time's up!", "Waiting for reveal...");
  }

  updateScore(newScore) {
    app.setText("current-score", newScore);
    app.setText("player-score", `${newScore} pts`);
  }

  updatePlayerInfo(players) {
    this.playerDirectory = {};
    players.forEach((player) => {
      this.playerDirectory[player.id] = player.name;
      if (player.id === this.playerId) {
        this.status = player.status || "alive";
        if (player.rank !== undefined) {
          app.setText("current-rank", player.rank);
        }
        if (player.score !== undefined) {
          app.setText("player-score", `${player.score} pts`);
        }
      }
    });
    const alivePlayers = players.filter((player) => player.status === "alive");
    const answeredCount = alivePlayers.filter((player) => player.answered_current)
      .length;
    this.overlayProgress = {
      answered: answeredCount,
      total: alivePlayers.length,
    };
    this.updateOverlayProgressText();
  }

  showCountdownBar(duration = 5000) {
    let bar = document.getElementById("countdown-bar");
    if (!bar) {
      bar = document.createElement("div");
      bar.id = "countdown-bar";
      document.body.appendChild(bar);
    }

    bar.style.width = "100%";
    bar.style.transition = "none";

    requestAnimationFrame(() => {
      bar.style.transition = `width ${duration}ms linear`;
      bar.style.width = "0%";
    });

    if (this.countdownTimeout) {
      clearTimeout(this.countdownTimeout);
      this.countdownTimeout = null;
    }
    this.countdownTimeout = setTimeout(() => {
      if (bar && bar.parentNode) {
        bar.parentNode.removeChild(bar);
      }
      this.countdownTimeout = null;
    }, duration + 200);
  }

  clearCountdownBar() {
    if (this.countdownTimeout) {
      clearTimeout(this.countdownTimeout);
      this.countdownTimeout = null;
    }
    const existingBar = document.getElementById("countdown-bar");
    if (existingBar && existingBar.parentNode) {
      existingBar.parentNode.removeChild(existingBar);
    }
  }

  showSubmissionOverlay(message, subtext = "") {
    if (!this.overlayEl || !this.overlayMessageEl || !this.overlaySubtextEl) {
      return;
    }
    this.overlayMessageEl.textContent = message;
    this.overlaySubtextEl.textContent = subtext || "";
    if (this.overlayResultEl) {
      this.overlayResultEl.textContent = "";
    }
    this.overlayEl.classList.remove("hidden");
  }

  hideSubmissionOverlay() {
    if (this.overlayEl) {
      this.overlayEl.classList.add("hidden");
    }
  }

  getOverlayProgressText() {
    const { answered, total } = this.overlayProgress;
    if (!total) return "";
    const base = `${answered}/${total} answered`;
    if (answered >= total) {
      return `${base} · revealing...`;
    }
    return `${base} · waiting for reveal`;
  }

  updateOverlayProgressText() {
    if (
      !this.overlayEl ||
      this.overlayEl.classList.contains("hidden") ||
      !this.overlaySubtextEl
    ) {
      return;
    }
    const text = this.getOverlayProgressText();
    if (text) {
      this.overlaySubtextEl.textContent = text;
    }
  }

  markSelectedAnswer(answer) {
    this.selectedAnswer = answer;
    this.answerButtons.forEach((btn) => {
      btn.classList.remove("correct", "incorrect", "inactive");
      if (btn.dataset.answerValue === answer) {
        btn.classList.add("selected");
      } else {
        btn.classList.remove("selected");
      }
    });
  }

  resetAnswerButtons() {
    this.answerButtons.forEach((btn) => {
      btn.classList.remove("selected", "correct", "incorrect", "inactive");
    });
  }

  highlightAnswers(correctAnswer) {
    if (!correctAnswer) return;
    this.answerButtons.forEach((btn) => {
      btn.classList.remove("correct", "incorrect", "inactive");
      if (btn.dataset.answerValue === correctAnswer) {
        btn.classList.add("correct");
      } else if (btn.classList.contains("selected")) {
        btn.classList.add("incorrect");
      } else {
        btn.classList.add("inactive");
      }
    });
  }

  onAnswerRevealed(data) {
    this.clearCountdownBar();
    this.hideSubmissionOverlay();
    const correctAnswer = data?.correct_answer;
    if (correctAnswer) {
      this.highlightAnswers(correctAnswer);
      this.setStatusBanner(`Correct answer: ${correctAnswer}`, "success");
    }
    this.showRevealFeedback(data);
  }

  showRevealFeedback(data) {
    const feedbackDiv = document.getElementById("answer-feedback");
    const messageDiv = document.getElementById("feedback-message");
    const pointsDiv = document.getElementById("points-earned");
    if (!feedbackDiv || !messageDiv || !pointsDiv) return;

    messageDiv.textContent = `Correct answer: "${data?.correct_answer || "??"}"`;
    messageDiv.className = "reveal-feedback";

    if (data?.stats?.is_poll && data.stats.poll_winner) {
      const winner = data.stats.poll_winner;
      pointsDiv.textContent = `${winner.name} +${winner.points_earned} pts`;
    } else {
      pointsDiv.textContent = "Next question is loading...";
    }

    feedbackDiv.classList.remove("hidden");
  }

  showFinalResults(summary) {
    this.clearTimer();
    this.hideSubmissionOverlay();
    app.hide("question-screen");
    app.show("final-results");

    // Find this player's final position
    const thisPlayer = summary.leaderboard.find((p) => p.player_id === this.playerId);
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
        player.player_id === this.playerId ? "current-player" : ""
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
  window.player = new PlayerDashboard();
});
