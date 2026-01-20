"""
Game module for chess environment abstraction.

This module provides the core game logic and state management
for the chess research platform.
"""

from .chess_game import ChessGame
from .game_state import GameState
from .types import Color, ChessMove, GameResult, PieceType

__all__ = [
    "ChessGame",
    "GameState",
    "Color",
    "ChessMove",
    "GameResult",
    "PieceType",
]
