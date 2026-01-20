"""
Agent registry for managing available chess agents.

This module provides a registry pattern for registering and retrieving
chess agents by name, useful for configuration and dynamic loading.
"""

from typing import Dict, Type, Optional
from .base import ChessAgent


class AgentRegistry:
    """
    Registry for chess agents.
    
    Allows agents to be registered with a name and later retrieved
    by that name. Useful for configuration files and dynamic agent loading.
    """
    
    _agents: Dict[str, Type[ChessAgent]] = {}
    
    @classmethod
    def register(cls, name: str, agent_class: Type[ChessAgent]) -> None:
        """
        Register an agent class with a name.
        
        Args:
            name: The name to register the agent under
            agent_class: The agent class to register
        """
        cls._agents[name] = agent_class
    
    @classmethod
    def get(cls, name: str) -> Optional[Type[ChessAgent]]:
        """
        Get an agent class by name.
        
        Args:
            name: The name of the agent to retrieve
        
        Returns:
            The agent class if found, None otherwise
        """
        return cls._agents.get(name)
    
    @classmethod
    def create(cls, name: str, **kwargs) -> Optional[ChessAgent]:
        """
        Create an agent instance by name.
        
        Args:
            name: The name of the agent to create
            **kwargs: Arguments to pass to the agent constructor
        
        Returns:
            A new agent instance if found, None otherwise
        """
        agent_class = cls.get(name)
        if agent_class is None:
            return None
        return agent_class(**kwargs)
    
    @classmethod
    def list_agents(cls) -> list[str]:
        """
        List all registered agent names.
        
        Returns:
            List of registered agent names
        """
        return list(cls._agents.keys())
    
    @classmethod
    def is_registered(cls, name: str) -> bool:
        """
        Check if an agent is registered.
        
        Args:
            name: The name to check
        
        Returns:
            True if registered, False otherwise
        """
        return name in cls._agents


def register_agent(name: str):
    """
    Decorator for registering agent classes.
    
    Usage:
        @register_agent("my_agent")
        class MyAgent(ChessAgent):
            ...
    
    Args:
        name: The name to register the agent under
    """
    def decorator(agent_class: Type[ChessAgent]):
        AgentRegistry.register(name, agent_class)
        return agent_class
    return decorator
