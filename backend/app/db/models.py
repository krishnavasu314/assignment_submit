from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class HCP(Base):
    __tablename__ = "hcps"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    specialty = Column(String(255), nullable=True)
    organization = Column(String(255), nullable=True)
    city = Column(String(255), nullable=True)
    state = Column(String(255), nullable=True)
    tier = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    interactions = relationship("Interaction", back_populates="hcp")


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    hcp_id = Column(Integer, ForeignKey("hcps.id"), nullable=False, index=True)
    interaction_type = Column(String(100), nullable=True)
    channel = Column(String(100), nullable=True)
    interaction_date = Column(DateTime(timezone=True), nullable=True)
    summary = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    attendees = Column(Text, nullable=True)
    outcomes = Column(Text, nullable=True)
    next_steps = Column(Text, nullable=True)
    products_discussed = Column(JSON, nullable=True)
    sentiment = Column(String(50), nullable=True)
    extracted_entities = Column(JSON, nullable=True)
    source = Column(String(50), nullable=False, default="form")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    hcp = relationship("HCP", back_populates="interactions")
