/**
 * App Module - Main application logic.
 */

const App = {
    eventSource: null,

    /**
     * Initialize application.
     */
    async init() {
        // Initialize components
        Board.init();
        Control.init();
        Eval.init();
        MoveList.init();

        // Create new game on load
        await this.newGame();
    },

    /**
     * Create a new game.
     */
    async newGame() {
        try {
            // Stop auto play
            State.stopAutoPlay();

            // Create new game
            const data = await API.newGame();
            State.gameId = data.game_id;
            State.reset();

            // Set agents
            await API.setAgent(State.gameId, 'white', State.whiteAgent);
            await API.setAgent(State.gameId, 'black', State.blackAgent);

            // Connect to SSE
            this.connectSSE();

            // Update UI
            this.updateUI();
        } catch (error) {
            console.error('Failed to create game:', error);
            alert('Failed to create game. Please try again.');
        }
    },

    /**
     * Reset current game.
     */
    async resetGame() {
        if (!State.gameId) {
            return;
        }

        try {
            State.stopAutoPlay();
            await API.resetGame(State.gameId);
            State.reset();
            this.updateUI();
        } catch (error) {
            console.error('Failed to reset game:', error);
            alert('Failed to reset game. Please try again.');
        }
    },

    /**
     * Make an AI move.
     */
    async makeAIMove() {
        if (!State.gameId || State.isTerminal) {
            return;
        }

        try {
            Control.setAIThinking(true);
            await API.makeAIMove(State.gameId);
        } catch (error) {
            console.error('Failed to make AI move:', error);
            alert('Failed to make AI move. Please try again.');
        } finally {
            Control.setAIThinking(false);
        }
    },

    /**
     * Connect to SSE event stream.
     */
    connectSSE() {
        // Close existing connection
        if (this.eventSource) {
            this.eventSource.close();
        }

        // Create new connection
        this.eventSource = new EventSource(`/events/${State.gameId}`);

        // Connection opened
        this.eventSource.onopen = () => {
            State.setConnected(true);
            Control.updateConnectionStatus(true);
        };

        // Connection closed
        this.eventSource.onclose = () => {
            State.setConnected(false);
            Control.updateConnectionStatus(false);
        };

        // Connection error
        this.eventSource.onerror = () => {
            State.setConnected(false);
            Control.updateConnectionStatus(false);
        };

        // State event
        this.eventSource.addEventListener('state', (e) => {
            const data = JSON.parse(e.data);
            this.onStateUpdate(data);
        });

        // AI move event
        this.eventSource.addEventListener('ai_move', (e) => {
            const data = JSON.parse(e.data);
            console.log('AI move:', data);
        });

        // Game over event
        this.eventSource.addEventListener('game_over', (e) => {
            const data = JSON.parse(e.data);
            this.onGameOver(data);
        });
    },

    /**
     * Handle state update.
     */
    onStateUpdate(data) {
        // Update state
        State.updateState(data);

        // Update UI
        this.updateUI();

        // Update legal moves
        this.updateLegalMoves();
    },

    /**
     * Handle game over.
     */
    onGameOver(data) {
        State.isTerminal = true;
        State.result = data.result;
        State.stopAutoPlay();

        // Update status
        const status = $('#gameStatus');
        if (data.result === 'white_win') {
            status.text('White wins!');
        } else if (data.result === 'black_win') {
            status.text('Black wins!');
        } else {
            status.text('Draw!');
        }
    },

    /**
     * Update UI from state.
     */
    updateUI() {
        // Update board
        if (State.fen) {
            Board.updatePosition(State.fen);
            if (Board.chess) {
                Board.chess.load(State.fen);
            }
        }

        // Update turn indicator
        const turn = $('#turnIndicator');
        if (State.currentPlayer === 'white') {
            turn.text('White to move');
        } else {
            turn.text('Black to move');
        }

        // Update evaluation
        Eval.update(State.eval);

        // Update move list
        MoveList.render();

        // Update game status
        const status = $('#gameStatus');
        if (State.isTerminal) {
            if (State.result === 'white_win') {
                status.text('White wins!');
            } else if (State.result === 'black_win') {
                status.text('Black wins!');
            } else {
                status.text('Draw!');
            }
        } else {
            status.text('');
        }
    },

    /**
     * Update legal moves.
     */
    async updateLegalMoves() {
        if (!State.gameId) {
            return;
        }

        try {
            const data = await API.getLegalMoves(State.gameId);
            State.updateLegalMoves(data.moves);
        } catch (error) {
            console.error('Failed to get legal moves:', error);
        }
    }
};

// Initialize app when DOM is ready
$(document).ready(() => {
    App.init();
});
