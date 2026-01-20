# Chess Algorithm Core

Research-grade chess algorithm layer for international chess research platform.

## Overview

This module provides a complete, research-oriented algorithm layer for chess, designed for:

- **Search algorithm research** (Minimax, Alpha-Beta, MCTS)
- **Classic engine integration** (Stockfish)
- **Reinforcement learning / Self-play**
- **Future LLM Chess Agent integration**

**This layer contains no UI, HTTP, frontend, or database logic** - it focuses purely on algorithms, state management, interfaces, and extensibility.

## Design Principles

1. **Algorithm and rules decoupled** - Search algorithms don't depend on game rules
2. **Agent ≠ Engine ≠ Game** - Clear separation of concerns
3. **Stable interfaces** - Long-term compatibility for paper reproduction
4. **Multi-agent support** - Support for multiple agents playing in the same game
5. **Research-friendly** - Follows mainstream research paradigms:
   - OpenAI Gym / PettingZoo patterns
   - AlphaZero / MuZero style abstraction
   - UCI Engine Adapter concepts

## Dependencies

```bash
# Core dependencies
pip install python-chess

# For Stockfish engine
pip install stockfish

# Optional: For Stockfish executable
# Download from: https://stockfishchess.org/download/
```

## Directory Structure

```
algorithms_core/
├── game/              # Game environment and state management
│   ├── chess_game.py   # ChessGame - environment abstraction
│   ├── game_state.py   # GameState - core data structure
│   └── types.py       # Type definitions (Color, ChessMove, etc.)
│
├── agent/             # Decision-making strategies
│   ├── base.py        # ChessAgent abstract base class
│   ├── random_agent.py # RandomAgent, WeightedRandomAgent
│   ├── engine_agent.py # EngineBasedAgent, MinimaxAgent, etc.
│   └── registry.py    # Agent registry for dynamic loading
│
├── engine/            # Search algorithms
│   ├── base.py        # SearchEngine abstract base class
│   ├── minimax.py    # Minimax with Alpha-Beta pruning
│   ├── mcts.py       # Monte Carlo Tree Search
│   └── stockfish_engine.py  # Stockfish UCI adapter
│
├── eval/              # Position evaluation
│   ├── base.py        # Evaluator abstract base class
│   └── material_eval.py  # Material-based evaluation
│
├── record/            # Game recording and analysis
│   └── game_record.py  # GameRecord, GameRecordBatch
│
├── match_runner.py    # Multi-agent match execution
└── README.md          # This file
```

## Core Concepts

### Agent vs Engine vs Game

| Component | Purpose | Example |
|-----------|---------|---------|
| **Game** | Environment abstraction, rules, state transitions | `ChessGame` |
| **Engine** | Search algorithm, finds best move from a position | `MinimaxEngine`, `MCTSEngine`, `StockfishEngine` |
| **Agent** | Decision strategy, may use engines internally | `RandomAgent`, `MinimaxAgent`, `StockfishAgent` |

- **Game** = The chess board, rules, and legal moves
- **Engine** = How to find the best move (algorithm)
- **Agent** = Who is playing (strategy)

## Quick Start

### Basic Game Play

```python
from algorithms_core import ChessGame, RandomAgent, MatchRunner

# Create agents
white = RandomAgent()
black = RandomAgent()

# Run a game
runner = MatchRunner(verbose=True)
record = runner.run(white, black)

print(f"Result: {record.result}")
print(f"Moves: {record.move_count}")
```

### Using Search Engines

```python
from algorithms_core import (
    ChessGame, MaterialEvaluator, MinimaxAgent, MCTSAgent
)

# Create evaluator
evaluator = MaterialEvaluator()

# Create engine-based agents
minimax_agent = MinimaxAgent(evaluator, depth=4)
mcts_agent = MCTSAgent(evaluator, time_limit=1.0)

# Run a match
runner = MatchRunner()
record = runner.run(minimax_agent, mcts_agent)
```

### Using Stockfish

```python
from algorithms_core import StockfishAgent, MatchRunner

# Create Stockfish agent
stockfish = StockfishAgent(
    skill_level=15,  # 0-20
    time_limit=0.5   # seconds
)

# Run against another agent
runner = MatchRunner()
record = runner.run(stockfish, RandomAgent())
```

## Components

### Game Layer

#### ChessGame

Environment abstraction following OpenAI Gym / PettingZoo patterns:

```python
from algorithms_core import ChessGame

game = ChessGame()  # Start from standard position
# or
game = ChessGame(fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

state = game.state
legal_moves = game.legal_moves()

# Make a move
from algorithms_core import ChessMove
move = ChessMove.from_uci("e2e4")
new_state = game.step(move)

# Clone for search
cloned = game.clone()
```

#### GameState

Core data structure with FEN as single source of truth:

```python
from algorithms_core import GameState

state = GameState.from_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

print(state.current_player)  # Color.WHITE
print(state.is_terminal)      # False
print(state.legal_moves())    # List of legal moves

# Serialize
data = state.to_dict()
restored = GameState.from_dict(data)
```

### Evaluation Layer

#### MaterialEvaluator

Classic material-based evaluation:

```python
from algorithms_core import MaterialEvaluator

evaluator = MaterialEvaluator()

# Evaluate a position
score = evaluator.evaluate(state)
# Positive = current player has material advantage

# Get detailed material info
material = evaluator.count_material(state)
# {"white_pawn": 8, "white_knight": 2, ...}
```

#### PythonChessEvaluator

Uses python-chess built-in evaluation:

```python
from algorithms_core import PythonChessEvaluator

evaluator = PythonChessEvaluator()
score = evaluator.evaluate(state)
```

### Engine Layer

#### MinimaxEngine

Minimax with Alpha-Beta pruning:

```python
from algorithms_core import MinimaxEngine, MaterialEvaluator

engine = MinimaxEngine(
    evaluator=MaterialEvaluator(),
    default_depth=4,
    use_quiescence=True  # Extend search in tactical positions
)

move = engine.search(game, time_limit=5.0, depth_limit=6)
print(f"Nodes searched: {engine.nodes_searched}")
```

#### MCTSEngine

Monte Carlo Tree Search with UCT:

```python
from algorithms_core import MCTSEngine, MaterialEvaluator

engine = MCTSEngine(
    evaluator=MaterialEvaluator(),
    exploration_weight=1.414,  # UCT constant
    rollout_depth=10,
    use_evaluation_rollout=True
)

move = engine.search(game, time_limit=2.0)
```

#### StockfishEngine

Stockfish UCI adapter:

```python
from algorithms_core import StockfishEngine

engine = StockfishEngine(
    stockfish_path="path/to/stockfish.exe",  # Optional
    skill_level=20,
    depth=15,
    threads=4,
    hash_size=256
)

move = engine.search(game, time_limit=1.0)

# Get evaluation
eval_result = engine.evaluate(game)

# Get top moves
top_moves = engine.get_top_moves(game, num_moves=5)
```

### Agent Layer

#### RandomAgent

```python
from algorithms_core import RandomAgent

agent = RandomAgent(seed=42)  # For reproducibility
move = agent.act(state)
```

#### Engine-Based Agents

```python
from algorithms_core import MinimaxAgent, MCTSAgent, StockfishAgent

# Minimax agent
minimax = MinimaxAgent(evaluator, depth=4, time_limit=5.0)

# MCTS agent
mcts = MCTSAgent(evaluator, time_limit=1.0)

# Stockfish agent
stockfish = StockfishAgent(skill_level=15, time_limit=0.5)
```

### Record Layer

#### GameRecord

```python
from algorithms_core import GameRecord

record = GameRecord(
    white_agent="Minimax",
    black_agent="MCTS"
)

record.add_move(move)
record.set_result(GameResult.WHITE_WIN, "checkmate")

# Export to PGN
print(record.pgn)

# Serialize
data = record.to_dict()
restored = GameRecord.from_dict(data)
```

#### GameRecordBatch

```python
from algorithms_core import GameRecordBatch

batch = GameRecordBatch()
batch.add(record)

# Filter
wins = batch.filter_by_result(GameResult.WHITE_WIN)
agent_games = batch.filter_by_agent("Minimax")

# Statistics
win_rate = batch.get_win_rate("Minimax")
```

### Match Runner

```python
from algorithms_core import MatchRunner, SelfPlayRunner

# Single game
runner = MatchRunner(verbose=True)
record = runner.run(white, black)

# Multi-game match
batch = runner.run_match(white, black, games=10)

# Tournament
agents = [agent1, agent2, agent3]
batch = runner.run_tournament(agents, rounds=2)
runner.print_results(batch)

# Self-play
self_play = SelfPlayRunner()
batch = self_play.run_self_play(agent, games=100)
```

## Adding a New Algorithm

### Adding a New Evaluator

```python
from algorithms_core.eval import Evaluator, GameState

class MyEvaluator(Evaluator):
    def evaluate(self, state: GameState) -> float:
        # Your evaluation logic here
        return score

# Use it
from algorithms_core import MinimaxAgent
agent = MinimaxAgent(MyEvaluator(), depth=4)
```

### Adding a New Search Engine

```python
from algorithms_core.engine import SearchEngine, ChessGame, ChessMove

class MyEngine(SearchEngine):
    def search(self, game: ChessGame, time_limit=None, depth_limit=None):
        # Your search logic here
        return best_move

# Use it via EngineBasedAgent
from algorithms_core.agent import EngineBasedAgent
agent = EngineBasedAgent(MyEngine(), time_limit=1.0)
```

### Adding a New Agent

```python
from algorithms_core.agent import ChessAgent, GameState, ChessMove

class MyAgent(ChessAgent):
    name = "MyAgent"
    
    def act(self, state: GameState) -> ChessMove:
        # Your decision logic here
        return move

# Register for dynamic loading
from algorithms_core.agent import register_agent

@register_agent("my_agent")
class MyAgent(ChessAgent):
    ...
```

## Using for RL / Self-Play

```python
from algorithms_core import SelfPlayRunner, MCTSAgent, MaterialEvaluator

# Create agent
evaluator = MaterialEvaluator()
agent = MCTSAgent(evaluator, time_limit=1.0)

# Run self-play
runner = SelfPlayRunner()
batch = runner.run_self_play(agent, games=1000)

# Process data for training
for record in batch:
    # Extract positions and outcomes
    for i, move in enumerate(record.moves):
        # Your training data processing here
        pass
```

## Research-Friendly Features

- **No global state** - All state is explicit
- **Reproducible experiments** - Random seeds are configurable
- **No magic parameters** - All parameters are explicit
- **Clean interfaces** - Easy to swap components

## License

This is part of the international chess research platform project.
