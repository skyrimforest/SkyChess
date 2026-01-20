# Chess Service Layer

FastAPI backend with SSE support for chess research platform.

## Quick Start

### 1. Install Dependencies

```bash
# Python dependencies
pip install fastapi uvicorn python-chess stockfish

# For Stockfish engine, download the executable:
# Windows: https://stockfishchess.org/files/stockfish_16_win_x64_avx2.zip
# macOS: https://stockfishchess.org/files/stockfish_16_macos_x64_avx2.zip
# Linux: https://stockfishchess.org/files/stockfish_16_linux_x64_avx2.zip
```

### 2. Start the Backend

```bash
cd chess_app
python main.py
```

The server will start at `http://localhost:8000`

### 3. Open the Frontend

Open your browser and navigate to:
```
http://localhost:8000/static/index.html
```

## SSE (Server-Sent Events) Overview

### What is SSE?

SSE is a server-push technology that allows the server to send updates to the client over a single HTTP connection. Unlike WebSocket, SSE is one-way (server to client), which is perfect for our use case of broadcasting game state updates.

### How It Works

1. **Client connects** to `/events/{game_id}` endpoint
2. **Server keeps connection open** and sends events as they happen
3. **Client receives events** in real-time without polling

### SSE Event Types

| Event Type | Description | Data Format |
|-------------|-------------|--------------|
| `state` | New game state | `{fen, current_player, eval, history, ...}` |
| `ai_move` | AI move completed | `{move, color, agent}` |
| `game_over` | Game ended | `{result}` |

### Example SSE Event

```
event: state
data: {
  "fen": "rnbqkbnr/pppppppp/8/8/4P3/8/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1",
  "current_player": "black",
  "eval": -0.42,
  "history": ["e2e4"],
  "is_terminal": false,
  "result": null
}

```

## Frontend Features

### Chess Board

- **Interactive board** - Drag and drop pieces to make moves
- **Legal move highlighting** - Click a piece to see legal moves
- **Move validation** - Illegal moves are rejected
- **FEN-based rendering** - Board state from backend

### Control Panel

- **Agent selection** - Choose algorithm for each player
- **Parameter tuning** - Adjust depth, time limit, skill level in real-time
- **AI Move button** - Trigger AI to make a move
- **Auto Play** - Watch AI vs AI play automatically
- **Game controls** - New game, reset game

### Evaluation Display

- **Numeric evaluation** - Shows position score in pawns
- **Visual eval bar** - Vertical bar showing advantage
  - Red = White advantage
  - Blue = Black advantage
  - Updates in real-time via SSE

### Move History

- **SAN notation** - Standard algebraic notation (e.g., "e4", "Nf3")
- **Scrollable list** - View complete game history
- **Current move highlight** - Shows last move made

### Status Indicators

- **Connection status** - Shows SSE connection state
- **Turn indicator** - Shows whose turn it is
- **AI thinking** - Spinner when AI is calculating

## API Endpoints

### Game Control

#### Create New Game
```http
POST /game/new
```
Response: `{"game_id": "uuid"}`

#### Reset Game
```http
POST /game/reset/{game_id}
```

#### Get Game State
```http
GET /game/state/{game_id}
```
Response: Game state object

#### Get Legal Moves
```http
GET /game/legal_moves/{game_id}
```
Response: `{"moves": ["e2e4", "d2d4", ...]}`

### Move Operations

#### Make Move
```http
POST /game/move/{game_id}
Content-Type: application/json

{"move": "e2e4"}
```

#### Make AI Move
```http
POST /game/ai_move/{game_id}
```

### Agent Management

#### Set Agent
```http
POST /game/set_agent/{game_id}
Content-Type: application/json

{
  "color": "black",
  "agent": {
    "type": "minimax",
    "depth": 4,
    "time_limit": 5.0
  }
}
```

#### Get Available Agents
```http
GET /agents/available
```
Response: List of agent types with parameters

## Available Algorithms

### Random Agent
- Makes random legal moves
- No parameters
- Good for testing and baseline

### Minimax
- Classic minimax with alpha-beta pruning
- Parameters:
  - `depth` (1-10): Search depth
  - `time_limit` (float): Maximum search time
  - `use_quiescence` (boolean): Extend search in tactical positions

### MCTS
- Monte Carlo Tree Search with UCT
- Parameters:
  - `time_limit` (float): Search time per move
  - `exploration_weight` (float): UCT exploration constant
  - `use_evaluation_rollout` (boolean): Use evaluation for rollouts

### Stockfish
- World-class chess engine
- Parameters:
  - `skill_level` (0-20): Playing strength
  - `time_limit` (float): Search time per move
  - `depth` (integer): Search depth (None = auto)

## How to Add a New Algorithm

### 1. Add to Algorithm Layer

Create a new agent in `algorithms_core/agent/`:

```python
from algorithms_core.agent import ChessAgent, register_agent

@register_agent("my_algorithm")
class MyAgent(ChessAgent):
    name = "My Algorithm"
    
    def act(self, state):
        # Your move selection logic
        return best_move
```

### 2. Update Backend

Add to `main.py` in the `create_agent()` function:

```python
elif agent_type == "my_algorithm":
    return MyAgent(param1=value1, param2=value2)
```

Add to `/agents/available` endpoint:

```python
{
    "type": "my_algorithm",
    "name": "My Algorithm",
    "description": "Description of your algorithm",
    "parameters": [
        {"name": "param1", "type": "integer", "default": 10},
        {"name": "param2", "type": "float", "default": 1.5}
    ]
}
```

### 3. Frontend Updates

The frontend will automatically discover and display your new algorithm from the `/agents/available` endpoint. No frontend code changes needed!

## Architecture

```
┌─────────────┐
│   Browser   │
│  (Frontend) │
└──────┬──────┘
       │
       ├───────────── SSE ───────────┐
       │                               │
       │ HTTP                         │
       │                               │
┌──────▼───────────────────────────────▼────────┐
│          FastAPI Backend (main.py)          │
│                                            │
│  ┌──────────┐  ┌──────────┐  ┌────────┐ │
│  │  Games   │  │  Agents  │  │   SSE  │ │
│  │  Storage │  │ Manager  │  │ Stream │ │
│  └──────────┘  └──────────┘  └────────┘ │
│         │              │              │         │
│         └──────────────┴──────────────┘         │
│                       │                        │
└───────────────────────┼────────────────────────┘
                        │
┌───────────────────────▼────────────────────────┐
│         Algorithm Layer (algorithms_core)       │
│  ┌──────────┐  ┌──────────┐  ┌────────┐ │
│  │   Game   │  │  Engine  │  │ Agent  │ │
│  └──────────┘  └──────────┘  └────────┘ │
└───────────────────────────────────────────────────┘
```

## Troubleshooting

### SSE Connection Issues

- Check that the backend is running on port 8000
- Verify firewall allows connections to localhost:8000
- Check browser console for connection errors

### Stockfish Not Working

- Ensure Stockfish executable is in PATH
- Or specify path in `StockfishAgent` constructor
- Test Stockfish works independently: `stockfish --version`

### Move Rejected

- Check that move is legal (highlighted squares)
- Verify it's your turn
- Check if game is over

## License

This is part of the international chess research platform project.
