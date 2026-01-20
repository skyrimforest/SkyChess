"""
Game state representation for chess research.

This module provides the core GameState dataclass that serves as the
single source of truth for chess positions throughout the algorithm layer.
Uses python-chess library for efficient state management.
"""

from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING
import chess
from .types import Color, ChessMove, GameResult

if TYPE_CHECKING:
    pass


@dataclass
class GameState:
    """
    Core data structure representing a chess game state.
    
    Design Principles:
    - FEN string is the single source of truth for board position
    - Uses python-chess Board internally for efficient operations
    - Fully serializable for dataset generation and logging
    - Immutable-like semantics (create new states instead of mutating)
    
    Attributes:
        board: python-chess Board object (internal representation)
        fen: Forsyth-Edwards Notation string representing the board position
        current_player: Color of the player whose turn it is
        move_history: List of moves leading to this state
        is_terminal: Whether the game has ended
        result: Game result if terminal, None otherwise
    """
    board: chess.Board
    fen: str
    current_player: Color
    move_history: list[ChessMove] = field(default_factory=list)
    is_terminal: bool = False
    result: Optional[GameResult] = None
    
    def __post_init__(self):
        """Ensure FEN is synchronized with board."""
        if self.fen != self.board.fen():
            self.fen = self.board.fen()
    
    @classmethod
    def from_fen(cls, fen: str) -> "GameState":
        """
        Create a GameState from a FEN string.
        
        Args:
            fen: FEN string to parse
        
        Returns:
            GameState instance
        """
        board = chess.Board(fen)
        return cls._from_board(board)
    
    @classmethod
    def _from_board(cls, board: chess.Board) -> "GameState":
        """
        Create a GameState from a python-chess Board object.
        
        Args:
            board: python-chess Board object
        
        Returns:
            GameState instance
        """
        result = None
        is_terminal = False
        
        if board.is_game_over():
            is_terminal = True
            if board.is_checkmate():
                result = GameResult.BLACK_WIN if board.turn else GameResult.WHITE_WIN
            else:
                result = GameResult.DRAW
        
        move_history = [
            ChessMove.from_uci(move.uci()) 
            for move in board.move_stack
        ]
        
        return cls(
            board=board.copy(),
            fen=board.fen(),
            current_player=Color.WHITE if board.turn else Color.BLACK,
            move_history=move_history,
            is_terminal=is_terminal,
            result=result
        )
    
    def copy(self) -> "GameState":
        """
        Create a deep copy of this state.
        
        Returns:
            A new GameState with identical values
        """
        return GameState(
            board=self.board.copy(),
            fen=self.fen,
            current_player=self.current_player,
            move_history=list(self.move_history),
            is_terminal=self.is_terminal,
            result=self.result
        )
    
    def with_move(self, move: ChessMove) -> "GameState":
        """
        Create a new state resulting from applying a move.
        
        Args:
            move: The move to apply
        
        Returns:
            New GameState instance after the move
        """
        new_board = self.board.copy()
        chess_move = chess.Move.from_uci(str(move))
        
        if chess_move not in new_board.legal_moves:
            raise ValueError(f"Illegal move: {move}")
        
        new_board.push(chess_move)
        return self._from_board(new_board)
    
    def legal_moves(self) -> list[ChessMove]:
        """
        Get all legal moves from this state.
        
        Returns:
            List of legal ChessMove objects
        """
        return [ChessMove.from_uci(m.uci()) for m in self.board.legal_moves]
    
    def to_dict(self) -> dict:
        """
        Convert state to dictionary for serialization.
        
        Returns:
            Dictionary representation of the state
        """
        return {
            "fen": self.fen,
            "current_player": self.current_player.value,
            "move_history": [str(move) for move in self.move_history],
            "is_terminal": self.is_terminal,
            "result": self.result.value if self.result else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "GameState":
        """
        Create state from dictionary.
        
        Args:
            data: Dictionary representation of the state
        
        Returns:
            GameState instance
        """
        return cls.from_fen(data["fen"])
    
    def __str__(self) -> str:
        """Return FEN string representation."""
        return self.fen
