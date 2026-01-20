"""
Engine-based agent for chess.

This module provides agents that wrap search engines,
allowing engines to be used as decision-making strategies.
"""

from typing import Optional
from .base import ChessAgent
from ..game.game_state import GameState
from ..game.types import Color, ChessMove
from ..game.chess_game import ChessGame
from ..engine.base import SearchEngine


class EngineBasedAgent(ChessAgent):
    """
    Agent that uses a search engine to choose moves.
    
    This agent wraps any SearchEngine (Minimax, MCTS, Stockfish, etc.)
    and uses it to select moves. The engine is called for each move
    with the current game state.
    """
    
    name = "EngineBasedAgent"
    
    def __init__(
        self,
        engine: SearchEngine,
        time_limit: Optional[float] = None,
        depth_limit: Optional[int] = None
    ):
        """
        Initialize the engine-based agent.
        
        Args:
            engine: The SearchEngine to use
            time_limit: Default time limit for searches (None = no limit)
            depth_limit: Default depth limit for searches (None = no limit)
        """
        super().__init__()
        self.engine = engine
        self.time_limit = time_limit
        self.depth_limit = depth_limit
    
    def act(self, state: GameState) -> ChessMove:
        """
        Choose a move using the search engine.
        
        Args:
            state: The current GameState
        
        Returns:
            The best ChessMove found by the engine
        """
        # Create a game from the state
        game = ChessGame(state.fen)
        
        # Use the engine to find the best move
        return self.engine.search(
            game,
            time_limit=self.time_limit,
            depth_limit=self.depth_limit
        )
    
    def set_time_limit(self, time_limit: Optional[float]) -> None:
        """
        Set the time limit for searches.
        
        Args:
            time_limit: Maximum search time in seconds (None = no limit)
        """
        self.time_limit = time_limit
    
    def set_depth_limit(self, depth_limit: Optional[int]) -> None:
        """
        Set the depth limit for searches.
        
        Args:
            depth_limit: Maximum search depth (None = no limit)
        """
        self.depth_limit = depth_limit


class MinimaxAgent(EngineBasedAgent):
    """
    Convenience agent using Minimax engine.
    """
    
    name = "MinimaxAgent"
    
    def __init__(
        self,
        evaluator,
        depth: int = 4,
        time_limit: Optional[float] = None,
        use_quiescence: bool = False
    ):
        """
        Initialize the Minimax agent.
        
        Args:
            evaluator: The evaluation function to use
            depth: Search depth
            time_limit: Time limit in seconds
            use_quiescence: Whether to use quiescence search
        """
        from ..engine.minimax import MinimaxEngine
        engine = MinimaxEngine(evaluator, depth, use_quiescence)
        super().__init__(engine, time_limit, depth)


class MCTSAgent(EngineBasedAgent):
    """
    Convenience agent using MCTS engine.
    """
    
    name = "MCTSAgent"
    
    def __init__(
        self,
        evaluator=None,
        exploration_weight: float = 1.414,
        time_limit: float = 1.0,
        rollout_depth: int = 10,
        use_evaluation_rollout: bool = False
    ):
        """
        Initialize the MCTS agent.
        
        Args:
            evaluator: Optional evaluator for rollout policy
            exploration_weight: UCT exploration constant
            time_limit: Search time limit in seconds
            rollout_depth: Maximum rollout depth
            use_evaluation_rollout: Use evaluation-based rollouts
        """
        from ..engine.mcts import MCTSEngine
        engine = MCTSEngine(
            evaluator=evaluator,
            exploration_weight=exploration_weight,
            rollout_depth=rollout_depth,
            use_evaluation_rollout=use_evaluation_rollout
        )
        super().__init__(engine, time_limit)


class StockfishAgent(EngineBasedAgent):
    """
    Convenience agent using Stockfish engine.
    """
    
    name = "StockfishAgent"
    
    def __init__(
        self,
        stockfish_path: Optional[str] = None,
        skill_level: int = 20,
        depth: Optional[int] = None,
        time_limit: Optional[float] = None,
        threads: int = 1,
        hash_size: int = 128
    ):
        """
        Initialize the Stockfish agent.
        
        Args:
            stockfish_path: Path to Stockfish executable
            skill_level: Engine skill level (0-20)
            depth: Search depth (None = auto)
            time_limit: Time limit in seconds
            threads: Number of threads
            hash_size: Hash table size in MB
        """
        from ..engine.stockfish_engine import StockfishEngine
        engine = StockfishEngine(
            stockfish_path=stockfish_path,
            skill_level=skill_level,
            depth=depth,
            threads=threads,
            hash_size=hash_size
        )
        super().__init__(engine, time_limit, depth)
