from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.db import models
from app.routers import agent, hcps, interactions


app = FastAPI(title="AI-First CRM HCP Module")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        if session.query(models.HCP).count() == 0:
            session.add_all(
                [
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
            )
            session.commit()
    finally:
        session.close()


@app.get("/")
def root():
    return {"status": "ok", "service": "hcp-crm"}


app.include_router(hcps.router)
app.include_router(interactions.router)
app.include_router(agent.router)
