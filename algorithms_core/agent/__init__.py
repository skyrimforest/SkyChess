"""
Agent module for chess decision-making strategies.

This module provides agents that can be used to play chess games,
wrapping different search engines and strategies.
"""

from .base import ChessAgent
from .random_agent import RandomAgent, WeightedRandomAgent, FirstMoveAgent
from .engine_agent import (
    EngineBasedAgent,
    MinimaxAgent,
    MCTSAgent,
    StockfishAgent
)
from .registry import AgentRegistry, register_agent

# Register default agents
AgentRegistry.register("random", RandomAgent)
AgentRegistry.register("weighted_random", WeightedRandomAgent)
AgentRegistry.register("first_move", FirstMoveAgent)
AgentRegistry.register("minimax", MinimaxAgent)
AgentRegistry.register("mcts", MCTSAgent)
AgentRegistry.register("stockfish", StockfishAgent)

__all__ = [
    "ChessAgent",
    "RandomAgent",
    "WeightedRandomAgent",
    "FirstMoveAgent",
    "EngineBasedAgent",
    "MinimaxAgent",
    "MCTSAgent",
    "StockfishAgent",
    "AgentRegistry",
    "register_agent",
]
