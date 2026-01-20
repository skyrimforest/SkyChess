/**
 * Control Component - Manages control panel interactions.
 */

const Control = {
    availableAgents: null,

    /**
     * Initialize control panel.
     */
    async init() {
        // Load available agents
        this.availableAgents = await API.getAvailableAgents();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Render agent parameters
        this.renderAgentParams('white', State.whiteAgent.type);
        this.renderAgentParams('black', State.blackAgent.type);
    },

    /**
     * Setup event listeners.
     */
    setupEventListeners() {
        // New game button
        $('#newGameBtn').on('click', async () => {
            await App.newGame();
        });

        // Reset game button
        $('#resetGameBtn').on('click', async () => {
            await App.resetGame();
        });

        // AI move button
        $('#aiMoveBtn').on('click', async () => {
            await App.makeAIMove();
        });

        // Auto play toggle
        $('#autoPlayToggle').on('change', (e) => {
            if (e.target.checked) {
                State.startAutoPlay();
            } else {
                State.stopAutoPlay();
            }
        });

        // White agent type change
        $('#whiteAgentType').on('change', (e) => {
            const type = e.target.value;
            this.renderAgentParams('white', type);
            this.updateAgent('white', type);
        });

        // Black agent type change
        $('#blackAgentType').on('change', (e) => {
            const type = e.target.value;
            this.renderAgentParams('black', type);
            this.updateAgent('black', type);
        });
    },

    /**
     * Render agent parameters.
     */
    renderAgentParams(color, agentType) {
        const container = $(`#${color}AgentParams`);
        container.empty();

        const agent = this.availableAgents.agents.find(a => a.type === agentType);
        if (!agent || !agent.parameters || agent.parameters.length === 0) {
            return;
        }

        agent.parameters.forEach(param => {
            const group = $('<div class="control-group">');
            
            const label = $(`<label>${this.formatLabel(param.name)}</label>`);
            group.append(label);

            if (param.type === 'integer' || param.type === 'float') {
                if (param.max && param.min) {
                    // Range slider
                    const inputGroup = $('<div class="parameter-input">');
                    const input = $(`<input type="range" min="${param.min}" max="${param.max}" step="${param.type === 'integer' ? 1 : 0.1}" value="${param.default}">`);
                    const valueDisplay = $(`<span class="parameter-value">${param.default}</span>`);
                    
                    input.on('input', (e) => {
                        valueDisplay.text(e.target.value);
                        this.updateAgentParam(color, param.name, parseFloat(e.target.value));
                    });
                    
                    inputGroup.append(input);
                    inputGroup.append(valueDisplay);
                    group.append(inputGroup);
                } else {
                    // Number input
                    const input = $(`<input type="number" value="${param.default}" step="${param.type === 'integer' ? 1 : 0.1}">`);
                    input.on('change', (e) => {
                        this.updateAgentParam(color, param.name, parseFloat(e.target.value));
                    });
                    group.append(input);
                }
            } else if (param.type === 'boolean') {
                const toggle = $('<div class="toggle-switch">');
                const input = $(`<input type="checkbox" ${param.default ? 'checked' : ''}>`);
                input.on('change', (e) => {
                    this.updateAgentParam(color, param.name, e.target.checked);
                });
                toggle.append(input);
                toggle.append(`<label>${this.formatLabel(param.name)}</label>`);
                group.append(toggle);
            }

            container.append(group);
        });
    },

    /**
     * Format parameter label.
     */
    formatLabel(name) {
        return name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    },

    /**
     * Update agent type.
     */
    async updateAgent(color, type) {
        const config = { type };
        
        // Add default parameters
        const agent = this.availableAgents.agents.find(a => a.type === type);
        if (agent && agent.parameters) {
            agent.parameters.forEach(param => {
                config[param.name] = param.default;
            });
        }

        State.updateAgent(color, config);

        if (State.gameId) {
            try {
                await API.setAgent(State.gameId, color, config);
            } catch (error) {
                console.error('Failed to update agent:', error);
            }
        }
    },

    /**
     * Update agent parameter.
     */
    async updateAgentParam(color, paramName, value) {
        const agentKey = color === 'white' ? 'whiteAgent' : 'blackAgent';
        const config = { ...State[agentKey] };
        config[paramName] = value;
        
        State.updateAgent(color, config);

        if (State.gameId) {
            try {
                await API.setAgent(State.gameId, color, config);
            } catch (error) {
                console.error('Failed to update agent parameter:', error);
            }
        }
    },

    /**
     * Update connection status.
     */
    updateConnectionStatus(connected) {
        const dot = $('#statusDot');
        const status = $('#connectionStatus');
        
        if (connected) {
            dot.removeClass('disconnected').addClass('connected');
            status.text('Connected');
        } else {
            dot.removeClass('connected').addClass('disconnected');
            status.text('Disconnected');
        }
    },

    /**
     * Update AI indicator.
     */
    setAIThinking(thinking) {
        const indicator = $('#aiIndicator');
        if (thinking) {
            indicator.addClass('active');
        } else {
            indicator.removeClass('active');
        }
    }
};
