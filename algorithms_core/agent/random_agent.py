"""
Random move agent for chess.

This module provides a simple agent that makes random legal moves,
useful for testing and baseline comparisons.
"""

import math
import random
from typing import Optional
from .base import ChessAgent
from ..game.game_state import GameState
from ..game.types import Color, ChessMove


class RandomAgent(ChessAgent):
    """
    Agent that selects random legal moves.
    
    This is the simplest possible agent, useful for:
    - Testing and debugging
    - Baseline comparisons
    - Self-play training (as opponent)
    """
    
    name = "RandomAgent"
    
    def __init__(self, seed: Optional[int] = None):
        """
        Initialize the random agent.
        
        Args:
            seed: Random seed for reproducibility
        """
        super().__init__()
        if seed is not None:
            random.seed(seed)
    
    def act(self, state: GameState) -> ChessMove:
        """
        Choose a random legal move.
        
        Args:
            state: The current GameState
        
        Returns:
            A randomly chosen legal ChessMove
        """
        legal_moves = state.legal_moves()
        
        if not legal_moves:
            raise ValueError("No legal moves available")
        
        return random.choice(legal_moves)


class WeightedRandomAgent(ChessAgent):
    """
    Agent that selects moves with weighted random choice.
    
    Can use an evaluator to weight moves by their estimated quality.
    """
    
    name = "WeightedRandomAgent"
    
    def __init__(self, evaluator=None, temperature: float = 1.0, seed: Optional[int] = None):
        """
        Initialize the weighted random agent.
        
        Args:
            evaluator: Optional evaluator to weight moves
            temperature: Controls randomness (higher = more random)
            seed: Random seed for reproducibility
        """
        super().__init__()
        self.evaluator = evaluator
        self.temperature = temperature
        if seed is not None:
            random.seed(seed)
    
    def act(self, state: GameState) -> ChessMove:
        """
        Choose a move with weighted random selection.
        
        Args:
            state: The current GameState
        
        Returns:
            A ChessMove chosen with weighted probability
        """
        legal_moves = state.legal_moves()
        
        if not legal_moves:
            raise ValueError("No legal moves available")
        
        if self.evaluator is None:
            return random.choice(legal_moves)
        
        # Evaluate each move
        import chess
        board = state.board
        move_scores = []
        
        for move in legal_moves:
            cloned_board = board.copy()
            cloned_board.push(chess.Move.from_uci(str(move)))
            # Create temporary state for evaluation
            temp_state = GameState._from_board(cloned_board)
            score = self.evaluator.evaluate(temp_state)
            move_scores.append(score)
        
        # Apply temperature and convert to probabilities
        scores = [s / self.temperature for s in move_scores]
        max_score = max(scores)
        exp_scores = [math.exp(s - max_score) for s in scores]
        total = sum(exp_scores)
        probabilities = [e / total for e in exp_scores]
        
        # Weighted random choice
        return random.choices(legal_moves, weights=probabilities, k=1)[0]


class FirstMoveAgent(ChessAgent):
    """
    Agent that always plays the first legal move.
    
    Useful for deterministic testing and debugging.
    """
    
    name = "FirstMoveAgent"
    
    def act(self, state: GameState) -> ChessMove:
        """
        Choose the first legal move.
        
        Args:
            state: The current GameState
        
        Returns:
            The first legal ChessMove
        """
        legal_moves = state.legal_moves()
        
        if not legal_moves:
            raise ValueError("No legal moves available")
        
        return legal_moves[0]
