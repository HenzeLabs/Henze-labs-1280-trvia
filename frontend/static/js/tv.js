// TV Spectator View JavaScript

class TVSpectator {
  constructor() {
    this.socket = null;
    this.roomCode = ROOM_CODE;
    this.gameState = "waiting";
    this.currentQuestion = null;
    this.players = [];
    this.playerDirectory = {};

    this.init();
  }

  init() {
    this.initializeSocket();
    this.loadGameInfo();
    this.setupControls();
  }

  setupControls() {
    // Start Game button
    const startBtn = document.getElementById("start-game-btn");
    if (startBtn) {
      startBtn.addEventListener("click", () => {
        this.socket.emit("start_game", { room_code: this.roomCode });
      });
    }

    // End Game button
    const endBtn = document.getElementById("end-game-btn");
    if (endBtn) {
      endBtn.addEventListener("click", () => {
        if (confirm("Are you sure you want to end this game?")) {
          window.location.href = "/";
        }
      });
    }
  }

  initializeSocket() {
    this.socket = io();

    this.socket.on("connect", () => {
      console.log("TV connected to server");
      this.joinRoom();
      // BUG #16: Restore state after reconnect
      this.restoreGameState();
    });

    this.socket.on("player_list_updated", (data) => {
      console.log("Player list updated:", data);
      this.updatePlayerList(data.players);
    });

    this.socket.on("game_started", () => {
      console.log("Game started");
      this.onGameStarted();
    });

    this.socket.on("new_question", (data) => {
      console.log("New question:", data);
      this.displayQuestion(data.question);
    });

    this.socket.on("question_started", (data) => {
      console.log("Question started:", data);
      this.displayQuestion(data.question);
    });

    this.socket.on("player_answered", (data) => {
      console.log("Player answered:", data);
      this.updateAnswerStatus();
    });

    this.socket.on("all_players_answered", (data) => {
      console.log("All players answered:", data);
      this.setStatusBanner(
        "All players answered! Revealing answer in 5 seconds...",
        ""
      );
      this.showCountdownBar(5000); // 5 second countdown
    });

    this.socket.on("answer_revealed", (data) => {
      console.log("Answer revealed:", data);
      this.revealAnswer(data);
    });

    // Minigame feature removed - dead code cleanup

    this.socket.on("final_sprint_started", (data) => {
      console.log("Final sprint started:", data);
      this.showFinalSprint(data);
    });

    this.socket.on("final_sprint_update", (data) => {
      console.log("Final sprint update:", data);
      this.updateFinalSprint(data);
    });

    this.socket.on("game_finished", (data) => {
      console.log("Game finished:", data);
      this.showFinalLeaderboard(data.summary);
    });

    this.socket.on("leaderboard_updated", (data) => {
      console.log("Leaderboard updated:", data);
      // Could show quick leaderboard flash
    });
  }

  joinRoom() {
    console.log("Joining room:", this.roomCode);
    this.socket.emit("join_room", {
      room_code: this.roomCode,
      role: "spectator",
    });
  }

  async restoreGameState() {
    // BUG #16: Restore state after reconnect
    try {
      const response = await fetch(`/api/game/state/${this.roomCode}`);
      if (!response.ok) {
        console.warn("Could not restore game state");
        return;
      }

      const state = await response.json();
      console.log("Restoring game state:", state);

      // Update local state
      if (state.phase === "question" || state.phase === "reveal") {
        this.currentQuestion = state.current_question;
        this.gameState = state.phase;

        // Restore UI to match current phase
        if (state.phase === "question") {
          this.displayQuestion(state.current_question);
        } else if (state.phase === "reveal" && state.reveal_data) {
          this.showAnswerReveal(state.reveal_data);
        }
      }
    } catch (error) {
      console.error("Error restoring game state:", error);
    }
  }

  async loadGameInfo() {
    try {
      const response = await fetch(`/api/game/stats/${this.roomCode}`);
      const data = await response.json();

      if (data && typeof data === "object") {
        this.updateGameStats(data);
      }
    } catch (error) {
      console.error("Error loading game info:", error);
    }
  }

  updateGameStats(data) {
    document.getElementById("tv-total-questions").textContent =
      data.total_questions || 0;
    document.getElementById("tv-current-question").textContent =
      data.current_question || 0;
  }

  updatePlayerList(players) {
    this.players = players;

    // Update player directory for name lookups
    this.playerDirectory = {};
    players.forEach((player) => {
      this.playerDirectory[player.id] = player.name;
    });

    // Update player count in waiting screen
    document.getElementById("tv-player-count").textContent = players.length;

    // Enable/disable start button based on player count
    const startBtn = document.getElementById("start-game-btn");
    if (startBtn) {
      startBtn.disabled = players.length < 1;
    }
  }

  onGameStarted() {
    this.gameState = "playing";
    this.hide("tv-waiting");
    this.setStatusBanner("Game Starting!", "");
    setTimeout(() => this.clearStatusBanner(), 3000);
  }

  displayQuestion(question) {
    this.currentQuestion = question;
    const phase = question.phase || "question";

    // Hide all screens
    this.hide("tv-waiting");
    this.hide("tv-leaderboard");
    this.hide("tv-minigame");
    this.hide("tv-final-sprint");

    // Update progress
    document.getElementById("tv-current-question").textContent =
      (question.id || 0) + 1;

    if (phase === "minigame") {
      // Minigame will be handled by minigame_started event
      return;
    } else if (phase === "final_sprint") {
      // Final sprint will be handled by final_sprint_started event
      return;
    }

    // Show question screen
    this.show("tv-question");

    // Display question details
    document.getElementById("tv-category").textContent =
      question.category || "";
    document.getElementById("tv-question-text").textContent =
      question.question_text || "";

    // Display answers
    const answersContainer = document.getElementById("tv-answers");
    answersContainer.innerHTML = "";

    (question.answers || []).forEach((answer, index) => {
      const answerDiv = document.createElement("div");
      answerDiv.className = "tv-answer";
      answerDiv.textContent = `${String.fromCharCode(65 + index)}) ${answer}`;
      answerDiv.dataset.answer = answer;
      answersContainer.appendChild(answerDiv);
    });

    // Show answer status indicators
    this.updateAnswerStatus();
    this.clearStatusBanner();
  }

  updateAnswerStatus() {
    const statusContainer = document.getElementById("tv-answer-status");
    statusContainer.innerHTML = "";

    // Get alive players only
    const alivePlayers = this.players.filter((p) => p.status === "alive");

    alivePlayers.forEach((player) => {
      const indicator = document.createElement("div");
      indicator.className = "tv-player-indicator";
      indicator.textContent = player.name;

      if (player.answered_current) {
        indicator.classList.add("answered");
        indicator.textContent += " ✓";
      } else {
        indicator.classList.add("waiting");
        indicator.textContent += " ...";
      }

      statusContainer.appendChild(indicator);
    });
  }

  revealAnswer(data) {
    const correctAnswer = data.correct_answer;

    // Highlight correct answer
    const answerElements = document.querySelectorAll(".tv-answer");
    answerElements.forEach((el) => {
      if (el.dataset.answer === correctAnswer) {
        el.classList.add("correct");
      } else {
        el.classList.add("incorrect");
      }
    });

    // Clear answer status
    document.getElementById("tv-answer-status").innerHTML = "";

    // Show banner
    this.setStatusBanner(`Correct Answer: ${correctAnswer}`, "");
  }

  showMinigame(data) {
    // Hide question screen
    this.hide("tv-question");
    this.show("tv-minigame");

    const message = data.message || "Choose your chalice wisely...";
    document.getElementById("tv-minigame-message").textContent = message;

    // Clear results initially
    document.getElementById("tv-minigame-results").innerHTML = "";

    this.setStatusBanner("KILLING FLOOR Active!", "danger");
  }

  showMinigameResults(data) {
    const resultsContainer = document.getElementById("tv-minigame-results");
    resultsContainer.innerHTML = "";

    if (!data.results || data.results.length === 0) {
      return;
    }

    // Show safe answer
    if (data.safe_answer) {
      const safeDiv = document.createElement("div");
      safeDiv.style.cssText =
        "font-size: 42px; margin-bottom: 40px; color: #4CAF50;";
      safeDiv.textContent = `Safe Chalice: ${data.safe_answer}`;
      resultsContainer.appendChild(safeDiv);
    }

    // Show each player's result
    data.results.forEach((result) => {
      const resultDiv = document.createElement("div");
      resultDiv.className = `tv-minigame-result ${
        result.survived ? "survived" : "eliminated"
      }`;

      const nameSpan = document.createElement("span");
      nameSpan.textContent = result.name;

      const statusSpan = document.createElement("span");
      if (result.survived) {
        statusSpan.textContent = "SURVIVED";
        statusSpan.style.color = "#4CAF50";
      } else {
        statusSpan.textContent = "ELIMINATED";
        statusSpan.style.color = "#F44336";
      }

      resultDiv.appendChild(nameSpan);
      resultDiv.appendChild(statusSpan);
      resultsContainer.appendChild(resultDiv);
    });

    this.setStatusBanner("Killing Floor Results", "danger");
  }

  showFinalSprint(data) {
    this.hide("tv-question");
    this.hide("tv-minigame");
    this.show("tv-final-sprint");

    const goal = data.goal || 5;
    document.getElementById("tv-sprint-goal").textContent = goal;

    this.updateFinalSprintProgress(data.positions || {}, goal);
    this.setStatusBanner("FINAL SPRINT - Race to the Exit!", "warning");
  }

  updateFinalSprint(data) {
    if (data.positions) {
      const goal = data.goal || 5;
      this.updateFinalSprintProgress(data.positions, goal);
    }

    if (data.winner_id) {
      const winnerName = this.playerDirectory[data.winner_id] || data.winner_id;
      this.setStatusBanner(`${winnerName} ESCAPED!`, "");
    }
  }

  updateFinalSprintProgress(positions, goal) {
    const progressContainer = document.getElementById("tv-sprint-progress");
    progressContainer.innerHTML = "";

    // Sort players by progress
    const sortedPlayers = Object.entries(positions).sort((a, b) => b[1] - a[1]);

    sortedPlayers.forEach(([playerId, progress]) => {
      const playerDiv = document.createElement("div");
      playerDiv.className = "tv-sprint-player";

      const nameSpan = document.createElement("span");
      nameSpan.className = "tv-sprint-player-name";
      nameSpan.textContent = this.playerDirectory[playerId] || playerId;

      const progressSpan = document.createElement("span");
      progressSpan.className = "tv-sprint-player-progress";
      progressSpan.textContent = `${progress} / ${goal}`;

      const barDiv = document.createElement("div");
      barDiv.className = "tv-sprint-bar";

      const barFill = document.createElement("div");
      barFill.className = "tv-sprint-bar-fill";
      barFill.style.width = `${(progress / goal) * 100}%`;

      barDiv.appendChild(barFill);
      playerDiv.appendChild(nameSpan);
      playerDiv.appendChild(barDiv);
      playerDiv.appendChild(progressSpan);

      progressContainer.appendChild(playerDiv);
    });
  }

  showFinalLeaderboard(summary) {
    // Hide all other screens
    this.hide("tv-waiting");
    this.hide("tv-question");
    this.hide("tv-minigame");
    this.hide("tv-final-sprint");

    // Show leaderboard
    this.show("tv-leaderboard");

    const listContainer = document.getElementById("tv-leaderboard-list");
    listContainer.innerHTML = "";

    summary.leaderboard.forEach((player, index) => {
      const itemDiv = document.createElement("div");
      itemDiv.className = `tv-leaderboard-item rank-${player.rank}`;

      const rankSpan = document.createElement("span");
      rankSpan.className = "tv-leaderboard-rank";
      rankSpan.textContent = `#${player.rank}`;

      const nameSpan = document.createElement("span");
      nameSpan.className = "tv-leaderboard-name";
      nameSpan.textContent = player.name;

      const scoreSpan = document.createElement("span");
      scoreSpan.className = "tv-leaderboard-score";
      scoreSpan.textContent = `${player.score} pts`;

      itemDiv.appendChild(rankSpan);
      itemDiv.appendChild(nameSpan);
      itemDiv.appendChild(scoreSpan);

      listContainer.appendChild(itemDiv);
    });

    this.setStatusBanner("Game Complete!", "");
  }

  setStatusBanner(message, variant = "") {
    const banner = document.getElementById("tv-status-banner");

    if (!message) {
      banner.classList.add("hidden");
      return;
    }

    banner.textContent = message;
    banner.className = "tv-status-banner";

    if (variant) {
      banner.classList.add(variant);
    }

    this.show("tv-status-banner");
  }

  clearStatusBanner() {
    this.setStatusBanner("");
  }



  show(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
      element.classList.remove("hidden");
    }
  }

  hide(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
      element.classList.add("hidden");
    }
  }

  showCountdownBar(duration) {
    // Create countdown progress bar
    let bar = document.getElementById("countdown-bar");
    if (!bar) {
      bar = document.createElement("div");
      bar.id = "countdown-bar";
      bar.className = "countdown-bar";
      document.body.appendChild(bar);
    }
    
    // Reset and animate
    bar.style.width = "100%";
    bar.style.transition = "none";
    
    setTimeout(() => {
      bar.style.transition = `width ${duration}ms linear`;
      bar.style.width = "0%";
    }, 50);
    
    // Remove after animation
    setTimeout(() => {
      if (bar && bar.parentNode) {
        bar.parentNode.removeChild(bar);
      }
    }, duration + 100);
  }
}

// Initialize when page loads
document.addEventListener("DOMContentLoaded", () => {
  new TVSpectator();
});
