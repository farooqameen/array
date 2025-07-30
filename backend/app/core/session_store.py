from collections import defaultdict
from typing import Any, Dict

from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import AIMessage, HumanMessage

# Session engine store (in-memory cache)
engine_store: Dict[str, Any] = {}

# LangChain-compatible per-session message history
_session_histories = defaultdict(InMemoryChatMessageHistory)


def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    """
    Get or create LangChain memory store for the session.
    """
    history = _session_histories[session_id]
    print(f"[DEBUG] History length for {session_id}: {len(history.messages)}")
    return history


def append_message(session_id: str, role: str, content: str) -> None:
    """
    Append a message to the chat history for a given session.
    """
    history = _session_histories[session_id]

    if role == "human":
        history.add_message(HumanMessage(content=content))
    elif role == "assistant":
        history.add_message(AIMessage(content=content))
    else:
        raise ValueError(f"Unknown role '{role}'")

    print(f"[DEBUG] Message appended. New history length: {len(history.messages)}")


def set_engine(session_id: str, engine: Any) -> None:
    """
    Cache the query engine for a session.
    """
    engine_store[session_id] = engine


def get_engine(session_id: str) -> Any:
    """
    Retrieve the query engine for a session.
    """
    return engine_store.get(session_id)


def reset_session(session_id: str) -> None:
    """
    Reset memory and cached engine for a session.
    """
    engine_store.pop(session_id, None)
    _session_histories.pop(session_id, None)
