"""
Owner: Member 4 (AI / Agent Engineer)
Wires the LLM + the single semantic-layer tool into a LangChain agent.
"""
import os
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from app.agent.prompts import SYSTEM_PROMPT
from app.agent.tools import query_semantic_layer_tool

_llm = ChatAnthropic(
    model=os.getenv("AGENT_MODEL", "claude-sonnet-4-6"),
    temperature=0,
    anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
)

_prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{input}"),
    MessagesPlaceholder("agent_scratchpad"),
])

_tools = [query_semantic_layer_tool]

_agent = create_tool_calling_agent(_llm, _tools, _prompt)

executor = AgentExecutor(
    agent=_agent,
    tools=_tools,
    max_iterations=6,
    return_intermediate_steps=True,
    verbose=os.getenv("AGENT_VERBOSE", "false").lower() == "true",
)


def ask(question: str) -> dict:
    result = executor.invoke({"input": question})

    transparency = []
    for action, observation in result.get("intermediate_steps", []):
        transparency.append({
            "tool": action.tool,
            "tool_input": action.tool_input,
            "query": observation.get("query") if isinstance(observation, dict) else None,
            "generated_sql": observation.get("generated_sql") if isinstance(observation, dict) else None,
            "data": observation.get("data") if isinstance(observation, dict) else None,
        })

    return {
        "answer": result["output"],
        "transparency": transparency,
    }