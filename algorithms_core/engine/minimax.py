"""
Minimax search algorithm with Alpha-Beta pruning.

This module implements the classic Minimax algorithm with Alpha-Beta pruning
for chess position search, using python-chess for game logic.
"""

import time
import math
from typing import Optional, Callable
import chess
from .base import SearchEngine
from ..game.chess_game import ChessGame
from ..game.types import ChessMove
from ..eval.base import Evaluator


class MinimaxEngine(SearchEngine):
    """
    Minimax search engine with Alpha-Beta pruning.
    
    Design Principles:
    - Configurable search depth
    - Pluggable evaluation function
    - Time limit support
    - Node counting for analysis
    
    The algorithm explores the game tree to find the best move
    using minimax with alpha-beta pruning for efficiency.
    """
    
    def __init__(
        self, 
        evaluator: Evaluator,
        default_depth: int = 4,
        use_quiescence: bool = False
    ):
        """
        Initialize the Minimax engine.
        
        Args:
            evaluator: The evaluation function to use
            default_depth: Default search depth if not specified
            use_quiescence: Whether to use quiescence search for tactical positions
        """
        super().__init__()
        self.evaluator = evaluator
        self.default_depth = default_depth
        self.use_quiescence = use_quiescence
        self._start_time = 0.0
        self._time_limit = 0.0
    
    def search(
        self,
        game: ChessGame,
        time_limit: Optional[float] = None,
        depth_limit: Optional[int] = None
    ) -> ChessMove:
        """
        Search for the best move using Minimax with Alpha-Beta pruning.
        
        Args:
            game: The ChessGame instance (will be cloned, not modified)
            time_limit: Maximum search time in seconds (None = no limit)
            depth_limit: Maximum search depth (None = use default)
        
        Returns:
            The best ChessMove found
        """
        self._reset_stats()
        self._start_time = time.time()
        self._time_limit = time_limit if time_limit is not None else float('inf')
        
        depth = depth_limit if depth_limit is not None else self.default_depth
        
        # Get legal moves
        legal_moves = game.legal_moves()
        
        if not legal_moves:
            raise ValueError("No legal moves available")
        
        # If only one move, return it immediately
        if len(legal_moves) == 1:
            return legal_moves[0]
        
        best_move = None
        best_score = -math.inf
        alpha = -math.inf
        beta = math.inf
        
        # Iterate through all legal moves
        for move in legal_moves:
            # Clone game and make move
            cloned_game = game.clone()
            cloned_game.step(move)
            
            # Get score from this move (minimax with alpha-beta)
            score = -self._minimax(
                cloned_game, 
                depth - 1, 
                -beta, 
                -alpha, 
                maximizing_player=False
            )
            
            # Update best move if this is better
            if score > best_score:
                best_score = score
                best_move = move
            
            # Update alpha
            alpha = max(alpha, score)
            
            # Check time limit
            if time.time() - self._start_time > self._time_limit:
                break
        
        return best_move
    
    def _minimax(
        self,
        game: ChessGame,
        depth: int,
        alpha: float,
        beta: float,
        maximizing_player: bool
    ) -> float:
        """
        Recursive minimax with alpha-beta pruning.
        
        Args:
            game: The game state to evaluate
            depth: Remaining search depth
            alpha: Alpha value for pruning
            beta: Beta value for pruning
            maximizing_player: Whether this is a maximizing node
        
        Returns:
            The evaluated score
        """
        self._increment_nodes()
        
        # Check time limit
        if time.time() - self._start_time > self._time_limit:
            return 0.0
        
        # Terminal state or depth reached
        if depth == 0 or game.is_game_over():
            if self.use_quiescence and depth == 0 and not game.is_game_over():
                return self._quiescence_search(game, alpha, beta, 4)
            return self.evaluator.evaluate(game.state)
        
        legal_moves = game.legal_moves()
        
        if not legal_moves:
            # No legal moves - checkmate or stalemate
            if game.is_checkmate():
                # Checkmate - large negative score (bad for current player)
                return -20000 + (self.default_depth - depth)
            else:
                # Stalemate - draw
                return 0.0
        
        if maximizing_player:
            max_eval = -math.inf
            for move in legal_moves:
                cloned_game = game.clone()
                cloned_game.step(move)
                eval_score = self._minimax(cloned_game, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  # Beta cutoff
            return max_eval
        else:
            min_eval = math.inf
            for move in legal_moves:
                cloned_game = game.clone()
                cloned_game.step(move)
                eval_score = self._minimax(cloned_game, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  # Alpha cutoff
            return min_eval
    
    def _quiescence_search(
        self,
        game: ChessGame,
        alpha: float,
        beta: float,
        depth: int
    ) -> float:
        """
        Quiescence search to extend search in tactical positions.
        
        Only searches captures and checks to reach a "quiet" position.
        
        Args:
            game: The game state to evaluate
            alpha: Alpha value for pruning
            beta: Beta value for pruning
            depth: Remaining search depth
        
        Returns:
            The evaluated score
        """
        self._increment_nodes()
        
        # Stand-pat score
        stand_pat = self.evaluator.evaluate(game.state)
        
        if stand_pat >= beta:
            return beta
        if stand_pat > alpha:
            alpha = stand_pat
        
        if depth == 0:
            return stand_pat
        
        # Only search captures and checks
        legal_moves = game.legal_moves()
        tactical_moves = [
            move for move in legal_moves
            if game.board.is_capture(chess.Move.from_uci(str(move)))
            or game.board.gives_check(chess.Move.from_uci(str(move)))
        ]
        
        if not tactical_moves:
            return stand_pat
        
        for move in tactical_moves:
            cloned_game = game.clone()
            cloned_game.step(move)
            score = -self._quiescence_search(cloned_game, -beta, -alpha, depth - 1)
            
            if score >= beta:
                return beta
            if score > alpha:
                alpha = score
        
        return alpha


class IterativeDeepeningMinimax(MinimaxEngine):
    """
    Iterative deepening variant of Minimax.
    
    Searches progressively deeper until time limit is reached,
    returning the best move found at the deepest completed depth.
    """
    
    def search(
        self,
        game: ChessGame,
        time_limit: Optional[float] = None,
        depth_limit: Optional[int] = None
    ) -> ChessMove:
        """
        Search with iterative deepening.
        
        Args:
            game: The ChessGame instance
            time_limit: Maximum search time in seconds
            depth_limit: Maximum search depth
        
        Returns:
            The best ChessMove found
        """
        self._reset_stats()
        self._start_time = time.time()
        self._time_limit = time_limit if time_limit is not None else float('inf')
        
        max_depth = depth_limit if depth_limit is not None else 10
        best_move = None
        
        legal_moves = game.legal_moves()
        
        if not legal_moves:
            raise ValueError("No legal moves available")
        
        if len(legal_moves) == 1:
            return legal_moves[0]
        
        # Iteratively deepen
        for depth in range(1, max_depth + 1):
            # Check time limit before starting new depth
            if time.time() - self._start_time > self._time_limit:
                break
            
            try:
                move = self._search_at_depth(game, depth)
                if move is not None:
                    best_move = move
            except TimeoutError:
                break
        
        return best_move if best_move else legal_moves[0]
    
    def _search_at_depth(self, game: ChessGame, depth: int) -> ChessMove:
        """Search at a specific depth."""
        # Use parent class search method with fixed depth
        return super().search(game, self._time_limit - (time.time() - self._start_time), depth)
