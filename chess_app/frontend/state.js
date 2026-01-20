/**
 * State Module - Manages application state.
 */

const State = {
    gameId: null,
    fen: null,
    currentPlayer: null,
    eval: 0,
    history: [],
    isTerminal: false,
    result: null,
    legalMoves: [],
    whiteAgent: { type: 'random' },
    blackAgent: { type: 'random' },
    autoPlay: false,
    autoPlayInterval: null,
    connected: false,

    /**
     * Update game state from server response.
     */
    updateState(data) {
        this.fen = data.fen;
        this.currentPlayer = data.current_player;
        this.eval = data.eval;
        this.history = data.history || [];
        this.isTerminal = data.is_terminal;
        this.result = data.result;
    },

    /**
     * Update legal moves.
     */
    updateLegalMoves(moves) {
        this.legalMoves = moves;
    },

    /**
     * Update agent configuration.
     */
    updateAgent(color, config) {
        if (color === 'white') {
            this.whiteAgent = config;
        } else {
            this.blackAgent = config;
        }
    },

    /**
     * Reset state for new game.
     */
    reset() {
        this.fen = null;
        this.currentPlayer = null;
        this.eval = 0;
        this.history = [];
        this.isTerminal = false;
        this.result = null;
        this.legalMoves = [];
        this.stopAutoPlay();
    },

    /**
     * Start auto play.
     */
    startAutoPlay() {
        this.autoPlay = true;
        this.runAutoPlay();
    },

    /**
     * Stop auto play.
     */
    stopAutoPlay() {
        this.autoPlay = false;
        if (this.autoPlayInterval) {
            clearTimeout(this.autoPlayInterval);
            this.autoPlayInterval = null;
        }
    },

    /**
     * Run auto play step.
     */
    async runAutoPlay() {
        if (!this.autoPlay || this.isTerminal) {
            return;
        }

        try {
            await API.makeAIMove(this.gameId);
            
            if (this.autoPlay && !this.isTerminal) {
                this.autoPlayInterval = setTimeout(() => this.runAutoPlay(), 500);
            }
        } catch (error) {
            console.error('Auto play error:', error);
            this.stopAutoPlay();
        }
    },

    /**
     * Set connection status.
     */
    setConnected(connected) {
        this.connected = connected;
    }
};
