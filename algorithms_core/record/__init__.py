"""
Record module for chess game recording and analysis.

This module provides data structures for recording and analyzing
chess games, useful for self-play and dataset generation.
"""

from .game_record import GameRecord, GameRecordBatch

__all__ = [
    "GameRecord",
    "GameRecordBatch",
]
