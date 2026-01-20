"""
Material-based position evaluator for chess.

This module provides a classic material evaluation function,
using python-chess library for piece counting and position analysis.
"""

from typing import Dict
import chess
from .base import Evaluator
from ..game.game_state import GameState


class MaterialEvaluator(Evaluator):
    """
    Material-based position evaluator.
    
    Uses classic piece-square values for evaluation:
    - Pawn: 100
    - Knight: 320
    - Bishop: 330
    - Rook: 500
    - Queen: 900
    - King: 20000 (for checkmate detection)
    
    The score is from the perspective of the player to move.
    Positive means the current player has material advantage.
    """
    
    # Standard piece values (in centipawns)
    PIECE_VALUES: Dict[chess.PieceType, int] = {
        chess.PAWN: 100,
        chess.KNIGHT: 320,
        chess.BISHOP: 330,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 20000,  # Large value to prioritize king safety
    }
    
    def __init__(self, piece_values: Dict[chess.PieceType, int] = None):
        """
        Initialize the material evaluator.
        
        Args:
            piece_values: Optional custom piece values. Defaults to standard values.
        """
        if piece_values is not None:
            self.piece_values = piece_values
        else:
            self.piece_values = self.PIECE_VALUES.copy()
    
    def evaluate(self, state: GameState) -> float:
        """
        Evaluate a game state based on material difference.
        
        Args:
            state: The GameState to evaluate
        
        Returns:
            Float score from perspective of the player to move.
            Positive = current player has material advantage.
            Negative = opponent has material advantage.
        """
        board = state.board
        
        white_score = 0.0
        black_score = 0.0
        
        # Count material for both sides using python-chess
        for piece_type in chess.PIECE_TYPES:
            white_count = len(board.pieces(piece_type, chess.WHITE))
            black_count = len(board.pieces(piece_type, chess.BLACK))
            
            value = self.piece_values[piece_type]
            white_score += white_count * value
            black_score += black_count * value
        
        # Calculate score from perspective of player to move
        material_diff = white_score - black_score
        
        # If it's white's turn, positive diff is good
        # If it's black's turn, negative diff is good
        if board.turn:  # White to move
            return material_diff
        else:  # Black to move
            return -material_diff
    
    def count_material(self, state: GameState) -> Dict[str, int]:
        """
        Count material pieces for both sides.
        
        Args:
            state: The GameState to analyze
        
        Returns:
            Dictionary with material counts for each piece type
        """
        board = state.board
        material = {}
        
        for piece_type in chess.PIECE_TYPES:
            white_count = len(board.pieces(piece_type, chess.WHITE))
            black_count = len(board.pieces(piece_type, chess.BLACK))
            piece_name = chess.piece_name(piece_type)
            material[f"white_{piece_name}"] = white_count
            material[f"black_{piece_name}"] = black_count
        
        return material
    
    def get_material_score(self, state: GameState) -> Dict[str, float]:
        """
        Get detailed material scores for both sides.
        
        Args:
            state: The GameState to analyze
        
        Returns:
            Dictionary with material scores for white and black
        """
        board = state.board
        
        white_score = 0.0
        black_score = 0.0
        
        for piece_type in chess.PIECE_TYPES:
            white_count = len(board.pieces(piece_type, chess.WHITE))
            black_count = len(board.pieces(piece_type, chess.BLACK))
            
            value = self.piece_values[piece_type]
            white_score += white_count * value
            black_score += black_count * value
        
        return {
            "white_score": white_score,
            "black_score": black_score,
            "difference": white_score - black_score
        }


class PythonChessEvaluator(Evaluator):
    """
    Evaluator using python-chess built-in evaluation function.
    
    This leverages python-chess's built-in evaluation which considers
    material, piece activity, and other positional factors.
    """
    
    def evaluate(self, state: GameState) -> float:
        """
        Evaluate a game state using python-chess built-in evaluation.
        
        Args:
            state: The GameState to evaluate
        
        Returns:
            Float score from perspective of the player to move.
        """
        board = state.board
        
        # Use python-chess built-in evaluation
        # Note: python-chess evaluation returns score from white's perspective
        score = board.eval()
        
        # Adjust for perspective of player to move
        if board.turn:  # White to move
            return score.relative.score(mate_score=20000)
        else:  # Black to move
            return -score.relative.score(mate_score=20000)
