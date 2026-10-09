"""
Owner: Member 4 (AI / Agent Engineer)
Wires the LLM + the single semantic-layer tool into a LangChain agent.
"""

import json
import os

from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI

from app.agent.prompts import SYSTEM_PROMPT
from app.agent.tools import query_semantic_layer_tool


_llm = ChatGoogleGenerativeAI(
    model=os.getenv("AGENT_MODEL", "gemini-3.8-flash"),
    temperature=0,
    google_api_key=os.getenv("GOOGLE_API_KEY"),
)

_tools = [query_semantic_layer_tool]

_agent = create_agent(
    model=_llm,
    tools=_tools,
    system_prompt=SYSTEM_PROMPT,
)


def _parse_tool_output(content):
    """Convert a tool message into a Python dictionary when possible."""
    if isinstance(content, dict):
        return content

    if isinstance(content, str):
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {}

    return {}


def _message_text(content) -> str:
    """Extract readable text from a LangChain message content value."""
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts = []

        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                if item.get("text"):
                    parts.append(str(item["text"]))

        return "".join(parts)

    return str(content)


def ask(question: str) -> dict:
    """
    Ask MetricMind a question and return the final answer
    together with semantic-layer transparency information.
    """

    result = _agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": question,
                }
            ]
        }
    )

    messages = result.get("messages", [])

    transparency = []

    # Collect tool calls and their corresponding tool results.
    for i, message in enumerate(messages):
        tool_calls = getattr(message, "tool_calls", None)

        if not tool_calls:
            continue

        for tool_call in tool_calls:
            tool_call_id = tool_call.get("id")
            tool_name = tool_call.get("name", "")
            tool_input = tool_call.get("args", {})

            observation = {}

            # Find the matching ToolMessage.
            for next_message in messages[i + 1:]:
                if getattr(next_message, "tool_call_id", None) == tool_call_id:
                    observation = _parse_tool_output(
                        getattr(next_message, "content", "")
                    )
                    break

            transparency.append(
                {
                    "tool": tool_name,
                    "tool_input": tool_input,
                    "query": observation.get("query"),
                    "generated_sql": observation.get("generated_sql"),
                    "data": observation.get("data"),
                }
            )

    # The last AI message should contain the final answer.
    answer = ""

    for message in reversed(messages):
        if getattr(message, "type", None) == "ai":
            answer = _message_text(getattr(message, "content", ""))
            if answer:
                break

    return {
        "answer": answer,
        "transparency": transparency,
    }