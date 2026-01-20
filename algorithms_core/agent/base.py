"""
Base agent abstraction for chess players.

This module defines the abstract interface for chess agents,
allowing different strategies to be used interchangeably.
"""

from abc import ABC, abstractmethod
from typing import Optional
from ..game.game_state import GameState
from ..game.types import Color, ChessMove


class ChessAgent(ABC):
    """
    Abstract base class for chess agents.
    
    Design Principles:
    - Agent = Decision strategy, not equal to search algorithm
    - No UI/API dependencies
    - Can internally use SearchEngine
    - Stateful: maintains color assignment
    
    Agents are responsible for choosing moves based on the current
    game state. They may use search engines, neural networks, or
    any other decision-making mechanism internally.
    """
    
    name: str = "BaseAgent"
    
    def __init__(self):
        """Initialize the agent."""
        self._color: Optional[Color] = None
    
    def reset(self, color: Color) -> None:
        """
        Reset the agent for a new game.
        
        Args:
            color: The color this agent will play as
        """
        self._color = color
    
    @abstractmethod
    def act(self, state: GameState) -> ChessMove:
        """
        Choose a move given the current game state.
        
        Args:
            state: The current GameState
        
        Returns:
            The chosen ChessMove
        """
        pass
    
    @property
    def color(self) -> Optional[Color]:
        """Get the agent's assigned color."""
        return self._color
    
    def __repr__(self) -> str:
        """String representation of the agent."""
        return f"{self.__class__.__name__}(color={self._color})"
