import json
from typing import Optional

from fastapi import APIRouter, Depends
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from sqlalchemy.orm import Session

from app.agents.graph import build_agent
from app.db.session import get_session
from app.schemas import AgentChatRequest, AgentChatResponse, AgentMessage


router = APIRouter(prefix="/agent", tags=["agent"])


def _extract_interaction_id(messages: list) -> Optional[int]:
    for message in messages:
        if isinstance(message, ToolMessage):
            try:
                payload = json.loads(message.content)
            except json.JSONDecodeError:
                continue
            if isinstance(payload, dict) and "interaction_id" in payload:
                return payload["interaction_id"]
    return None


def _serialize_message(message) -> AgentMessage:
    if isinstance(message, HumanMessage):
        return AgentMessage(role="user", content=message.content)
    if isinstance(message, AIMessage):
        return AgentMessage(role="assistant", content=message.content or "", tool_calls=message.tool_calls)
    if isinstance(message, ToolMessage):
        return AgentMessage(role="tool", content=message.content)
    return AgentMessage(role="assistant", content=str(message))


@router.post("/chat", response_model=AgentChatResponse)
def chat(payload: AgentChatRequest, session: Session = Depends(get_session)):
    agent = build_agent(session, model_override=payload.model)
    result = agent.invoke({"messages": [HumanMessage(content=payload.message)]})
    messages = result.get("messages", [])
    interaction_id = _extract_interaction_id(messages)
    return AgentChatResponse(
        messages=[_serialize_message(message) for message in messages],
        interaction_id=interaction_id,
    )
