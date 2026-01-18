# AI-First CRM HCP Module - Log Interaction Screen

This repository contains a minimal full-stack prototype for the Log Interaction Screen of an AI-first CRM designed for life sciences field reps. Users can log HCP interactions via a structured form or a conversational assistant powered by LangGraph and Groq LLMs (default: `gemma2-9b-it`).

## Tech Stack
- Frontend: React + Redux Toolkit (Vite)
- Backend: Python + FastAPI
- AI Agent: LangGraph
- LLM Provider: Groq (model: `gemma2-9b-it`, optional `llama-3.3-70b-versatile`)
- Database: Postgres or MySQL via SQLAlchemy
- Font: Google Inter

## Architecture Overview
- Structured Log: Form data is posted to `/interactions`, with optional AI summarization of raw notes.
- Conversational Log: `/agent/chat` routes messages to a LangGraph agent that can invoke tools to log or edit interactions using the selected HCP context.
- Persistence: HCPs and interactions are stored in SQL tables.

## LangGraph Agent Role
The LangGraph agent serves as the reasoning layer that:
- Interprets user intent in conversational chat.
- Chooses between tools (log, edit, compliance review, etc.).
- Summarizes raw notes and extracts entities to keep CRM fields structured.
- Suggests next-best actions based on recent interactions.

### Tools (Minimum 5)
1. Log Interaction (`log_interaction`)
   - Captures raw notes, invokes the LLM for summarization + entity extraction, and writes a structured interaction record.
2. Edit Interaction (`edit_interaction`)
   - Updates existing records for corrections or follow-ups.
3. Fetch HCP Profile (`fetch_hcp_profile`)
   - Pulls HCP info + recent interactions for context.
4. Suggest Next Best Action (`suggest_next_best_action`)
   - Uses the LLM to propose next steps based on interaction history.
5. Check Compliance (`check_compliance`)
   - Flags potential compliance risks (for example, off-label claims, safety omissions).

## Backend Setup
```bash
cd backend
python -m venv .venv
. .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env` from `.env.example` and set:
```bash
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/hcp_crm
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=gemma2-9b-it
```

Run the API:
```bash
uvicorn app.main:app --reload
```

## Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

The UI runs on `http://localhost:5173` and calls the FastAPI server at `http://localhost:8000`.

## API Endpoints
- `GET /hcps` - list HCPs
- `POST /hcps/seed` - seed sample HCPs
- `GET /interactions?hcp_id=...` - list interactions
- `POST /interactions` - create interaction (structured form)
- `PUT /interactions/{id}` - edit interaction
- `POST /agent/chat` - LangGraph agent chat interface

## Demo Tips
- Seed HCPs via the Seed sample HCPs button.
- Use the structured form to log a detailed visit.
- In chat, try: "Log a follow-up with Dr. Iyer about adverse event monitoring."

## Notes
- The video instructions link is not accessible from this environment; follow it separately when recording your walkthrough.
