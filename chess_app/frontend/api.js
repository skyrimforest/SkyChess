/**
 * API Module - Handles HTTP requests to the backend.
 */

const API = {
    baseUrl: '',

    /**
     * Create a new game.
     */
    async newGame() {
        const response = await fetch(`${this.baseUrl}/game/new`, {
            method: 'POST'
        });
        return response.json();
    },

    /**
     * Reset a game.
     */
    async resetGame(gameId) {
        const response = await fetch(`${this.baseUrl}/game/reset/${gameId}`, {
            method: 'POST'
        });
        return response.json();
    },

    /**
     * Get the current game state.
     */
    async getState(gameId) {
        const response = await fetch(`${this.baseUrl}/game/state/${gameId}`);
        return response.json();
    },

    /**
     * Get legal moves for the current position.
     */
    async getLegalMoves(gameId) {
        const response = await fetch(`${this.baseUrl}/game/legal_moves/${gameId}`);
        return response.json();
    },

    /**
     * Make a move.
     */
    async makeMove(gameId, move) {
        const response = await fetch(`${this.baseUrl}/game/move/${gameId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ move })
        });
        return response.json();
    },

    /**
     * Make an AI move.
     */
    async makeAIMove(gameId) {
        const response = await fetch(`${this.baseUrl}/game/ai_move/${gameId}`, {
            method: 'POST'
        });
        return response.json();
    },

    /**
     * Set an agent for a player.
     */
    async setAgent(gameId, color, agentConfig) {
        const response = await fetch(`${this.baseUrl}/game/set_agent/${gameId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ color, agent: agentConfig })
        });
        return response.json();
    },

    /**
     * Get available agents.
     */
    async getAvailableAgents() {
        const response = await fetch(`${this.baseUrl}/agents/available`);
        return response.json();
    }
};
