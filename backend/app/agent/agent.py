"""
LangChain agent with ONE tool (the governed semantic layer).
LLM is built lazily (a missing key no longer crashes startup); any LLM failure becomes a
single LLMUnavailableError with a readable reason; identical questions are cached.
"""
import os
import threading
import time

from app.agent.prompts import SYSTEM_PROMPT
from app.agent.tools import query_semantic_layer_tool

CACHE_TTL = int(os.getenv("AGENT_CACHE_TTL", "600"))
MAX_ITERATIONS = int(os.getenv("AGENT_MAX_ITERATIONS", "5"))


class LLMUnavailableError(Exception):
    """The LLM could not be used (quota, credits, key, retired model...)."""


_executor = None
_lock = threading.Lock()
_cache: dict = {}


def _provider() -> str:
    explicit = os.getenv("LLM_PROVIDER", "").strip().lower()
    if explicit:
        return explicit
    if os.getenv("ANTHROPIC_API_KEY"):
        return "anthropic"
    if os.getenv("XAI_API_KEY"):
        return "xai"
    return "gemini"


def _build_llm():
    provider = _provider()
    model = os.getenv("AGENT_MODEL", "")
    try:
        if provider == "anthropic":
            key = os.getenv("ANTHROPIC_API_KEY")
            if not key:
                raise LLMUnavailableError("ANTHROPIC_API_KEY is not set.")
            from langchain_anthropic import ChatAnthropic
            return ChatAnthropic(model=model or "claude-sonnet-4-6", temperature=0,
                                 anthropic_api_key=key)
        if provider == "xai":
            key = os.getenv("XAI_API_KEY")
            if not key:
                raise LLMUnavailableError("XAI_API_KEY is not set.")
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(model=model or "grok-4.1-fast", temperature=0,
                              api_key=key, base_url="https://api.x.ai/v1")
        if provider == "gemini":
            key = os.getenv("GOOGLE_API_KEY")
            if not key:
                raise LLMUnavailableError("GOOGLE_API_KEY is not set.")
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(model=model or "gemini-3.5-flash-lite",
                                          temperature=0, google_api_key=key)
        raise LLMUnavailableError(f"Unknown LLM_PROVIDER '{provider}'.")
    except ImportError as e:
        raise LLMUnavailableError(f"Package for provider '{provider}' is not installed: {e}")


def _get_executor():
    global _executor
    with _lock:
        if _executor is None:
            from langchain.agents import AgentExecutor, create_tool_calling_agent
            from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

            llm = _build_llm()
            prompt = ChatPromptTemplate.from_messages([
                ("system", SYSTEM_PROMPT),
                ("human", "{input}"),
                MessagesPlaceholder("agent_scratchpad"),
            ])
            tools = [query_semantic_layer_tool]
            agent = create_tool_calling_agent(llm, tools, prompt)
            _executor = AgentExecutor(
                agent=agent, tools=tools, max_iterations=MAX_ITERATIONS,
                return_intermediate_steps=True, handle_parsing_errors=True,
            )
        return _executor


def explain_llm_error(e: Exception) -> str:
    low = f"{type(e).__name__}: {e}".lower()
    if "429" in low or "resource_exhausted" in low or "quota" in low or "rate limit" in low:
        return "The LLM quota/rate limit is exhausted. Wait a minute, or switch API key/provider."
    if "credit balance" in low:
        return "The LLM account has no credit. Add credit or switch provider."
    if "no longer available" in low or "not found" in low or "404" in low:
        return "The configured model is retired/unavailable. Change AGENT_MODEL in backend/.env."
    if "thought_signature" in low:
        return "This Gemini model needs thought-signature support. Use another model/provider."
    if any(k in low for k in ("api key", "api_key", "401", "403", "permission", "unauthorized", "workspace")):
        return "The LLM API key was rejected. Check the key and account settings in backend/.env."
    return f"The LLM call failed ({type(e).__name__})."


def ask(question: str) -> dict:
    key = " ".join(question.lower().split())
    hit = _cache.get(key)
    if hit and time.time() - hit[0] < CACHE_TTL:
        return {**hit[1], "cached": True}

    try:
        executor = _get_executor()
        result = executor.invoke({"input": question})
    except LLMUnavailableError:
        raise
    except Exception as e:
        raise LLMUnavailableError(explain_llm_error(e)) from e

    transparency = []
    for action, observation in result.get("intermediate_steps", []):
        obs = observation if isinstance(observation, dict) else {}
        transparency.append({
            "tool": action.tool,
            "tool_input": action.tool_input,
            "query": obs.get("query"),
            "generated_sql": obs.get("generated_sql"),
            "data": obs.get("data"),
            "error": obs.get("error"),
        })

    out = {"answer": result["output"], "transparency": transparency, "mode": "agent"}
    _cache[key] = (time.time(), out)
    return out