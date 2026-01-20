/**
 * Board Component - Manages chess board display and interaction.
 */

const Board = {
    board: null,
    chess: null,
    selectedSquare: null,

    /**
     * Initialize the board.
     */
    init() {
        this.chess = new Chess();
        this.board = Chessboard('board', {
            position: 'start',
            draggable: true,
            onDragStart: this.onDragStart.bind(this),
            onDrop: this.onDrop.bind(this),
            onSnapEnd: this.onSnapEnd.bind(this),
            pieceTheme: this.pieceTheme.bind(this)
        });
    },

    /**
     * Custom piece theme (using standard images).
     */
    pieceTheme(piece) {
        return `https://chessboardjs.com/img/chesspieces/wikipedia/${piece}.png`;
    },

    /**
     * Handle drag start.
     */
    onDragStart(source, piece) {
        // Don't allow drag if game is over
        if (State.isTerminal) {
            return false;
        }

        // Don't allow drag if it's not the player's turn
        const pieceColor = piece[0] === 'w' ? 'white' : 'black';
        if (pieceColor !== State.currentPlayer) {
            return false;
        }

        // Don't allow drag if piece is not legal to move
        const legalMoves = State.legalMoves;
        const canMove = legalMoves.some(move => move.startsWith(source));
        if (!canMove) {
            return false;
        }
    },

    /**
     * Handle piece drop.
     */
    async onDrop(source, target) {
        // Remove highlight
        this.clearHighlights();

        // Check if move is legal
        const move = `${source}${target}`;
        const legalMoves = State.legalMoves;
        const isLegal = legalMoves.some(m => m === move);

        if (!isLegal) {
            return 'snapback';
        }

        try {
            // Make move
            await API.makeMove(State.gameId, move);
        } catch (error) {
            console.error('Move error:', error);
            return 'snapback';
        }
    },

    /**
     * Handle snap end.
     */
    onSnapEnd() {
        this.selectedSquare = null;
    },

    /**
     * Update board position from FEN.
     */
    updatePosition(fen) {
        if (this.board) {
            this.board.position(fen);
        }
    },

    /**
     * Highlight legal moves for a square.
     */
    highlightMoves(square) {
        this.clearHighlights();
        this.selectedSquare = square;

        // Find legal moves from this square
        const legalMoves = State.legalMoves.filter(m => m.startsWith(square));
        
        // Highlight target squares
        legalMoves.forEach(move => {
            const target = move.substring(2, 4);
            const $square = $(`.square-${target}`);
            $square.addClass('highlight');
        });
    },

    /**
     * Clear all highlights.
     */
    clearHighlights() {
        $('.highlight').removeClass('highlight');
        this.selectedSquare = null;
    },

    /**
     * Handle square click.
     */
    onSquareClick(square) {
        if (State.isTerminal) {
            return;
        }

        if (this.selectedSquare) {
            // Try to make move
            const move = `${this.selectedSquare}${square}`;
            const legalMoves = State.legalMoves;
            const isLegal = legalMoves.some(m => m === move);

            if (isLegal) {
                API.makeMove(State.gameId, move);
            } else {
                this.clearHighlights();
            }
        } else {
            // Select square and highlight moves
            this.highlightMoves(square);
        }
    }
};
