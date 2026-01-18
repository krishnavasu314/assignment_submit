from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import models
from app.db.session import get_session
from app.schemas import HCPCreate, HCPOut


router = APIRouter(prefix="/hcps", tags=["hcps"])


@router.get("", response_model=list[HCPOut])
def list_hcps(session: Session = Depends(get_session)):
    return session.query(models.HCP).order_by(models.HCP.name).all()


@router.post("", response_model=HCPOut)
def create_hcp(payload: HCPCreate, session: Session = Depends(get_session)):
    hcp = models.HCP(**payload.model_dump())
    session.add(hcp)
    session.commit()
    session.refresh(hcp)
    return hcp


@router.post("/seed", response_model=list[HCPOut])
def seed_hcps(session: Session = Depends(get_session)):
    existing = session.query(models.HCP).count()
    if existing:
        return session.query(models.HCP).order_by(models.HCP.name).all()

    seed_data = [
        models.HCP(
            name="Dr. Anaya Iyer",
            specialty="Cardiology",
            organization="Northbridge Medical Center",
            city="Pune",
            state="MH",
            tier="A",
        ),
        models.HCP(
            name="Dr. Kunal Mehta",
            specialty="Endocrinology",
            organization="Sunrise Hospitals",
            city="Ahmedabad",
            state="GJ",
            tier="B",
        ),
    ]
    session.add_all(seed_data)
    session.commit()
    return session.query(models.HCP).order_by(models.HCP.name).all()
