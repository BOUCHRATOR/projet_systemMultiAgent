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
    physician_treatment: str
    physician_notes: str
    physician_validated: bool
    awaiting_physician_review: bool
    final_report: str
    next: str


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
        "physician_treatment": "",
        "physician_notes": "",
        "physician_validated": False,
        "awaiting_physician_review": False,
        "final_report": "",
        "next": "diagnostic_agent",
    }