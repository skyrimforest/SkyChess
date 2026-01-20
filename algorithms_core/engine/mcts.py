"""
Monte Carlo Tree Search (MCTS) algorithm for chess.

This module implements MCTS with UCT selection for chess position search,
using python-chess for game logic and simulation.
"""

import time
import math
from typing import Optional, List, Dict
import chess
from .base import SearchEngine
from ..game.chess_game import ChessGame
from ..game.types import ChessMove
from ..eval.base import Evaluator


class MCTSNode:
    """
    Node in the MCTS search tree.
    
    Attributes:
        move: The move that led to this node (None for root)
        parent: Parent node (None for root)
        children: Dictionary mapping moves to child nodes
        visits: Number of times this node has been visited
        value: Cumulative value from this node's perspective
        untried_moves: List of moves not yet explored
        is_terminal: Whether this node represents a terminal state
    """
    
    def __init__(
        self, 
        move: Optional[ChessMove] = None, 
        parent: Optional["MCTSNode"] = None,
        game: Optional[ChessGame] = None
    ):
        """
        Initialize an MCTS node.
        
        Args:
            move: The move that led to this node
            parent: Parent node
            game: The game state at this node
        """
        self.move = move
        self.parent = parent
        self.children: Dict[ChessMove, MCTSNode] = {}
        self.visits = 0
        self.value = 0.0
        self.is_terminal = False
        
        if game is not None:
            self.untried_moves: List[ChessMove] = game.legal_moves()
            if not self.untried_moves or game.is_game_over():
                self.is_terminal = True
        else:
            self.untried_moves = []
    
    def is_fully_expanded(self) -> bool:
        """Check if all children have been created."""
        return len(self.untried_moves) == 0
    
    def is_leaf(self) -> bool:
        """Check if this is a leaf node (no children)."""
        return len(self.children) == 0
    
    def best_child(self, exploration_weight: float = 1.414) -> "MCTSNode":
        """
        Select the best child using UCT (Upper Confidence Bound for Trees).
        
        Args:
            exploration_weight: The exploration constant (C_puct)
        
        Returns:
            The child node with highest UCT score
        """
        best_score = -float('inf')
        best_child = None
        
        for child in self.children.values():
            if child.visits == 0:
                uct_score = float('inf')
            else:
                exploitation = child.value / child.visits
                exploration = exploration_weight * math.sqrt(
                    math.log(self.visits) / child.visits
                )
                uct_score = exploitation + exploration
            
            if uct_score > best_score:
                best_score = uct_score
                best_child = child
        
        return best_child
    
    def update(self, result: float) -> None:
        """
        Update node statistics with simulation result.
        
        Args:
            result: The result of the simulation from this node's perspective
        """
        self.visits += 1
        self.value += result


class MCTSEngine(SearchEngine):
    """
    Monte Carlo Tree Search engine with UCT selection.
    
    Design Principles:
    - UCT-based selection for balancing exploration/exploitation
    - Pluggable rollout policy (random or evaluation-based)
    - Time limit support
    - Node counting for analysis
    
    The algorithm builds a search tree by iteratively:
    1. Selection: Traverse tree using UCT
    2. Expansion: Add a new node
    3. Simulation: Roll out from new node
    4. Backpropagation: Update statistics up the tree
    """
    
    def __init__(
        self,
        evaluator: Optional[Evaluator] = None,
        exploration_weight: float = 1.414,
        rollout_depth: int = 10,
        use_evaluation_rollout: bool = False
    ):
        """
        Initialize the MCTS engine.
        
        Args:
            evaluator: Optional evaluator for rollout policy
            exploration_weight: UCT exploration constant (C_puct)
            rollout_depth: Maximum depth for rollouts
            use_evaluation_rollout: Use evaluation instead of random rollouts
        """
        super().__init__()
        self.evaluator = evaluator
        self.exploration_weight = exploration_weight
        self.rollout_depth = rollout_depth
        self.use_evaluation_rollout = use_evaluation_rollout
        self._start_time = 0.0
        self._time_limit = 0.0
    
    def search(
        self,
        game: ChessGame,
        time_limit: Optional[float] = None,
        depth_limit: Optional[int] = None
    ) -> ChessMove:
        """
        Search for the best move using MCTS.
        
        Args:
            game: The ChessGame instance (will be cloned, not modified)
            time_limit: Maximum search time in seconds (None = no limit)
            depth_limit: Maximum simulation depth (None = use default)
        
        Returns:
            The best ChessMove found
        """
        self._reset_stats()
        self._start_time = time.time()
        self._time_limit = time_limit if time_limit is not None else 5.0
        
        # Create root node
        root = MCTSNode(game=game.clone())
        
        # Check for terminal position
        if root.is_terminal:
            raise ValueError("Game is already over")
        
        # Check for only one legal move
        if len(root.untried_moves) == 1:
            return root.untried_moves[0]
        
        # Run MCTS iterations
        iterations = 0
        while time.time() - self._start_time < self._time_limit:
            self._mcts_iteration(root, game.clone())
            iterations += 1
        
        # Return the most visited child's move
        best_child = max(root.children.values(), key=lambda c: c.visits)
        return best_child.move
    
    def _mcts_iteration(self, root: MCTSNode, game: ChessGame) -> None:
        """
        Run a single MCTS iteration.
        
        Args:
            root: The root node of the tree
            game: A clone of the original game
        """
        # Selection
        node = root
        current_game = game
        
        while not node.is_leaf() and not node.is_terminal:
            node = node.best_child(self.exploration_weight)
            current_game.step(node.move)
        
        # Expansion
        if not node.is_terminal and node.untried_moves:
            move = node.untried_moves.pop()
            current_game.step(move)
            new_node = MCTSNode(move=move, parent=node, game=current_game.clone())
            node.children[move] = new_node
            node = new_node
        
        # Simulation (Rollout)
        result = self._rollout(current_game)
        
        # Backpropagation
        self._backpropagate(node, result)
    
    def _rollout(self, game: ChessGame) -> float:
        """
        Simulate a game from the current position.
        
        Args:
            game: The game state to simulate from
        
        Returns:
            The result from the perspective of the player to move at start
        """
        if self.use_evaluation_rollout and self.evaluator is not None:
            return self._evaluation_rollout(game)
        else:
            return self._random_rollout(game)
    
    def _random_rollout(self, game: ChessGame) -> float:
        """Perform a random rollout."""
        import random
        rollout_game = game.clone()
        depth = 0
        max_depth = self.rollout_depth
        
        while not rollout_game.is_game_over() and depth < max_depth:
            legal_moves = rollout_game.legal_moves()
            if not legal_moves:
                break
            move = random.choice(legal_moves)
            rollout_game.step(move)
            depth += 1
        
        # Determine result
        if rollout_game.is_game_over():
            state = rollout_game.state
            if state.result is not None:
                if state.result.value == "white_win":
                    return 1.0 if rollout_game.turn() else -1.0
                elif state.result.value == "black_win":
                    return -1.0 if rollout_game.turn() else 1.0
                else:
                    return 0.0  # Draw
        
        # If reached max depth, use evaluation if available
        if self.evaluator is not None:
            eval_score = self.evaluator.evaluate(rollout_game.state)
            # Normalize to [-1, 1] range
            return max(-1.0, min(1.0, eval_score / 1000.0))
        
        return 0.0
    
    def _evaluation_rollout(self, game: ChessGame) -> float:
        """Perform an evaluation-based rollout."""
        rollout_game = game.clone()
        depth = 0
        max_depth = self.rollout_depth
        
        while not rollout_game.is_game_over() and depth < max_depth:
            legal_moves = rollout_game.legal_moves()
            if not legal_moves:
                break
            
            # Choose move based on evaluation
            best_move = None
            best_score = -float('inf')
            
            for move in legal_moves:
                cloned = rollout_game.clone()
                cloned.step(move)
                score = self.evaluator.evaluate(cloned.state)
                if score > best_score:
                    best_score = score
                    best_move = move
            
            rollout_game.step(best_move)
            depth += 1
        
        # Determine result
        if rollout_game.is_game_over():
            state = rollout_game.state
            if state.result is not None:
                if state.result.value == "white_win":
                    return 1.0 if rollout_game.turn() else -1.0
                elif state.result.value == "black_win":
                    return -1.0 if rollout_game.turn() else 1.0
                else:
                    return 0.0  # Draw
        
        # Use final evaluation
        eval_score = self.evaluator.evaluate(rollout_game.state)
        return max(-1.0, min(1.0, eval_score / 1000.0))
    
    def _backpropagate(self, node: MCTSNode, result: float) -> None:
        """
        Backpropagate the result up the tree.
        
        Args:
            node: The node to start backpropagation from
            result: The result to propagate
        """
        while node is not None:
            node.update(result)
            result = -result  # Flip perspective for parent
            node = node.parent
