"""
Game record for storing and analyzing chess games.

This module provides data structures for recording chess games,
useful for self-play, dataset generation, and analysis.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from ..game.types import Color, ChessMove, GameResult


@dataclass
class GameRecord:
    """
    Record of a complete chess game.
    
    Stores all information about a played game including:
    - Players (agent names)
    - Moves played
    - Final result
    - Metadata (timestamps, tags, etc.)
    
    Useful for:
    - Self-play data collection
    - Dataset generation for training
    - Game analysis and review
    - Tournament results
    """
    
    # Player information
    white_agent: str
    black_agent: str
    
    # Game data
    moves: List[ChessMove] = field(default_factory=list)
    result: Optional[GameResult] = None
    termination_reason: Optional[str] = None  # e.g., "checkmate", "draw", "resign"
    
    # Metadata
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    initial_fen: Optional[str] = None  # None = standard starting position
    
    # Additional tags (PGN-style)
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Additional data (for research purposes)
    annotations: List[Dict[str, Any]] = field(default_factory=list)
    
    @property
    def move_count(self) -> int:
        """Get the number of moves played."""
        return len(self.moves)
    
    @property
    def duration(self) -> Optional[float]:
        """Get game duration in seconds."""
        if self.end_time and self.start_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
    
    @property
    def pgn(self) -> str:
        """
        Get the game in PGN format.
        
        Returns:
            PGN string representation of the game
        """
        lines = []
        
        # Add tags
        if self.tags:
            for key, value in self.tags.items():
                lines.append(f'[{key} "{value}"]')
        else:
            # Default tags
            lines.append('[Event "Chess Game"]')
            lines.append(f'[White "{self.white_agent}"]')
            lines.append(f'[Black "{self.black_agent}"]')
            if self.result:
                result_str = self._result_to_pgn(self.result)
                lines.append(f'[Result "{result_str}"]')
            if self.initial_fen:
                lines.append(f'[SetUp "1"]')
                lines.append(f'[FEN "{self.initial_fen}"]')
        
        lines.append("")  # Empty line before moves
        
        # Add moves
        move_strings = [str(move) for move in self.moves]
        pgn_moves = self._format_moves_pgn(move_strings)
        lines.append(pgn_moves)
        
        # Add result
        if self.result:
            result_str = self._result_to_pgn(self.result)
            lines[-1] += f" {result_str}"
        
        return "\n".join(lines)
    
    def _format_moves_pgn(self, moves: List[str]) -> str:
        """Format moves into PGN-style move list."""
        result = []
        for i, move in enumerate(moves):
            if i % 2 == 0:
                move_num = i // 2 + 1
                result.append(f"{move_num}.")
            result.append(move)
        return " ".join(result)
    
    def _result_to_pgn(self, result: GameResult) -> str:
        """Convert GameResult to PGN result string."""
        if result == GameResult.WHITE_WIN:
            return "1-0"
        elif result == GameResult.BLACK_WIN:
            return "0-1"
        else:
            return "1/2-1/2"
    
    def add_move(self, move: ChessMove) -> None:
        """
        Add a move to the record.
        
        Args:
            move: The move to add
        """
        self.moves.append(move)
    
    def set_result(self, result: GameResult, reason: str = "") -> None:
        """
        Set the game result.
        
        Args:
            result: The game result
            reason: The reason for termination (e.g., "checkmate")
        """
        self.result = result
        self.termination_reason = reason
        self.end_time = datetime.now()
    
    def add_annotation(self, move_index: int, annotation: Dict[str, Any]) -> None:
        """
        Add an annotation to a move.
        
        Args:
            move_index: Index of the move to annotate
            annotation: Annotation data (e.g., {"eval": 1.5, "comment": "Good move"})
        """
        while len(self.annotations) <= move_index:
            self.annotations.append({})
        self.annotations[move_index].update(annotation)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert record to dictionary for serialization.
        
        Returns:
            Dictionary representation of the record
        """
        return {
            "white_agent": self.white_agent,
            "black_agent": self.black_agent,
            "moves": [str(move) for move in self.moves],
            "result": self.result.value if self.result else None,
            "termination_reason": self.termination_reason,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "initial_fen": self.initial_fen,
            "tags": self.tags,
            "annotations": self.annotations,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GameRecord":
        """
        Create record from dictionary.
        
        Args:
            data: Dictionary representation of the record
        
        Returns:
            GameRecord instance
        """
        record = cls(
            white_agent=data["white_agent"],
            black_agent=data["black_agent"],
            moves=[ChessMove.from_uci(m) for m in data["moves"]],
            result=GameResult(data["result"]) if data.get("result") else None,
            termination_reason=data.get("termination_reason"),
            initial_fen=data.get("initial_fen"),
            tags=data.get("tags", {}),
            annotations=data.get("annotations", []),
        )
        
        if data.get("start_time"):
            record.start_time = datetime.fromisoformat(data["start_time"])
        if data.get("end_time"):
            record.end_time = datetime.fromisoformat(data["end_time"])
        
        return record
    
    def __str__(self) -> str:
        """String representation of the record."""
        return (
            f"GameRecord({self.white_agent} vs {self.black_agent}, "
            f"result={self.result}, moves={self.move_count})"
        )


class GameRecordBatch:
    """
    Container for multiple game records.
    
    Useful for:
    - Batch processing of games
    - Dataset management
    - Tournament results
    """
    
    def __init__(self, records: Optional[List[GameRecord]] = None):
        """
        Initialize the batch.
        
        Args:
            records: Initial list of records
        """
        self.records = records or []
    
    def add(self, record: GameRecord) -> None:
        """
        Add a record to the batch.
        
        Args:
            record: The record to add
        """
        self.records.append(record)
    
    def extend(self, records: List[GameRecord]) -> None:
        """
        Add multiple records to the batch.
        
        Args:
            records: List of records to add
        """
        self.records.extend(records)
    
    def filter_by_result(self, result: GameResult) -> "GameRecordBatch":
        """
        Filter records by result.
        
        Args:
            result: The result to filter by
        
        Returns:
            New GameRecordBatch with filtered records
        """
        filtered = [r for r in self.records if r.result == result]
        return GameRecordBatch(filtered)
    
    def filter_by_agent(self, agent_name: str) -> "GameRecordBatch":
        """
        Filter records by agent name.
        
        Args:
            agent_name: The agent name to filter by
        
        Returns:
            New GameRecordBatch with filtered records
        """
        filtered = [
            r for r in self.records 
            if r.white_agent == agent_name or r.black_agent == agent_name
        ]
        return GameRecordBatch(filtered)
    
    def get_win_rate(self, agent_name: str) -> float:
        """
        Calculate win rate for an agent.
        
        Args:
            agent_name: The agent name
        
        Returns:
            Win rate (0.0 to 1.0)
        """
        if not self.records:
            return 0.0
        
        wins = 0
        total = 0
        
        for record in self.records:
            if record.result is None:
                continue
            
            total += 1
            if agent_name == record.white_agent:
                if record.result == GameResult.WHITE_WIN:
                    wins += 1
                elif record.result == GameResult.DRAW:
                    wins += 0.5
            elif agent_name == record.black_agent:
                if record.result == GameResult.BLACK_WIN:
                    wins += 1
                elif record.result == GameResult.DRAW:
                    wins += 0.5
        
        return wins / total if total > 0 else 0.0
    
    def to_dict(self) -> List[Dict[str, Any]]:
        """
        Convert all records to dictionaries.
        
        Returns:
            List of dictionary representations
        """
        return [record.to_dict() for record in self.records]
    
    @classmethod
    def from_dict(cls, data: List[Dict[str, Any]]) -> "GameRecordBatch":
        """
        Create batch from list of dictionaries.
        
        Args:
            data: List of dictionary representations
        
        Returns:
            GameRecordBatch instance
        """
        records = [GameRecord.from_dict(d) for d in data]
        return cls(records)
    
    def __len__(self) -> int:
        """Get the number of records."""
        return len(self.records)
    
    def __getitem__(self, index: int) -> GameRecord:
        """Get a record by index."""
        return self.records[index]
    
    def __iter__(self):
        """Iterate over records."""
        return iter(self.records)
