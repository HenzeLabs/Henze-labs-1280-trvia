// 1280 Trivia - Main JavaScript utilities

class TriviaApp {
    constructor() {
        this.apiBase = '/api';
        this.init();
    }

    init() {
        // Common initialization
        this.setupErrorHandling();
        this.setupUtilities();
    }

    setupErrorHandling() {
        window.addEventListener('error', (event) => {
            console.error('Global error:', event.error);
            this.showError('An unexpected error occurred');
        });
    }

    setupUtilities() {
        // Add utility methods to window for global access
        window.formatTime = this.formatTime;
        window.showSuccess = this.showSuccess;
        window.showError = this.showError;
        window.apiCall = this.apiCall.bind(this);
    }

    // API call wrapper
    async apiCall(endpoint, options = {}) {
        const url = `${this.apiBase}${endpoint}`;
        const defaultHeaders = {
            'Content-Type': 'application/json'
        };

        // Add host token if this is a host-only endpoint
        if (endpoint.includes('/host') || endpoint.includes('/reveal/') || endpoint.includes('/question/')) {
            // Extract room code from endpoint
            const roomMatch = endpoint.match(/\/([A-Z0-9]{6})/);
            if (roomMatch) {
                const roomCode = roomMatch[1];
                const hostToken = sessionStorage.getItem(`host_token_${roomCode}`);
                if (hostToken) {
                    defaultHeaders['X-Host-Token'] = hostToken;
                }
            }
        }

        const defaultOptions = {
            headers: defaultHeaders
        };

        try {
            const response = await fetch(url, { ...defaultOptions, ...options });
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || 'API call failed');
            }

            return data;
        } catch (error) {
            console.error('API call error:', error);
            throw error;
        }
    }

    // Utility functions
    formatTime(seconds) {
        return seconds.toString().padStart(2, '0');
    }

    showSuccess(message, containerId = 'admin-results') {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = `<div class="success-message">${message}</div>`;
            container.scrollTop = container.scrollHeight;
        }
    }

    showError(message, containerId = 'admin-results') {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = `<div class="error-message">${message}</div>`;
            container.scrollTop = container.scrollHeight;
        } else {
            // Fallback to alert if container doesn't exist
            console.error('Error:', message);
            alert(message);
        }
    }

    // Element helpers
    show(elementId) {
        const element = document.getElementById(elementId);
        if (element) element.classList.remove('hidden');
    }

    hide(elementId) {
        const element = document.getElementById(elementId);
        if (element) element.classList.add('hidden');
    }

    setText(elementId, text) {
        const element = document.getElementById(elementId);
        if (element) element.textContent = text;
    }

    setHTML(elementId, html) {
        const element = document.getElementById(elementId);
        if (element) element.innerHTML = html;
    }

    getValue(elementId) {
        const element = document.getElementById(elementId);
        return element ? element.value : '';
    }

    setValue(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) element.value = value;
    }
}

// Initialize the app
const app = new TriviaApp();

// Make utilities available globally
window.app = app;