/**
 * Eval Component - Manages evaluation display.
 */

const Eval = {
    /**
     * Initialize eval component.
     */
    init() {
        // Initial update
        this.update(0);
    },

    /**
     * Update evaluation display.
     */
    update(evalScore) {
        const fill = $('#evalFill');
        const value = $('#evalValue');

        // Clamp eval score
        const clamped = Math.max(-10, Math.min(10, evalScore));
        
        // Calculate fill percentage (50% = 0 eval)
        const percentage = 50 - (clamped * 5);
        fill.css('height', `${percentage}%`);

        // Update value display
        if (evalScore > 0) {
            value.text(`+${evalScore.toFixed(2)}`);
            fill.css('background', 'linear-gradient(to top, #e94560, #ff6b6b)');
        } else if (evalScore < 0) {
            value.text(evalScore.toFixed(2));
            fill.css('background', 'linear-gradient(to top, #533483, #7b2cbf)');
        } else {
            value.text('0.00');
            fill.css('background', 'linear-gradient(to top, #666, #888)');
        }
    }
};
