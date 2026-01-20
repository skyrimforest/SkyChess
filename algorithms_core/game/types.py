"""
Core type definitions for the chess algorithm layer.

This module defines fundamental types used throughout the chess research platform,
ensuring type safety and clear interfaces between components.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional


class Color(Enum):
    """Chess piece color enumeration."""
    WHITE = "white"
    BLACK = "black"

    def opposite(self) -> "Color":
        """Return the opposite color."""
        return Color.BLACK if self == Color.WHITE else Color.WHITE


class PieceType(Enum):
    """Chess piece type enumeration."""
    PAWN = "pawn"
    KNIGHT = "knight"
    BISHOP = "bishop"
    ROOK = "rook"
    QUEEN = "queen"
    KING = "king"


class GameResult(Enum):
    """Game termination result enumeration."""
    WHITE_WIN = "white_win"
    BLACK_WIN = "black_win"
    DRAW = "draw"
    IN_PROGRESS = "in_progress"


@dataclass(frozen=True)
class ChessMove:
    """
    Immutable representation of a chess move.
    
    Uses algebraic notation internally but provides structured access.
    Frozen to ensure immutability - important for search algorithms.
    """
    from_square: str  # e.g., "e2"
    to_square: str    # e.g., "e4"
    promotion: Optional[PieceType] = None
    
    def __str__(self) -> str:
        """Return move in UCI format (e.g., 'e2e4' or 'e7e8q')."""
        if self.promotion:
            return f"{self.from_square}{self.to_square}{self.promotion.value[0].lower()}"
        return f"{self.from_square}{self.to_square}"
    
    @classmethod
    def from_uci(cls, uci: str) -> "ChessMove":
        """
        Create a ChessMove from UCI notation.
        
        Args:
            uci: UCI move string (e.g., 'e2e4', 'e7e8q')
        
        Returns:
            ChessMove instance
        """
        if len(uci) == 4:
            return cls(from_square=uci[:2], to_square=uci[2:4])
        elif len(uci) == 5:
            promotion_char = uci[4].lower()
            promotion_map = {
                'q': PieceType.QUEEN,
                'r': PieceType.ROOK,
                'b': PieceType.BISHOP,
                'n': PieceType.KNIGHT
            }
            return cls(
                from_square=uci[:2],
                to_square=uci[2:4],
                promotion=promotion_map.get(promotion_char)
            )
        raise ValueError(f"Invalid UCI move: {uci}")
