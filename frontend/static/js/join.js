// Join Game JavaScript

class JoinGame {
    constructor() {
        this.init();
    }

    init() {
        this.bindEvents();
        this.focusRoomCode();
    }

    bindEvents() {
        document.getElementById('join-game-btn').addEventListener('click', () => {
            this.joinGame();
        });

        // Allow Enter key to join
        document.getElementById('room-code').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                document.getElementById('player-name').focus();
            }
        });

        document.getElementById('player-name').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.joinGame();
            }
        });

        // Auto-uppercase room code
        document.getElementById('room-code').addEventListener('input', (e) => {
            e.target.value = e.target.value.toUpperCase();
        });
    }

    focusRoomCode() {
        document.getElementById('room-code').focus();
    }

    async joinGame() {
        const roomCode = app.getValue('room-code').trim().toUpperCase();
        const playerName = app.getValue('player-name').trim();
        
        // Validation
        if (!roomCode) {
            this.showError('Please enter a room code');
            return;
        }
        
        if (roomCode.length !== 6) {
            this.showError('Room code must be 6 characters');
            return;
        }
        
        if (!playerName) {
            this.showError('Please enter your name');
            return;
        }

        if (playerName.length > 20) {
            this.showError('Name must be 20 characters or less');
            return;
        }

        this.showJoining();

        try {
            const response = await app.apiCall('/game/join', {
                method: 'POST',
                body: JSON.stringify({
                    room_code: roomCode,
                    player_name: playerName
                })
            });

            if (response.success) {
                // Persist creator status so the player dashboard can unlock host controls
                sessionStorage.setItem('is_creator', response.is_creator ? 'true' : 'false');
                sessionStorage.setItem('player_id', response.player_id);
                sessionStorage.setItem('room_code', response.room_code);
                // Redirect to player dashboard
                window.location.href = `/player/${response.player_id}`;
            } else {
                this.showError(response.message);
                this.hideJoining();
            }
        } catch (error) {
            this.showError('Failed to join game: ' + error.message);
            this.hideJoining();
        }
    }

    showJoining() {
        app.hide('join-form');
        app.show('joining-game');
    }

    hideJoining() {
        app.show('join-form');
        app.hide('joining-game');
    }

    showError(message) {
        const errorDiv = document.getElementById('join-error');
        errorDiv.textContent = message;
        errorDiv.classList.remove('hidden');
        
        // Hide error after 5 seconds
        setTimeout(() => {
            errorDiv.classList.add('hidden');
        }, 5000);
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    new JoinGame();
});
