# ai_agent.py
# -------------------------
# Helper that builds an agent and returns the final AI message text.

from __future__ import annotations
import os
from typing import Iterable, List, Sequence, Tuple, Union

from dotenv import load_dotenv, find_dotenv

# Load .env early
load_dotenv(find_dotenv(usecwd=True), override=True)

from langgraph.prebuilt import create_react_agent
from langchain_core.messages import AIMessage, BaseMessage

# Primary providers
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch

# Optional providers (only used if you pick them)
try:
    from langchain_anthropic import ChatAnthropic  # requires ANTHROPIC_API_KEY
except Exception:
    ChatAnthropic = None  # type: ignore

try:
    # Local models via Ollama (optional, no key needed, must have Ollama running)
    from langchain_community.chat_models import ChatOllama
except Exception:
    ChatOllama = None  # type: ignore


# --------- Config / Model registry ---------
# You can add more here freely.
ALLOWED_MODEL_NAMES = {
    # Groq
    "llama-3.1-8b-instant",
    "llama-3.1-70b-versatile",
    # OpenAI
    "gpt-4o-mini",
    # Anthropic (optional)
    "claude-3-haiku-20240307",
    # Local (Ollama) – model tags differ per your machine
    "llama3.1:8b",
}

ALLOWED_PROVIDERS = {"Groq", "OpenAI", "Anthropic", "Ollama"}


def _build_llm(provider: str, model_id: str):
    p = provider.strip().lower()
    if p == "groq":
        return ChatGroq(model=model_id)
    if p == "openai":
        return ChatOpenAI(model=model_id)
    if p == "anthropic":
        if ChatAnthropic is None:
            raise RuntimeError("Anthropic not installed. `pip install langchain-anthropic`")
        return ChatAnthropic(model=model_id)
    if p == "ollama":
        if ChatOllama is None:
            raise RuntimeError("Ollama not installed. `pip install langchain-community` and run Ollama.")
        return ChatOllama(model=model_id)
    raise ValueError("Unknown provider. Use one of: " + ", ".join(sorted(ALLOWED_PROVIDERS)))


def _normalize_messages(
    messages: Union[str, Tuple[str, str], Sequence[Tuple[str, str]], Sequence[BaseMessage]],
    system_prompt: str | None,
):
    """Return a list of (role, content) tuples for LangGraph."""
    norm: List[Tuple[str, str]] = []
    if system_prompt:
        norm.append(("system", system_prompt))

    # simple string = one user message
    if isinstance(messages, str):
        norm.append(("user", messages))
        return norm

    # tuple ("role","text")
    if isinstance(messages, tuple) and len(messages) == 2 and isinstance(messages[0], str):
        norm.append((messages[0], messages[1]))
        return norm

    # already a list/tuple of tuples
    if isinstance(messages, Iterable) and messages and isinstance(next(iter(messages)), tuple):
        norm.extend(messages)  # type: ignore[arg-type]
        return norm

    # list of message objects (rare in your case)
    if isinstance(messages, Iterable) and messages and isinstance(next(iter(messages)), BaseMessage):
        # LangGraph will accept these directly, but keep it uniform:
        norm.extend([(m.type, m.content) for m in messages])  # type: ignore
        return norm

    raise ValueError("Unsupported messages format. Use str or list of (role, content) tuples.")


def get_response_from_ai_agent(
    llm_id: str,
    messages: Union[str, Tuple[str, str], Sequence[Tuple[str, str]], Sequence[BaseMessage]],
    allow_search: bool,
    provider: str,
    system_prompt: str | None = None,
) -> str:
    """Create a ReAct agent and return the final AI reply text."""
    llm = _build_llm(provider, llm_id)
    tools = [TavilySearch(max_results=3)] if allow_search else []

    agent = create_react_agent(model=llm, tools=tools)

    state = {"messages": _normalize_messages(messages, system_prompt)}
    result = agent.invoke(state)

    msgs: List[BaseMessage] = result.get("messages", [])
    # return the last AI message content if present
    for m in reversed(msgs):
        if isinstance(m, AIMessage):
            return m.content
    return msgs[-1].content if msgs else ""
