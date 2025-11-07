// Host Dashboard JavaScript

class HostDashboard {
  constructor() {
    this.socket = null;
    this.roomCode = null;
    this.gameState = "setup"; // setup, lobby, playing, finished
    this.currentQuestion = null;
    this.timer = null;
    this.timeRemaining = 30;
    this.currentPhase = "setup";
    this.minigameTargets = [];
    this.finalSprintInfo = { positions: {}, goal: null };
    this.playerDirectory = {};

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
  }

  bindEvents() {
    const createBtn = document.getElementById("create-game-btn");
    if (createBtn) {
      createBtn.addEventListener("click", (e) => {
        e.preventDefault();
        this.createGame();
      });
      console.log("✅ Create Game button event listener bound");
    } else {
      console.error("❌ Create Game button not found for event binding");
    }

    // Allow Enter key to create game
    const hostNameInput = document.getElementById("host-name");
    if (hostNameInput) {
      hostNameInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
          e.preventDefault();
          this.createGame();
        }
      });
      console.log("✅ Host name Enter key listener bound");
    }

    const startBtn = document.getElementById("start-game-btn");
    if (startBtn) {
      startBtn.addEventListener("click", () => {
        this.startGame();
      });
    }

    const revealBtn = document.getElementById("reveal-answer-btn");
    if (revealBtn) {
      revealBtn.addEventListener("click", () => {
        this.revealAnswer();
      });
    }

    const nextBtn = document.getElementById("next-question-btn");
    if (nextBtn) {
      nextBtn.addEventListener("click", () => {
        this.nextQuestion();
      });
    }

    const newGameBtn = document.getElementById("new-game-btn");
    if (newGameBtn) {
      newGameBtn.addEventListener("click", () => {
        this.resetForNewGame();
      });
    }
  }

  async createGame() {
    console.log("🚀 createGame() function called!");

    const hostName = app.getValue("host-name");
    console.log("Host name from input:", hostName);

    if (!hostName.trim()) {
      console.log("❌ No host name provided");
      app.showError("Please enter your name", "host-name");
      return;
    }

    console.log("✅ Host name valid, making API call...");
    try {
      const response = await app.apiCall("/game/create", {
        method: "POST",
        body: JSON.stringify({ host_name: hostName }),
      });

      console.log("📡 API response:", response);

      if (response.success) {
        console.log("✅ Game created successfully!");
        console.log("🏠 Room code:", response.room_code);
        console.log("🔑 Host token:", response.host_token);

        // Store host token in sessionStorage for subsequent requests
        sessionStorage.setItem(`host_token_${response.room_code}`, response.host_token);

        console.log("🎯 Redirecting to lobby page...");
        // Redirect to the lobby page with the room code
        window.location.href = `/host/lobby?room=${response.room_code}`;
      } else {
        console.log("❌ API returned error:", response.message);
        app.showError(response.message);
      }
    } catch (error) {
      console.log("💥 Exception in createGame:", error);
      app.showError("Failed to create game: " + error.message);
    }
  }

  showGameLobby() {
    console.log("🎯 showGameLobby called with roomCode:", this.roomCode);

    // Debug: List all elements with these IDs
    console.log("🔍 Debugging elements...");
    console.log(
      "All elements with 'game' in ID:",
      Array.from(document.querySelectorAll('[id*="game"]')).map((el) => ({
        id: el.id,
        visible: !el.classList.contains("hidden"),
      }))
    );

    // Check if elements exist
    const setupEl = document.getElementById("game-setup");
    const lobbyEl = document.getElementById("game-lobby");
    const roomCodeEl = document.getElementById("room-code");

    console.log(
      "Setup element:",
      setupEl,
      "Classes:",
      setupEl?.classList.value
    );
    console.log(
      "Lobby element:",
      lobbyEl,
      "Classes:",
      lobbyEl?.classList.value
    );
    console.log("Room code element:", roomCodeEl);

    // Hide setup screen
    if (setupEl) {
      console.log("📍 Setup BEFORE hiding:");
      console.log("   - classList:", setupEl.classList.value);
      console.log("   - display:", window.getComputedStyle(setupEl).display);
      console.log("   - offsetHeight:", setupEl.offsetHeight);

      setupEl.classList.add("hidden");

      console.log("📍 Setup AFTER hiding:");
      console.log("   - classList:", setupEl.classList.value);
      console.log("   - display:", window.getComputedStyle(setupEl).display);
      console.log("   - offsetHeight:", setupEl.offsetHeight);
      console.log("✅ Hidden game-setup");
    } else {
      console.error("❌ game-setup element not found");
    }

    // Force show lobby
    if (lobbyEl) {
      console.log("📍 BEFORE removing hidden class:");
      console.log("   - classList:", lobbyEl.classList.value);
      console.log("   - display:", window.getComputedStyle(lobbyEl).display);
      console.log("   - visibility:", window.getComputedStyle(lobbyEl).visibility);
      console.log("   - offsetHeight:", lobbyEl.offsetHeight);
      console.log("   - offsetWidth:", lobbyEl.offsetWidth);

      // Remove the hidden class - this is all we need!
      lobbyEl.classList.remove("hidden");

      console.log("📍 AFTER removing hidden class:");
      console.log("   - classList:", lobbyEl.classList.value);
      console.log("   - display:", window.getComputedStyle(lobbyEl).display);
      console.log("   - visibility:", window.getComputedStyle(lobbyEl).visibility);
      console.log("   - offsetHeight:", lobbyEl.offsetHeight);
      console.log("   - offsetWidth:", lobbyEl.offsetWidth);

      // Force a reflow
      void lobbyEl.offsetHeight;

      // Scroll to the lobby section smoothly
      setTimeout(() => {
        lobbyEl.scrollIntoView({ behavior: "smooth", block: "start" });
        console.log("✅ Scrolled to lobby");
      }, 100);

      console.log("✅ Shown game-lobby");
    } else {
      console.error("❌ game-lobby element not found");
    }
    if (roomCodeEl) {
      roomCodeEl.textContent = this.roomCode;
      console.log("✅ Set room code to:", this.roomCode);
    } else {
      console.error("❌ room-code element not found");
    }

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
    this.playerDirectory = {};
    const playersList = document.getElementById("players-ul");
    if (playersList) {
      playersList.innerHTML = "";

      players.forEach((player) => {
        this.playerDirectory[player.id] = player.name;
        const li = document.createElement("li");
        const statusText = player.status === "alive" ? "" : " [GHOST]";
        li.textContent = `${player.name} (${player.score} pts)${statusText}`;
        li.className = player.status === "alive" ? "" : "player-ghost";
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
      const response = await app.apiCall(`/game/question/${this.roomCode}/host`);
      if (response.success) {
        this.displayQuestion(response.question);
      } else {
        app.showError(response.message);
      }
    } catch (error) {
      app.showError("Failed to load question: " + error.message);
    }
  }

  resetPhaseUI() {
    this.minigameTargets = [];
    const targetsEl = document.getElementById("minigame-targets");
    const resultsEl = document.getElementById("minigame-results");
    const sprintEl = document.getElementById("final-sprint-status");

    ["minigame-targets", "minigame-results", "final-sprint-status"].forEach((id) => {
      app.hide(id);
    });

    if (targetsEl) targetsEl.innerHTML = "";
    if (resultsEl) resultsEl.innerHTML = "";
    if (sprintEl) sprintEl.innerHTML = "";

    this.setPhaseBanner("");
  }

  setPhaseBanner(message, variant = "default") {
    const banner = document.getElementById("phase-banner");
    if (!banner) return;

    if (!message) {
      banner.className = "phase-banner hidden";
      banner.textContent = "";
      return;
    }

    banner.textContent = message;
    banner.className = `phase-banner phase-${variant}`;
    app.show("phase-banner");
  }

  showMinigameTargets(targetIds = []) {
    const container = document.getElementById("minigame-targets");
    if (!container || !targetIds.length) {
      app.hide("minigame-targets");
      return;
    }

    const names = targetIds.map((id) => this.playerDirectory[id] || id);
    container.innerHTML = `<strong>In danger:</strong> ${names.join(", ")}`;
    app.show("minigame-targets");
  }

  renderMinigameResults(data) {
    const container = document.getElementById("minigame-results");
    if (!container) return;

    if (!data || !data.results || !data.results.length) {
      container.innerHTML = "";
      app.hide("minigame-results");
      return;
    }

    const items = data.results
      .map((entry) => {
        const statusClass = entry.survived ? "minigame-safe" : "minigame-dead";
        const outcome = entry.survived ? "SURVIVED" : "ELIMINATED";
        const choice = entry.choice ? ` (picked ${entry.choice})` : "";
        return `<li class="${statusClass}"><span>${entry.name}</span><span>${outcome}${choice}</span></li>`;
      })
      .join("");

    container.innerHTML = `
      <h4>Killing Floor Results</h4>
      <p>Safe chalice: <strong>${data.safe_answer || "??"}</strong></p>
      <ul>${items}</ul>
    `;

    app.show("minigame-results");
  }

  updateFinalSprintBoard(positions = {}, goal = null) {
    this.finalSprintInfo = { positions, goal };
    const container = document.getElementById("final-sprint-status");
    if (!container) return;

    const entries = Object.entries(positions);
    if (!entries.length) {
      container.innerHTML = "";
      app.hide("final-sprint-status");
      return;
    }

    const rows = entries
      .map(([playerId, progress]) => {
        const name = this.playerDirectory[playerId] || playerId;
        return `<li><span>${name}</span><span>${progress}/${goal || "?"}</span></li>`;
      })
      .join("");

    container.innerHTML = `
      <h4>Final Sprint Progress</h4>
      <p>Goal: first to ${goal || "?"}</p>
      <ul>${rows}</ul>
    `;

    app.show("final-sprint-status");
  }

  setNextButtonDisabled(disabled) {
    const nextBtn = document.getElementById("next-question-btn");
    if (nextBtn) {
      nextBtn.disabled = disabled;
    }
  }

  setRevealButtonDisabled(disabled) {
    const revealBtn = document.getElementById("reveal-answer-btn");
    if (revealBtn) {
      revealBtn.disabled = disabled;
    }
  }

  onMinigameStarted(data) {
    this.currentPhase = "minigame";
    this.minigameTargets = data.targets || [];
    this.setPhaseBanner("KILLING FLOOR", "warning");
    this.showMinigameTargets(this.minigameTargets);
    this.setNextButtonDisabled(true);
    this.setRevealButtonDisabled(true);
  }

  onMinigameResults(data) {
    this.renderMinigameResults(data);
    this.setNextButtonDisabled(false);
  }

  onFinalSprintStarted(data) {
    this.currentPhase = "final_sprint";
    this.setPhaseBanner("FINAL SPRINT", "info");
    this.updateFinalSprintBoard(data.positions || {}, data.goal);
    this.setNextButtonDisabled(true);
    this.setRevealButtonDisabled(true);
  }

  onFinalSprintUpdate(data) {
    if (data.positions) {
      this.updateFinalSprintBoard(data.positions, this.finalSprintInfo.goal);
    }

    if (data.winner_id) {
      const winnerName = this.playerDirectory[data.winner_id] || data.winner_id;
      this.setPhaseBanner(`${winnerName} escaped the final sprint!`, "info");
    }
  }

  displayQuestion(question) {
    this.currentQuestion = question;
    const phase = question.phase || "question";
    this.currentPhase = phase;

    this.resetPhaseUI();

    if (phase === "minigame") {
      this.setPhaseBanner("KILLING FLOOR", "warning");
      const targets = question.targets || this.minigameTargets;
      this.showMinigameTargets(targets);
      this.setNextButtonDisabled(true);
      this.setRevealButtonDisabled(true);
    } else if (phase === "final_sprint") {
      this.setPhaseBanner("FINAL SPRINT", "info");
      this.updateFinalSprintBoard(
        question.sprint_positions || {},
        question.sprint_goal
      );
      this.setNextButtonDisabled(true);
      this.setRevealButtonDisabled(true);
    } else {
      this.setPhaseBanner("QUESTION ROUND", "default");
      this.setNextButtonDisabled(true);
      this.setRevealButtonDisabled(false);
    }

    const contextText =
      phase === "final_sprint"
        ? `Final sprint: first to ${question.sprint_goal || "?"} correct answers escapes.`
        : question.context || "";

    app.setText("question-category", question.category || "");
    app.setText("question-text", question.question_text || "");
    app.setText("question-context", contextText);

    // Display answer options
    const answersGrid = document.getElementById("answers-grid");
    answersGrid.innerHTML = "";

    (question.answers || []).forEach((answer, index) => {
      const answerDiv = document.createElement("div");
      answerDiv.className = "answer-btn";
      answerDiv.textContent = `${String.fromCharCode(65 + index)}) ${answer}`;
      answersGrid.appendChild(answerDiv);
    });

    // Start timer
    this.timeRemaining = question.time_remaining || 30;
    this.startTimer();

    if (phase !== "question") {
      this.setRevealButtonDisabled(true);
    }

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

  async revealAnswer() {
    if (this.timer) {
      clearInterval(this.timer);
    }

    try {
      // Call API to get reveal stats (triggers poll scoring on backend)
      const response = await app.apiCall(`/game/reveal/${this.roomCode}`);

      if (response.success) {
        const stats = response.stats;

        // Check if this is a poll question
        if (stats.is_poll && stats.poll_winner) {
          // POLL QUESTION: Show poll results
          this.showPollResults(stats.poll_winner, stats.answer_breakdown);
        } else {
          // NORMAL QUESTION: Highlight correct answer
          const answersGrid = document.getElementById("answers-grid");
          const answerBtns = answersGrid.children;
          const correctAnswer = response.correct_answer; // Use API response, not cached question

          for (let i = 0; i < answerBtns.length; i++) {
            const btn = answerBtns[i];
            const answerText = btn.textContent.substring(3); // Remove "A) " prefix

            if (answerText === correctAnswer) {
              btn.classList.add("correct");
            } else {
              btn.classList.add("incorrect");
            }
          }
        }

        // Update leaderboard since scores may have changed
        this.updateLeaderboard(await this.getLeaderboard());
      }
    } catch (error) {
      console.error("Error revealing answer:", error);
    }

    document.getElementById("reveal-answer-btn").disabled = true;
    document.getElementById("next-question-btn").disabled = false;
  }

  showPollResults(winner, voteBreakdown) {
    // Show poll winner with special styling
    const answersGrid = document.getElementById("answers-grid");
    const answerBtns = answersGrid.children;

    for (let i = 0; i < answerBtns.length; i++) {
      const btn = answerBtns[i];
      const answerText = btn.textContent.substring(3); // Remove "A) " prefix

      // Find vote count for this option
      const voteInfo = voteBreakdown.find(v => v.answer === answerText);
      const voteCount = voteInfo ? voteInfo.count : 0;

      // Highlight winner in gold
      if (answerText === winner.name) {
        btn.classList.add("poll-winner");
        btn.textContent = `${btn.textContent} - WINNER: ${voteCount} votes (+${winner.points_earned} pts!)`;
      } else {
        btn.classList.add("poll-option");
        btn.textContent = `${btn.textContent} - ${voteCount} votes`;
      }
    }
  }

  async getLeaderboard() {
    try {
      const response = await app.apiCall(`/game/leaderboard/${this.roomCode}`);
      return response.leaderboard || [];
    } catch (error) {
      console.error("Error getting leaderboard:", error);
      return [];
    }
  }

  async nextQuestion() {
    try {
      const response = await app.apiCall(`/game/next/${this.roomCode}`, {
        method: "POST",
      });

      if (response.success) {
        if (response.game_finished) {
          this.showGameResults(response.summary);
        } else if (response.minigame_started) {
          this.setPhaseBanner("KILLING FLOOR", "warning");
          this.setNextButtonDisabled(true);
          this.setRevealButtonDisabled(true);
        } else if (response.final_sprint_started) {
          this.setPhaseBanner("FINAL SPRINT", "info");
          this.setNextButtonDisabled(true);
          this.setRevealButtonDisabled(true);
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
  window.hostDashboard = new HostDashboard();
  console.log("🚀 HostDashboard created and available globally");
});
