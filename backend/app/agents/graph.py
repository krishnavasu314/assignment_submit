from typing import Annotated, TypedDict

from langchain_core.messages import SystemMessage
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_groq import ChatGroq

from app.agents.tools import build_tools
from app.config import settings


SYSTEM_MESSAGE = SystemMessage(
    content=(
        "You are an AI-first CRM assistant for life sciences field reps. "
        "Prefer tool usage when logging, editing, or reviewing HCP interactions. "
        "Ask clarifying questions when required fields are missing."
    )
)


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


def build_agent(session, model_override: str | None = None):
    model_name = model_override or settings.groq_model
    llm = ChatGroq(api_key=settings.groq_api_key, model_name=model_name)
    tools = build_tools(session, llm)
    llm_with_tools = llm.bind_tools(tools)

    def assistant(state: AgentState):
        response = llm_with_tools.invoke([SYSTEM_MESSAGE] + state["messages"])
        return {"messages": [response]}

    graph = StateGraph(AgentState)
    graph.add_node("assistant", assistant)
    graph.add_node("tools", ToolNode(tools))
    graph.add_conditional_edges("assistant", tools_condition)
    graph.add_edge("tools", "assistant")
    graph.set_entry_point("assistant")
    return graph.compile()
