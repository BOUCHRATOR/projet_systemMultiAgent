from typing import TypedDict, List, Dict, Optional


class MedicalState(TypedDict):
    session_id: str
    patient_input: str
    messages: List[Dict[str, str]]
    question_count: int
    current_question: str
    diagnostic_summary: str
    interim_care: str
    urgency_level: Optional[str]
    is_complete: bool

    final_report: Optional[Dict]  # Pour stocker  rapport Pydantic final
    physician_treatment: Optional[str] # recevoir le traitement proposé par le médecin dans le rapport final (partie d abdellah)


def initial_state(session_id: str, patient_input: str) -> MedicalState:
    return {
        "session_id": session_id,
        "patient_input": patient_input,
        "messages": [],
        "question_count": 0,
        "current_question": "",
        "diagnostic_summary": "",
        "interim_care": "",
        "urgency_level": None,
        "is_complete": False,
        "final_report": None,
        "physician_treatment": None,
    }