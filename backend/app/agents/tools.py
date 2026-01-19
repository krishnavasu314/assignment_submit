import json
from datetime import datetime
from typing import Any, Optional

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from sqlalchemy.orm import Session

from app.db import models


SUMMARY_PROMPT = SystemMessage(
    content=(
        "You are a life sciences CRM assistant. Extract a concise summary and key entities "
        "from HCP interaction notes. Return strict JSON with keys: summary, products_discussed, "
        "sentiment, outcomes, next_steps, attendees. Use arrays for products_discussed."))

COMPLIANCE_PROMPT = SystemMessage(
    content=(
        "You are a medical compliance reviewer for field interactions. Identify potential risks "
        "(off-label claims, safety omissions, or unbalanced benefit statements). Return strict JSON "
        "with keys: risk_level (low|medium|high), issues (array), suggested_remediation."))


def _safe_json_loads(text: str) -> dict[str, Any]:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {}


def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def build_tools(session: Session, llm, default_hcp_id: Optional[int] = None):
    def _resolve_hcp_id(hcp_id: Optional[int]) -> Optional[int]:
        return hcp_id if hcp_id is not None else default_hcp_id

    @tool("fetch_hcp_profile")
    def fetch_hcp_profile(hcp_id: Optional[int] = None) -> dict[str, Any]:
        """Fetch HCP profile details with recent interactions."""
        resolved_hcp_id = _resolve_hcp_id(hcp_id)
        if resolved_hcp_id is None:
            return {"error": "HCP id is required"}

        hcp = session.query(models.HCP).filter(models.HCP.id == resolved_hcp_id).first()
        if not hcp:
            return {"error": "HCP not found"}

        interactions = (
            session.query(models.Interaction)
            .filter(models.Interaction.hcp_id == resolved_hcp_id)
            .order_by(models.Interaction.interaction_date.desc().nullslast())
            .limit(3)
            .all()
        )

        return {
            "hcp": {
                "id": hcp.id,
                "name": hcp.name,
                "specialty": hcp.specialty,
                "organization": hcp.organization,
                "city": hcp.city,
                "state": hcp.state,
                "tier": hcp.tier,
            },
            "recent_interactions": [
                {
                    "id": interaction.id,
                    "summary": interaction.summary,
                    "interaction_date": interaction.interaction_date.isoformat() if interaction.interaction_date else None,
                    "sentiment": interaction.sentiment,
                }
                for interaction in interactions
            ],
        }

    @tool("log_interaction")
    def log_interaction(
        raw_notes: str,
        hcp_id: Optional[int] = None,
        interaction_type: Optional[str] = None,
        channel: Optional[str] = None,
        interaction_date: Optional[str] = None,
        attendees: Optional[str] = None,
        outcomes: Optional[str] = None,
        next_steps: Optional[str] = None,
        products_discussed: Optional[list[str]] = None,
        sentiment: Optional[str] = None,
        summary: Optional[str] = None,
    ) -> dict[str, Any]:
        """Log an HCP interaction. If summary or entities are missing, auto-extract them."""
        resolved_hcp_id = _resolve_hcp_id(hcp_id)
        if resolved_hcp_id is None:
            return {"error": "HCP id is required"}

        extracted_entities = None
        if raw_notes and (summary is None or products_discussed is None or sentiment is None):
            response = llm.invoke([SUMMARY_PROMPT, HumanMessage(content=raw_notes)])
            extracted_entities = _safe_json_loads(getattr(response, "content", "") or "")
            summary = summary or extracted_entities.get("summary")
            products_discussed = products_discussed or extracted_entities.get("products_discussed")
            sentiment = sentiment or extracted_entities.get("sentiment")
            outcomes = outcomes or extracted_entities.get("outcomes")
            next_steps = next_steps or extracted_entities.get("next_steps")
            attendees = attendees or extracted_entities.get("attendees")

        interaction = models.Interaction(
            hcp_id=resolved_hcp_id,
            interaction_type=interaction_type,
            channel=channel,
            interaction_date=_parse_datetime(interaction_date),
            summary=summary,
            notes=raw_notes,
            attendees=attendees,
            outcomes=outcomes,
            next_steps=next_steps,
            products_discussed=products_discussed,
            sentiment=sentiment,
            extracted_entities=extracted_entities,
            source="chat",
        )
        session.add(interaction)
        session.commit()
        session.refresh(interaction)
        return {"interaction_id": interaction.id, "summary": interaction.summary}

    @tool("edit_interaction")
    def edit_interaction(
        interaction_id: int,
        summary: Optional[str] = None,
        notes: Optional[str] = None,
        outcomes: Optional[str] = None,
        next_steps: Optional[str] = None,
        products_discussed: Optional[list[str]] = None,
        sentiment: Optional[str] = None,
    ) -> dict[str, Any]:
        """Edit an existing interaction record."""
        interaction = (
            session.query(models.Interaction)
            .filter(models.Interaction.id == interaction_id)
            .first()
        )
        if not interaction:
            return {"error": "Interaction not found"}

        if summary is not None:
            interaction.summary = summary
        if notes is not None:
            interaction.notes = notes
        if outcomes is not None:
            interaction.outcomes = outcomes
        if next_steps is not None:
            interaction.next_steps = next_steps
        if products_discussed is not None:
            interaction.products_discussed = products_discussed
        if sentiment is not None:
            interaction.sentiment = sentiment

        session.commit()
        session.refresh(interaction)
        return {"interaction_id": interaction.id, "summary": interaction.summary}

    @tool("suggest_next_best_action")
    def suggest_next_best_action(hcp_id: Optional[int] = None) -> dict[str, Any]:
        """Provide a recommended next action for the rep."""
        resolved_hcp_id = _resolve_hcp_id(hcp_id)
        if resolved_hcp_id is None:
            return {"error": "HCP id is required"}

        hcp = session.query(models.HCP).filter(models.HCP.id == resolved_hcp_id).first()
        if not hcp:
            return {"error": "HCP not found"}

        last_interaction = (
            session.query(models.Interaction)
            .filter(models.Interaction.hcp_id == resolved_hcp_id)
            .order_by(models.Interaction.interaction_date.desc().nullslast())
            .first()
        )
        context = {
            "hcp": {
                "name": hcp.name,
                "specialty": hcp.specialty,
                "organization": hcp.organization,
                "tier": hcp.tier,
            },
            "last_interaction": {
                "summary": last_interaction.summary if last_interaction else None,
                "outcomes": last_interaction.outcomes if last_interaction else None,
                "next_steps": last_interaction.next_steps if last_interaction else None,
            },
        }
        response = llm.invoke(
            [
                SystemMessage(
                    content=(
                        "You are a CRM assistant. Suggest a concise next best action for a rep "
                        "based on the HCP context. Respond in 2-3 sentences.")),
                HumanMessage(content=json.dumps(context)),
            ]
        )
        return {"recommendation": getattr(response, "content", "")}

    @tool("check_compliance")
    def check_compliance(raw_notes: str, products_discussed: Optional[list[str]] = None) -> dict[str, Any]:
        """Check compliance risks in the interaction notes."""
        payload = {
            "notes": raw_notes,
            "products_discussed": products_discussed or [],
        }
        response = llm.invoke([COMPLIANCE_PROMPT, HumanMessage(content=json.dumps(payload))])
        return _safe_json_loads(getattr(response, "content", "") or "")

    return [
        fetch_hcp_profile,
        log_interaction,
        edit_interaction,
        suggest_next_best_action,
        check_compliance,
    ]
