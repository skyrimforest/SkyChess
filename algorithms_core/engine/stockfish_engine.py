"""
Stockfish engine adapter using the stockfish Python library.

This module provides a wrapper around Stockfish chess engine,
allowing it to be used as a SearchEngine in the algorithm layer.
"""

import time
from typing import Optional
from .base import SearchEngine
from ..game.chess_game import ChessGame
from ..game.types import ChessMove


class StockfishEngine(SearchEngine):
    """
    Stockfish engine adapter using the stockfish library.
    
    Design Principles:
    - Uses stockfish Python library for UCI communication
    - Configurable skill level and search parameters
    - Time limit support
    - No pollution of other engines
    
    Requires:
    - Stockfish executable installed
    - stockfish Python package: pip install stockfish
    """
    
    def __init__(
        self,
        stockfish_path: Optional[str] = None,
        skill_level: int = 20,
        depth: Optional[int] = None,
        threads: int = 1,
        hash_size: int = 128
    ):
        """
        Initialize the Stockfish engine.
        
        Args:
            stockfish_path: Path to Stockfish executable. If None, uses default.
            skill_level: Engine skill level (0-20)
            depth: Default search depth (None = auto)
            threads: Number of threads to use
            hash_size: Hash table size in MB
        """
        super().__init__()
        
        try:
            from stockfish import Stockfish
            self._Stockfish = Stockfish
        except ImportError:
            raise ImportError(
                "stockfish package is required. Install with: pip install stockfish"
            )
        
        self.stockfish_path = stockfish_path
        self.skill_level = skill_level
        self.depth = depth
        self.threads = threads
        self.hash_size = hash_size
        self._engine = None
    
    def _get_engine(self):
        """Get or create the Stockfish engine instance."""
        if self._engine is None:
            self._engine = self._Stockfish(
                path=self.stockfish_path,
                depth=self.depth,
                parameters={
                    "Threads": self.threads,
                    "Hash": self.hash_size,
                    "Skill Level": self.skill_level,
                }
            )
        return self._engine
    
    def search(
        self,
        game: ChessGame,
        time_limit: Optional[float] = None,
        depth_limit: Optional[int] = None
    ) -> ChessMove:
        """
        Search for the best move using Stockfish.
        
        Args:
            game: The ChessGame instance
            time_limit: Maximum search time in seconds (None = use default)
            depth_limit: Maximum search depth (None = use engine default)
        
        Returns:
            The best ChessMove found
        """
        self._reset_stats()
        engine = self._get_engine()
        
        # Set the position
        fen = game.to_fen()
        engine.set_fen_position(fen)
        
        # Configure search
        if depth_limit is not None:
            engine.depth = depth_limit
        elif self.depth is not None:
            engine.depth = self.depth
        
        # Get best move
        if time_limit is not None:
            best_move = engine.get_best_move_time(int(time_limit * 1000))
        else:
            best_move = engine.get_best_move()
        
        if best_move is None:
            # No move found (game over or no legal moves)
            legal_moves = game.legal_moves()
            if legal_moves:
                return legal_moves[0]
            raise ValueError("No legal moves available")
        
        return ChessMove.from_uci(best_move)
    
    def evaluate(self, game: ChessGame) -> dict:
        """
        Evaluate the current position using Stockfish.
        
        Args:
            game: The ChessGame instance
        
        Returns:
            Dictionary with evaluation information
        """
        engine = self._get_engine()
        engine.set_fen_position(game.to_fen())
        
        return engine.get_evaluation()
    
    def get_top_moves(self, game: ChessGame, num_moves: int = 5) -> list:
        """
        Get the top N moves with their evaluations.
        
        Args:
            game: The ChessGame instance
            num_moves: Number of top moves to return
        
        Returns:
            List of dictionaries with move and score information
        """
        engine = self._get_engine()
        engine.set_fen_position(game.to_fen())
        
        return engine.get_top_moves(num_moves)
    
    def set_skill_level(self, level: int) -> None:
        """
        Set the engine skill level.
        
        Args:
            level: Skill level (0-20)
        """
        self.skill_level = max(0, min(20, level))
        if self._engine is not None:
            self._engine.set_skill_level(self.skill_level)
    
    def set_fen_position(self, fen: str) -> None:
        """
        Set the board position from FEN.
        
        Args:
            fen: FEN string
        """
        engine = self._get_engine()
        engine.set_fen_position(fen)
    
    def make_moves_from_current_position(self, moves: list[str]) -> None:
        """
        Make a sequence of moves from the current position.
        
        Args:
            moves: List of UCI move strings
        """
        engine = self._get_engine()
        engine.make_moves_from_current_position(moves)
    
    def close(self) -> None:
        """Close the Stockfish engine."""
        if self._engine is not None:
            del self._engine
            self._engine = None
    
    def __del__(self):
        """Clean up on deletion."""
        self.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
