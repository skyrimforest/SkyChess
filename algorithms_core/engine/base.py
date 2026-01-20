"""
Base search engine abstraction for chess algorithms.

This module defines the abstract interface for search engines,
allowing different search algorithms to be used interchangeably.
"""

from abc import ABC, abstractmethod
from typing import Optional
from ..game.chess_game import ChessGame
from ..game.types import ChessMove


class SearchEngine(ABC):
    """
    Abstract base class for search engines.
    
    Design Principles:
    - Does NOT hold GameState (stateless search)
    - Uses game.clone() for tree expansion
    - Easy to swap between different search algorithms
    - Time and depth limits for flexible search control
    
    Search engines are responsible for finding the best move
    from a given position using their specific algorithm.
    """
    
    def __init__(self):
        """Initialize the search engine."""
        self._nodes_searched = 0
    
    @property
    def nodes_searched(self) -> int:
        """Return the number of nodes searched in the last search."""
        return self._nodes_searched
    
    @abstractmethod
    def search(
        self,
        game: ChessGame,
        time_limit: Optional[float] = None,
        depth_limit: Optional[int] = None
    ) -> ChessMove:
        """
        Search for the best move from the current position.
        
        Args:
            game: The ChessGame instance (will be cloned, not modified)
            time_limit: Maximum search time in seconds (None = no limit)
            depth_limit: Maximum search depth (None = no limit)
        
        Returns:
            The best ChessMove found
        
        Note:
            The game object is not modified. Search is performed on clones.
        """
        pass
    
    def _reset_stats(self) -> None:
        """Reset search statistics."""
        self._nodes_searched = 0
    
    def _increment_nodes(self) -> None:
        """Increment the node counter."""
        self._nodes_searched += 1
