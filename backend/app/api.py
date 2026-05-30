import uuid
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.state import MedicalState, initial_state
from app.nodes.diagnostic_agent import diagnostic_agent
from app.tools.patient_tools import ask_patient
from app.tools.care_tools import recommend_interim_care

from app.nodes.report_agent import report_agent


app = FastAPI(
    title="Medical AI",
    version="1.0.0"
)


sessions: dict[str, MedicalState] = {}


class StartRequest(BaseModel):
    patient_input: str


class StartResponse(BaseModel):
    session_id: str
    first_question: str


class AnswerRequest(BaseModel):
    session_id: str
    patient_answer: str


class AnswerResponse(BaseModel):
    session_id: str
    next_question: str | None
    diagnostic_summary: str | None
    interim_care: str | None
    urgency_level: str | None
    is_complete: bool


@app.post("/consultation/start", response_model=StartResponse)
async def start_consultation(body: StartRequest):
    session_id = str(uuid.uuid4())

    state = initial_state(
        session_id=session_id,
        patient_input=body.patient_input
    )

    state = diagnostic_agent(state)

    sessions[session_id] = state

    return StartResponse(
        session_id=session_id,
        first_question=state["current_question"],
    )


@app.post("/consultation/answer", response_model=AnswerResponse)
async def answer_question(body: AnswerRequest):
    state = sessions.get(body.session_id)

    if not state:
        raise HTTPException(
            status_code=404,
            detail="Session introuvable."
        )

    if state["is_complete"]:
        return AnswerResponse(
            session_id=body.session_id,
            next_question=None,
            diagnostic_summary=state["diagnostic_summary"],
            interim_care=state["interim_care"],
            urgency_level=state["urgency_level"],
            is_complete=True,
        )

    state = ask_patient(state, body.patient_answer)

    if state["question_count"] >= 5:
        state = recommend_interim_care(state)

    sessions[body.session_id] = state

    return AnswerResponse(
        session_id=body.session_id,
        next_question=state["current_question"] if not state["is_complete"] else None,
        diagnostic_summary=state["diagnostic_summary"] if state["is_complete"] else None,
        interim_care=state["interim_care"] if state["is_complete"] else None,
        urgency_level=state["urgency_level"] if state["is_complete"] else None,
        is_complete=state["is_complete"],
    )


@app.get("/consultation/state/{session_id}")
async def get_state(session_id: str):
    state = sessions.get(session_id)

    if not state:
        raise HTTPException(
            status_code=404,
            detail="Session introuvable."
        )

    return state

# Route pour récupérer le rapport final ou le générer s'il n'existe pas encore
@app.get("/consultation/{session_id}/report")
async def get_consultation_report(session_id: str):
    state = sessions.get(session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Session introuvable.")
    
    # Si le rapport n'a pas encore été généré par le workflow, on appelle ton agent
    if not state.get("final_report"):
        state = report_agent(state)
        sessions[session_id] = state  # Sauvegarde dans l'historique mémoire
        
    return state["final_report"]


# Route Bonus : Historique complet de toutes les consultations enregistrées
@app.get("/consultation/history")
async def get_all_history():
    # Renvoie toutes les sessions actives en mémoire pour ton écran Streamlit Historique
    return sessions
