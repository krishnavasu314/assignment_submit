import json
from typing import Annotated, TypedDict

from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_groq import ChatGroq

from app.agents.tools import build_tools
from app.config import settings


BASE_SYSTEM_PROMPT = (
    "You are an AI-first CRM assistant for life sciences field reps. "
    "Prefer tool usage when logging, editing, or reviewing HCP interactions. "
    "Ask clarifying questions when required fields are missing."
)


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


def build_agent(
    session,
    model_override: str | None = None,
    default_hcp_id: int | None = None,
    hcp_context: dict | None = None,
):
    model_name = model_override or settings.groq_model
    llm = ChatGroq(api_key=settings.groq_api_key, model_name=model_name)
    tools = build_tools(session, llm, default_hcp_id=default_hcp_id)
    llm_with_tools = llm.bind_tools(tools)
    system_content = BASE_SYSTEM_PROMPT
    if hcp_context:
        system_content = (
            f"{system_content} Active HCP context: {json.dumps(hcp_context)}. "
            "Use this HCP by default unless the user specifies a different one."
        )
    system_message = SystemMessage(content=system_content)

    def assistant(state: AgentState):
        response = llm_with_tools.invoke([system_message] + state["messages"])
        return {"messages": [response]}

    graph = StateGraph(AgentState)
    graph.add_node("assistant", assistant)
    graph.add_node("tools", ToolNode(tools))
    graph.add_conditional_edges("assistant", tools_condition)
    graph.add_edge("tools", "assistant")
    graph.set_entry_point("assistant")
    return graph.compile()
