"""
Chess Service Layer - FastAPI backend with SSE support.

This is a single-file backend that:
1. Manages game state
2. Schedules algorithm layer agents
3. Broadcasts state changes via SSE
"""

import asyncio
import json
import uuid
from typing import Dict, List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import chess

# Import from algorithm layer
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from algorithms_core import (
    ChessGame, ChessMove, Color, GameResult,
    ChessAgent, RandomAgent,
    MaterialEvaluator, MinimaxAgent, MCTSAgent, StockfishAgent,
    AgentRegistry
)

# ============================================================================
# Data Models
# ============================================================================

class AgentConfig(BaseModel):
    """Configuration for an agent."""
    type: str
    depth: Optional[int] = None
    time_limit: Optional[float] = None
    simulations: Optional[int] = None
    skill_level: Optional[int] = None
    exploration_weight: Optional[float] = None
    use_quiescence: Optional[bool] = False


class SetAgentRequest(BaseModel):
    """Request to set an agent."""
    color: str  # "white" or "black"
    agent: AgentConfig


class MoveRequest(BaseModel):
    """Request to make a move."""
    move: str  # UCI format


# ============================================================================
# Global State
# ============================================================================

# Game storage: game_id -> ChessGame
GAMES: Dict[str, ChessGame] = {}

# Agent storage: game_id -> {color: ChessAgent}
AGENTS: Dict[str, Dict[str, ChessAgent]] = {}

# SSE subscribers: game_id -> list[asyncio.Queue]
SUBSCRIBERS: Dict[str, List[asyncio.Queue]] = {}

# Evaluator for position evaluation
EVALUATOR = MaterialEvaluator()


# ============================================================================
# Agent Factory
# ============================================================================

def create_agent(config: AgentConfig) -> ChessAgent:
    """
    Create an agent from configuration.
    
    Args:
        config: Agent configuration
    
    Returns:
        ChessAgent instance
    """
    agent_type = config.type.lower()
    
    if agent_type == "random":
        return RandomAgent()
    
    elif agent_type == "minimax":
        return MinimaxAgent(
            evaluator=EVALUATOR,
            depth=config.depth or 4,
            time_limit=config.time_limit,
            use_quiescence=config.use_quiescence or False
        )
    
    elif agent_type == "mcts":
        return MCTSAgent(
            evaluator=EVALUATOR,
            time_limit=config.time_limit or 1.0,
            exploration_weight=config.exploration_weight or 1.414,
            use_evaluation_rollout=True
        )
    
    elif agent_type == "stockfish":
        return StockfishAgent(
            skill_level=config.skill_level or 15,
            time_limit=config.time_limit or 0.5,
            depth=config.depth
        )
    
    else:
        raise HTTPException(status_code=400, detail=f"Unknown agent type: {agent_type}")


# ============================================================================
# SSE Utilities
# ============================================================================

async def broadcast_event(game_id: str, event_type: str, data: dict):
    """
    Broadcast an event to all subscribers of a game.
    
    Args:
        game_id: The game ID
        event_type: Type of event (state, ai_move, game_over)
        data: Event data
    """
    if game_id not in SUBSCRIBERS:
        return
    
    message = f"event: {event_type}\ndata: {json.dumps(data)}\n\n"
    
    # Send to all subscribers
    for queue in SUBSCRIBERS[game_id][:]:
        try:
            await queue.put(message)
        except:
            # Remove broken queues
            SUBSCRIBERS[game_id].remove(queue)


async def event_generator(game_id: str):
    """
    SSE event generator for a game.
    
    Args:
        game_id: The game ID
    
    Yields:
        SSE event strings
    """
    queue = asyncio.Queue()
    
    # Add subscriber
    if game_id not in SUBSCRIBERS:
        SUBSCRIBERS[game_id] = []
    SUBSCRIBERS[game_id].append(queue)
    
    try:
        # Send initial state
        game = GAMES.get(game_id)
        if game:
            await broadcast_event(game_id, "state", get_game_state(game_id))
        
        # Stream events
        while True:
            message = await queue.get()
            yield message
    except asyncio.CancelledError:
        pass
    finally:
        # Remove subscriber
        if game_id in SUBSCRIBERS and queue in SUBSCRIBERS[game_id]:
            SUBSCRIBERS[game_id].remove(queue)


def get_game_state(game_id: str) -> dict:
    """
    Get the current state of a game.
    
    Args:
        game_id: The game ID
    
    Returns:
        Dictionary with game state
    """
    game = GAMES.get(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    state = game.state
    eval_score = EVALUATOR.evaluate(state)
    
    return {
        "fen": state.fen,
        "current_player": state.current_player.value,
        "eval": eval_score / 100.0,  # Normalize to pawns
        "history": [str(move) for move in state.move_history],
        "is_terminal": state.is_terminal,
        "result": state.result.value if state.result else None
    }


# ============================================================================
# FastAPI App
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager."""
    yield
    # Cleanup: remove all subscribers
    SUBSCRIBERS.clear()


app = FastAPI(
    title="Chess Research Platform",
    description="Service layer for chess algorithm research",
    lifespan=lifespan
)

# Mount static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")


# ============================================================================
# SSE Endpoint
# ============================================================================

@app.get("/events/{game_id}")
async def events(game_id: str):
    """
    SSE endpoint for game events.
    
    Streams:
    - state: New game state
    - ai_move: AI move completed
    - game_over: Game ended
    """
    return StreamingResponse(
        event_generator(game_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


# ============================================================================
# Game Control Endpoints
# ============================================================================

@app.post("/game/new")
async def new_game() -> dict:
    """
    Create a new game.
    
    Returns:
        Dictionary with game_id
    """
    game_id = str(uuid.uuid4())
    
    # Create game
    game = ChessGame()
    GAMES[game_id] = game
    
    # Create default agents
    AGENTS[game_id] = {
        "white": RandomAgent(),
        "black": RandomAgent()
    }
    
    # Initialize subscribers
    SUBSCRIBERS[game_id] = []
    
    # Broadcast initial state
    await broadcast_event(game_id, "state", get_game_state(game_id))
    
    return {"game_id": game_id}


@app.post("/game/reset/{game_id}")
async def reset_game(game_id: str) -> dict:
    """
    Reset a game to starting position.
    
    Args:
        game_id: The game ID
    
    Returns:
        Dictionary with game state
    """
    game = GAMES.get(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    # Reset game
    game.reset()
    
    # Reset agents
    for color, agent in AGENTS[game_id].items():
        agent.reset(Color.WHITE if color == "white" else Color.BLACK)
    
    # Broadcast new state
    await broadcast_event(game_id, "state", get_game_state(game_id))
    
    return get_game_state(game_id)


@app.get("/game/state/{game_id}")
async def get_state(game_id: str) -> dict:
    """
    Get the current state of a game.
    
    Args:
        game_id: The game ID
    
    Returns:
        Dictionary with game state
    """
    return get_game_state(game_id)


@app.get("/game/legal_moves/{game_id}")
async def get_legal_moves(game_id: str) -> dict:
    """
    Get legal moves for the current position.
    
    Args:
        game_id: The game ID
    
    Returns:
        Dictionary with legal moves
    """
    game = GAMES.get(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    return {
        "moves": [str(move) for move in game.legal_moves()]
    }


# ============================================================================
# Move Endpoints
# ============================================================================

@app.post("/game/move/{game_id}")
async def make_move(game_id: str, request: MoveRequest) -> dict:
    """
    Make a move in a game.
    
    Args:
        game_id: The game ID
        request: Move request with UCI move string
    
    Returns:
        Dictionary with game state
    """
    game = GAMES.get(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    # Parse move
    try:
        move = ChessMove.from_uci(request.move)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid move format")
    
    # Make move
    try:
        state = game.step(move)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Broadcast new state
    await broadcast_event(game_id, "state", get_game_state(game_id))
    
    # Check if game over
    if state.is_terminal:
        await broadcast_event(
            game_id,
            "game_over",
            {"result": state.result.value if state.result else None}
        )
    
    return get_game_state(game_id)


@app.post("/game/ai_move/{game_id}")
async def make_ai_move(game_id: str) -> dict:
    """
    Make an AI move for the current player.
    
    Args:
        game_id: The game ID
    
    Returns:
        Dictionary with game state
    """
    game = GAMES.get(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    # Get current player's agent
    current_color = game.turn()
    color_key = "white" if current_color == Color.WHITE else "black"
    agent = AGENTS[game_id].get(color_key)
    
    if not agent:
        raise HTTPException(status_code=400, detail="No agent set for current player")
    
    # Get move from agent
    state = game.state
    move = agent.act(state)
    
    # Make move
    new_state = game.step(move)
    
    # Broadcast AI move event
    await broadcast_event(
        game_id,
        "ai_move",
        {
            "move": str(move),
            "color": color_key,
            "agent": agent.name
        }
    )
    
    # Broadcast new state
    await broadcast_event(game_id, "state", get_game_state(game_id))
    
    # Check if game over
    if new_state.is_terminal:
        await broadcast_event(
            game_id,
            "game_over",
            {"result": new_state.result.value if new_state.result else None}
        )
    
    return get_game_state(game_id)


# ============================================================================
# Agent Management Endpoints
# ============================================================================

@app.post("/game/set_agent/{game_id}")
async def set_agent(game_id: str, request: SetAgentRequest) -> dict:
    """
    Set an agent for a player.
    
    Args:
        game_id: The game ID
        request: Agent configuration
    
    Returns:
        Dictionary with agent info
    """
    game = GAMES.get(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    # Create agent
    agent = create_agent(request.agent)
    
    # Set agent color
    color = Color.WHITE if request.color == "white" else Color.BLACK
    agent.reset(color)
    
    # Store agent
    AGENTS[game_id][request.color] = agent
    
    return {
        "color": request.color,
        "agent": agent.name,
        "config": request.agent.dict()
    }


@app.get("/game/agents/{game_id}")
async def get_agents(game_id: str) -> dict:
    """
    Get current agents for a game.
    
    Args:
        game_id: The game ID
    
    Returns:
        Dictionary with agent info
    """
    if game_id not in AGENTS:
        raise HTTPException(status_code=404, detail="Game not found")
    
    return {
        "white": AGENTS[game_id]["white"].name,
        "black": AGENTS[game_id]["black"].name
    }


# ============================================================================
# Available Agents Endpoint
# ============================================================================

@app.get("/agents/available")
async def get_available_agents() -> dict:
    """
    Get list of available agent types.
    
    Returns:
        Dictionary with available agents and their parameters
    """
    return {
        "agents": [
            {
                "type": "random",
                "name": "Random Agent",
                "description": "Makes random legal moves",
                "parameters": []
            },
            {
                "type": "minimax",
                "name": "Minimax",
                "description": "Minimax with Alpha-Beta pruning",
                "parameters": [
                    {"name": "depth", "type": "integer", "default": 4, "min": 1, "max": 10},
                    {"name": "time_limit", "type": "float", "default": 5.0, "min": 0.1},
                    {"name": "use_quiescence", "type": "boolean", "default": False}
                ]
            },
            {
                "type": "mcts",
                "name": "MCTS",
                "description": "Monte Carlo Tree Search",
                "parameters": [
                    {"name": "time_limit", "type": "float", "default": 1.0, "min": 0.1},
                    {"name": "exploration_weight", "type": "float", "default": 1.414},
                    {"name": "use_evaluation_rollout", "type": "boolean", "default": True}
                ]
            },
            {
                "type": "stockfish",
                "name": "Stockfish",
                "description": "Stockfish chess engine",
                "parameters": [
                    {"name": "skill_level", "type": "integer", "default": 15, "min": 0, "max": 20},
                    {"name": "time_limit", "type": "float", "default": 0.5, "min": 0.1},
                    {"name": "depth", "type": "integer", "default": None}
                ]
            }
        ]
    }


# ============================================================================
# Root Endpoint
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Chess Research Platform API",
        "docs": "/docs",
        "events": "/events/{game_id}"
    }


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
