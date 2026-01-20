/**
 * MoveList Component - Manages move history display.
 */

const MoveList = {
    /**
     * Initialize move list.
     */
    init() {
        this.render();
    },

    /**
     * Render move list.
     */
    render() {
        const container = $('#moveList');
        container.empty();

        const history = State.history;
        
        for (let i = 0; i < history.length; i += 2) {
            const moveNumber = (i / 2) + 1;
            const whiteMove = history[i];
            const blackMove = history[i + 1];

            const row = $('<div class="move-row">');
            
            // Move number
            const num = $(`<div class="move-number">${moveNumber}.</div>`);
            row.append(num);

            // White move
            const white = $(`<div class="move white">${this.formatMove(whiteMove)}</div>`);
            white.on('click', () => this.onMoveClick(i));
            row.append(white);

            // Black move
            if (blackMove) {
                const black = $(`<div class="move black">${this.formatMove(blackMove)}</div>`);
                black.on('click', () => this.onMoveClick(i + 1));
                row.append(black);
            }

            // Highlight current move
            if (i === history.length - 1 || (blackMove && i + 1 === history.length - 1)) {
                if (i === history.length - 1) {
                    white.addClass('current');
                } else {
                    black.addClass('current');
                }
            }

            container.append(row);
        }

        // Scroll to bottom
        container.scrollTop(container[0].scrollHeight);
    },

    /**
     * Format move for display.
     */
    formatMove(uciMove) {
        // Convert UCI to SAN (Standard Algebraic Notation)
        if (!Board.chess) {
            return uciMove;
        }

        try {
            const move = Board.chess.move({ from: uciMove.substring(0, 2), to: uciMove.substring(2, 4), promotion: uciMove.substring(4) });
            return move.san;
        } catch (e) {
            return uciMove;
        }
    },

    /**
     * Handle move click.
     */
    onMoveClick(moveIndex) {
        // Navigate to move (future feature: move history navigation)
        console.log('Clicked move at index:', moveIndex);
    }
};
