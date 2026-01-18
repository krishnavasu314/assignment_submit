import json
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from sqlalchemy.orm import Session

from app.config import settings
from app.db import models
from app.db.session import get_session
from app.schemas import InteractionCreate, InteractionOut, InteractionUpdate


router = APIRouter(prefix="/interactions", tags=["interactions"])

SUMMARY_PROMPT = SystemMessage(
    content=(
        "You are a life sciences CRM assistant. Extract a concise summary and key entities "
        "from HCP interaction notes. Return strict JSON with keys: summary, products_discussed, "
        "sentiment, outcomes, next_steps, attendees. Use arrays for products_discussed."))


def _safe_json_loads(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {}


@router.get("", response_model=list[InteractionOut])
def list_interactions(
    hcp_id: Optional[int] = None,
    session: Session = Depends(get_session),
):
    query = session.query(models.Interaction)
    if hcp_id is not None:
        query = query.filter(models.Interaction.hcp_id == hcp_id)
    return query.order_by(models.Interaction.interaction_date.desc().nullslast()).all()


@router.post("", response_model=InteractionOut)
def create_interaction(payload: InteractionCreate, session: Session = Depends(get_session)):
    extracted_entities = payload.extracted_entities
    summary = payload.summary
    attendees = payload.attendees
    outcomes = payload.outcomes
    next_steps = payload.next_steps
    products_discussed = payload.products_discussed
    sentiment = payload.sentiment

    if payload.raw_notes and not summary:
        llm = ChatGroq(api_key=settings.groq_api_key, model_name=settings.groq_model)
        response = llm.invoke([SUMMARY_PROMPT, HumanMessage(content=payload.raw_notes)])
        extracted_entities = _safe_json_loads(getattr(response, "content", "") or "")
        summary = extracted_entities.get("summary")
        products_discussed = extracted_entities.get("products_discussed")
        sentiment = extracted_entities.get("sentiment")
        outcomes = extracted_entities.get("outcomes")
        next_steps = extracted_entities.get("next_steps")
        attendees = extracted_entities.get("attendees")

    interaction = models.Interaction(
        hcp_id=payload.hcp_id,
        interaction_type=payload.interaction_type,
        channel=payload.channel,
        interaction_date=payload.interaction_date,
        summary=summary,
        notes=payload.notes or payload.raw_notes,
        attendees=attendees,
        outcomes=outcomes,
        next_steps=next_steps,
        products_discussed=products_discussed,
        sentiment=sentiment,
        extracted_entities=extracted_entities,
        source=payload.source or "form",
    )
    session.add(interaction)
    session.commit()
    session.refresh(interaction)
    return interaction


@router.put("/{interaction_id}", response_model=InteractionOut)
def update_interaction(
    interaction_id: int,
    payload: InteractionUpdate,
    session: Session = Depends(get_session),
):
    interaction = session.query(models.Interaction).filter(models.Interaction.id == interaction_id).first()
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(interaction, field, value)

    session.commit()
    session.refresh(interaction)
    return interaction
