"""
Chess game environment abstraction.

This module provides the ChessGame class that encapsulates chess rules
and state transitions, serving as the environment for agents and engines.
Uses python-chess library for all game logic.
"""

from typing import List, Optional
import chess
from .game_state import GameState
from .types import Color, ChessMove, GameResult


class ChessGame:
    """
    Environment abstraction for chess, following OpenAI Gym / PettingZoo patterns.
    
    Design Principles:
    - Pure game logic, no Agent or Engine dependencies
    - Clone method for search tree expansion
    - FEN-based state management for consistency
    - No global state for reproducibility
    
    Uses python-chess library internally for all chess rules and validation.
    """
    
    def __init__(self, fen: Optional[str] = None):
        """
        Initialize a chess game.
        
        Args:
            fen: Optional FEN string to start from. Defaults to starting position.
        """
        self._board = chess.Board(fen) if fen else chess.Board()
        self._initial_fen = self._board.fen()
    
    @property
    def state(self) -> GameState:
        """
        Get the current game state.
        
        Returns:
            GameState representing the current position
        """
        return GameState._from_board(self._board)
    
    def reset(self) -> GameState:
        """
        Reset the game to the initial position.
        
        Returns:
            Initial GameState
        """
        self._board = chess.Board(self._initial_fen)
        return self.state
    
    def step(self, move: ChessMove) -> GameState:
        """
        Apply a move and return the new state.
        
        Args:
            move: The move to apply
        
        Returns:
            New GameState after the move
        
        Raises:
            ValueError: If the move is illegal
        """
        # Convert to python-chess move
        chess_move = chess.Move.from_uci(str(move))
        
        if chess_move not in self._board.legal_moves:
            raise ValueError(f"Illegal move: {move}")
        
        # Apply the move
        self._board.push(chess_move)
        
        return self.state
    
    def legal_moves(self) -> List[ChessMove]:
        """
        Get all legal moves from the current position.
        
        Returns:
            List of legal ChessMove objects
        """
        return [ChessMove.from_uci(m.uci()) for m in self._board.legal_moves]
    
    def clone(self) -> "ChessGame":
        """
        Create a deep copy of the game.
        
        This is critical for search algorithms that need to explore
        different branches without modifying the original game state.
        
        Returns:
            New ChessGame instance with identical state
        """
        cloned = ChessGame.__new__(ChessGame)
        cloned._board = self._board.copy()
        cloned._initial_fen = self._initial_fen
        return cloned
    
    def is_check(self) -> bool:
        """Check if the current player is in check."""
        return self._board.is_check()
    
    def is_checkmate(self) -> bool:
        """Check if the current position is checkmate."""
        return self._board.is_checkmate()
    
    def is_stalemate(self) -> bool:
        """Check if the current position is stalemate."""
        return self._board.is_stalemate()
    
    def is_insufficient_material(self) -> bool:
        """Check if the position has insufficient material to checkmate."""
        return self._board.is_insufficient_material()
    
    def is_fifty_moves(self) -> bool:
        """Check if the 50-move rule applies."""
        return self._board.is_fifty_moves()
    
    def is_threefold_repetition(self) -> bool:
        """Check if threefold repetition has occurred."""
        return self._board.is_threefold_repetition()
    
    def is_game_over(self) -> bool:
        """Check if the game is over."""
        return self._board.is_game_over()
    
    def turn(self) -> Color:
        """Get the current player's color."""
        return Color.WHITE if self._board.turn else Color.BLACK
    
    def to_fen(self) -> str:
        """Get the FEN string of the current position."""
        return self._board.fen()
    
    def from_fen(self, fen: str) -> None:
        """
        Load a position from FEN string.
        
        Args:
            fen: FEN string to load
        """
        self._board = chess.Board(fen)
    
    @property
    def board(self) -> chess.Board:
        """
        Get the internal python-chess Board object.
        
        Returns:
            python-chess Board instance
        """
        return self._board
    
    def __repr__(self) -> str:
        """String representation of the game."""
        return f"ChessGame(fen='{self.to_fen()}')"
