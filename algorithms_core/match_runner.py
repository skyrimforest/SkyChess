"""
Match runner for multi-agent chess games.

This module provides functionality for running matches between agents,
supporting self-play, algorithm comparison, and tournament play.
"""

from typing import Optional, Callable, List
from .agent.base import ChessAgent
from .game.chess_game import ChessGame
from .game.types import Color, GameResult
from .record.game_record import GameRecord, GameRecordBatch


class MatchRunner:
    """
    Runner for chess matches between two agents.
    
    Supports:
    - Single games between two agents
    - Self-play (same agent vs itself)
    - Algorithm comparison
    - Tournament play
    - Move-by-move callbacks
    """
    
    def __init__(self, verbose: bool = False):
        """
        Initialize the match runner.
        
        Args:
            verbose: Whether to print move information
        """
        self.verbose = verbose
    
    def run(
        self,
        white: ChessAgent,
        black: ChessAgent,
        initial_fen: Optional[str] = None,
        max_moves: Optional[int] = None,
        move_callback: Optional[Callable[[int, Color, str], None]] = None
    ) -> GameRecord:
        """
        Run a single game between two agents.
        
        Args:
            white: Agent playing white
            black: Agent playing black
            initial_fen: Optional starting FEN (None = standard position)
            max_moves: Maximum number of moves (None = no limit)
            move_callback: Optional callback called after each move
                           (move_number, color, move_string)
        
        Returns:
            GameRecord with the complete game
        """
        # Reset agents
        white.reset(Color.WHITE)
        black.reset(Color.BLACK)
        
        # Initialize game
        game = ChessGame(initial_fen)
        
        # Create record
        record = GameRecord(
            white_agent=white.name,
            black_agent=black.name,
            initial_fen=initial_fen
        )
        
        move_count = 0
        
        # Main game loop
        while not game.is_game_over():
            # Check max moves
            if max_moves is not None and move_count >= max_moves:
                record.set_result(GameResult.DRAW, "max_moves")
                break
            
            # Get current agent
            current_agent = white if game.turn() == Color.WHITE else black
            
            # Get move
            move = current_agent.act(game.state)
            
            # Record move
            record.add_move(move)
            move_count += 1
            
            # Apply move
            game.step(move)
            
            # Callback
            if move_callback:
                move_callback(move_count, game.turn().opposite(), str(move))
            
            # Verbose output
            if self.verbose:
                print(f"{move_count}. {move} ({current_agent.name})")
        
        # Set result if game ended
        if not record.result:
            state = game.state
            if state.result:
                reason = "checkmate" if game.is_checkmate() else "draw"
                record.set_result(state.result, reason)
            else:
                record.set_result(GameResult.DRAW, "unknown")
        
        return record
    
    def run_match(
        self,
        white: ChessAgent,
        black: ChessAgent,
        games: int = 2,
        **kwargs
    ) -> GameRecordBatch:
        """
        Run a match with multiple games (alternating colors).
        
        Args:
            white: First agent
            black: Second agent
            games: Number of games to play (must be even for fair comparison)
            **kwargs: Additional arguments passed to run()
        
        Returns:
            GameRecordBatch with all games
        """
        batch = GameRecordBatch()
        
        for i in range(games):
            # Alternate colors
            if i % 2 == 0:
                record = self.run(white, black, **kwargs)
            else:
                record = self.run(black, white, **kwargs)
            
            batch.add(record)
        
        return batch
    
    def run_tournament(
        self,
        agents: List[ChessAgent],
        rounds: int = 1,
        **kwargs
    ) -> GameRecordBatch:
        """
        Run a round-robin tournament between multiple agents.
        
        Args:
            agents: List of agents to compete
            rounds: Number of rounds (each pair plays rounds games)
            **kwargs: Additional arguments passed to run()
        
        Returns:
            GameRecordBatch with all games
        """
        batch = GameRecordBatch()
        
        # Round-robin: each agent plays against each other
        for i in range(len(agents)):
            for j in range(i + 1, len(agents)):
                agent1 = agents[i]
                agent2 = agents[j]
                
                # Play multiple rounds
                for r in range(rounds):
                    # Alternate colors
                    if r % 2 == 0:
                        record = self.run(agent1, agent2, **kwargs)
                    else:
                        record = self.run(agent2, agent1, **kwargs)
                    
                    batch.add(record)
        
        return batch
    
    def print_results(self, batch: GameRecordBatch) -> None:
        """
        Print tournament results in a table format.
        
        Args:
            batch: GameRecordBatch with tournament results
        """
        # Collect all agent names
        agents = set()
        for record in batch.records:
            agents.add(record.white_agent)
            agents.add(record.black_agent)
        agents = sorted(agents)
        
        if not agents:
            print("No games played.")
            return
        
        # Print header
        print("\nTournament Results")
        print("=" * (10 + 10 * len(agents)))
        print(f"{'Agent':<10}", end="")
        for agent in agents:
            print(f"{agent:>10}", end="")
        print()
        print("-" * (10 + 10 * len(agents)))
        
        # Print results for each agent
        for agent in agents:
            print(f"{agent:<10}", end="")
            for opponent in agents:
                if agent == opponent:
                    print(f"{'-':>10}", end="")
                else:
                    # Calculate score against this opponent
                    score = 0.0
                    games = 0
                    for record in batch.records:
                        if record.white_agent == agent and record.black_agent == opponent:
                            if record.result == GameResult.WHITE_WIN:
                                score += 1
                            elif record.result == GameResult.DRAW:
                                score += 0.5
                            games += 1
                        elif record.white_agent == opponent and record.black_agent == agent:
                            if record.result == GameResult.BLACK_WIN:
                                score += 1
                            elif record.result == GameResult.DRAW:
                                score += 0.5
                            games += 1
                    
                    if games > 0:
                        print(f"{score:>10.1f}", end="")
                    else:
                        print(f"{'-':>10}", end="")
            print()
        
        print("=" * (10 + 10 * len(agents)))
        
        # Print overall win rates
        print("\nOverall Win Rates:")
        print("-" * 30)
        for agent in agents:
            win_rate = batch.get_win_rate(agent)
            print(f"{agent}: {win_rate:.1%}")


class SelfPlayRunner(MatchRunner):
    """
    Specialized runner for self-play training.
    
    Supports:
    - Self-play for reinforcement learning
    - Position evaluation data collection
    - Opening book generation
    """
    
    def run_self_play(
        self,
        agent: ChessAgent,
        games: int = 1,
        **kwargs
    ) -> GameRecordBatch:
        """
        Run self-play games (agent plays against itself).
        
        Args:
            agent: The agent to use for both sides
            games: Number of games to play
            **kwargs: Additional arguments passed to run()
        
        Returns:
            GameRecordBatch with all games
        """
        batch = GameRecordBatch()
        
        for _ in range(games):
            # Create two instances of the same agent
            white = agent.__class__(**self._get_agent_init_args(agent))
            black = agent.__class__(**self._get_agent_init_args(agent))
            
            record = self.run(white, black, **kwargs)
            batch.add(record)
        
        return batch
    
    def _get_agent_init_args(self, agent: ChessAgent) -> dict:
        """Get initialization arguments for creating agent instances."""
        # This is a simple implementation - in practice you might want
        # to store the init args when creating the agent
        return {}
