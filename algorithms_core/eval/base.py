"""
Base evaluator abstraction for chess position evaluation.

This module defines the abstract interface for position evaluators,
allowing different evaluation strategies (material, NN-based, etc.)
to be used interchangeably.
"""

from abc import ABC, abstractmethod
from ..game.game_state import GameState


class Evaluator(ABC):
    """
    Abstract base class for position evaluators.
    
    Design Principles:
    - Decoupled from search algorithms
    - Stateless evaluation (no caching)
    - Returns a float score from the perspective of the current player
    
    Score Convention:
    - Positive values favor the current player (the one to move)
    - Negative values favor the opponent
    - Scale is evaluator-dependent, but typically:
      - Material evaluator: pawn = 100 points
      - NN evaluator: typically in [-1, 1] range
    """
    
    @abstractmethod
    def evaluate(self, state: GameState) -> float:
        """
        Evaluate a game state.
        
        Args:
            state: The GameState to evaluate
        
        Returns:
            Float score from perspective of the player to move.
            Higher values indicate better positions for the current player.
        """
        pass
    
    def evaluate_from_perspective(
        self, 
        state: GameState, 
        color: bool  # True for white, False for black
    ) -> float:
        """
        Evaluate a state from a specific player's perspective.
        
        Args:
            state: The GameState to evaluate
            color: True for white's perspective, False for black's
        
        Returns:
            Float score from the specified player's perspective
        """
        score = self.evaluate(state)
        # If evaluating from black's perspective and it's white's turn,
        # we need to negate the score
        if not color and state.current_player.value == "white":
            return -score
        return score
