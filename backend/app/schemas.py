from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class HCPBase(BaseModel):
    name: str
    specialty: Optional[str] = None
    organization: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    tier: Optional[str] = None


class HCPCreate(HCPBase):
    pass


class HCPOut(HCPBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class InteractionBase(BaseModel):
    hcp_id: int
    interaction_type: Optional[str] = None
    channel: Optional[str] = None
    interaction_date: Optional[datetime] = None
    summary: Optional[str] = None
    notes: Optional[str] = None
    attendees: Optional[str] = None
    outcomes: Optional[str] = None
    next_steps: Optional[str] = None
    products_discussed: Optional[List[str]] = None
    sentiment: Optional[str] = None
    extracted_entities: Optional[dict[str, Any]] = None
    source: Optional[str] = None


class InteractionCreate(InteractionBase):
    raw_notes: Optional[str] = None


class InteractionUpdate(BaseModel):
    interaction_type: Optional[str] = None
    channel: Optional[str] = None
    interaction_date: Optional[datetime] = None
    summary: Optional[str] = None
    notes: Optional[str] = None
    attendees: Optional[str] = None
    outcomes: Optional[str] = None
    next_steps: Optional[str] = None
    products_discussed: Optional[List[str]] = None
    sentiment: Optional[str] = None
    extracted_entities: Optional[dict[str, Any]] = None


class InteractionOut(InteractionBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AgentChatRequest(BaseModel):
    hcp_id: Optional[int] = None
    message: str
    conversation_id: Optional[str] = None
    model: Optional[str] = None


class AgentMessage(BaseModel):
    role: str
    content: str
    tool_calls: Optional[List[dict[str, Any]]] = None


class AgentChatResponse(BaseModel):
    messages: List[AgentMessage]
    interaction_id: Optional[int] = None
