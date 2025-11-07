// Host Lobby JavaScript

class HostLobby {
  constructor() {
    this.socket = null;
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

    console.log('🏠 Lobby initialized with room code:', this.roomCode);

    // Display room code
    document.getElementById('room-code').textContent = this.roomCode;

    // Set TV view link
    const tvLink = document.getElementById('tv-view-link');
    if (tvLink) {
      tvLink.href = `/tv/${this.roomCode}`;
    }

    // Initialize socket
    this.initializeSocket();

    // Bind events
    this.bindEvents();

    // Join host to the room
    this.joinHostToRoom();

    // Load initial players
    this.loadPlayers();
  }

  initializeSocket() {
    this.socket = io();

    this.socket.on('connect', () => {
      console.log('✅ Connected to server');
    });

    this.socket.on('player_list_updated', (data) => {
      console.log('📝 Player list updated:', data);
      this.updatePlayersList(data.players);
    });

    this.socket.on('player_joined', (data) => {
      console.log('👋 Player joined:', data.player_name);
    });

    this.socket.on('game_started', () => {
      console.log('🎮 Game started!');
      this.navigateToGamePlay();
    });
  }

  bindEvents() {
    const startBtn = document.getElementById('start-game-btn');
    if (startBtn) {
      startBtn.addEventListener('click', () => {
        this.startGame();
      });
    }
  }

  joinHostToRoom() {
    console.log('🔌 Joining room:', this.roomCode);
    this.socket.emit('join_room', { room_code: this.roomCode });
  }

  async loadPlayers() {
    try {
      const response = await app.apiCall(`/game/stats/${this.roomCode}`);
      console.log('📊 Game stats:', response);

      const playerCount = response.total_players || 0;
      document.getElementById('player-count').textContent = playerCount;

      // Enable start button if there are players
      const startBtn = document.getElementById('start-game-btn');
      if (startBtn) {
        startBtn.disabled = playerCount === 0;
      }
    } catch (error) {
      console.error('❌ Error loading players:', error);
    }
  }

  updatePlayersList(players) {
    const playersList = document.getElementById('players-ul');
    if (!playersList) return;

    playersList.innerHTML = '';

    players.forEach((player) => {
      const li = document.createElement('li');
      li.textContent = `${player.name} (${player.score} pts)`;
      playersList.appendChild(li);
    });

    // Update player count
    const playerCountElement = document.getElementById('player-count');
    if (playerCountElement) {
      playerCountElement.textContent = players.length;
    }

    // Enable start button if there are players
    const startBtn = document.getElementById('start-game-btn');
    if (startBtn) {
      startBtn.disabled = players.length === 0;
    }

    console.log('✅ Updated players list:', players.length, 'players');
  }

  async startGame() {
    console.log('🚀 Starting game...');

    try {
      const response = await app.apiCall(`/game/start/${this.roomCode}`, {
        method: 'POST',
      });

      if (response.success) {
        console.log('✅ Game started successfully!');
        // The socket event will handle navigation
      } else {
        app.showError(response.message);
      }
    } catch (error) {
      console.error('❌ Error starting game:', error);
      app.showError('Failed to start game: ' + error.message);
    }
  }

  navigateToGamePlay() {
    console.log('🎮 Navigating to game play page...');
    window.location.href = `/host/play?room=${this.roomCode}`;
  }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
  window.hostLobby = new HostLobby();
  console.log('🚀 HostLobby created and available globally');
});
