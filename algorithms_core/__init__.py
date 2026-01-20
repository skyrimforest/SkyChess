"""
Chess Algorithm Core - Research-grade chess algorithm layer.

This module provides a complete algorithm layer for chess research,
including game logic, search algorithms, agents, and game recording.

Core Components:
- game: Chess game environment and state management
- eval: Position evaluation functions
- engine: Search algorithms (Minimax, MCTS, Stockfish)
- agent: Decision-making strategies
- record: Game recording and analysis
- match_runner: Multi-agent match execution

Dependencies:
- python-chess: pip install python-chess
- stockfish: pip install stockfish (for StockfishEngine)
"""

from .game import ChessGame, GameState, Color, ChessMove, GameResult, PieceType
from .eval import Evaluator, MaterialEvaluator, PythonChessEvaluator
from .engine import (
    SearchEngine,
    MinimaxEngine,
    IterativeDeepeningMinimax,
    MCTSEngine,
    MCTSNode,
    StockfishEngine
)
from .agent import (
    ChessAgent,
    RandomAgent,
    WeightedRandomAgent,
    FirstMoveAgent,
    EngineBasedAgent,
    MinimaxAgent,
    MCTSAgent,
    StockfishAgent,
    AgentRegistry,
    register_agent
)
from .record import GameRecord, GameRecordBatch
from .match_runner import MatchRunner, SelfPlayRunner

__all__ = [
    # Game
    "ChessGame",
    "GameState",
    "Color",
    "ChessMove",
    "GameResult",
    "PieceType",
    # Evaluation
    "Evaluator",
    "MaterialEvaluator",
    "PythonChessEvaluator",
    # Engine
    "SearchEngine",
    "MinimaxEngine",
    "IterativeDeepeningMinimax",
    "MCTSEngine",
    "MCTSNode",
    "StockfishEngine",
    # Agent
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
    # Record
    "GameRecord",
    "GameRecordBatch",
    # Match Runner
    "MatchRunner",
    "SelfPlayRunner",
]

__version__ = "0.1.0"
