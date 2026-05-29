from app.state import MedicalState


def physician_review(state: MedicalState) -> MedicalState:
    """
    Human-in-the-Loop node.

    This node does not generate a medical decision automatically.
    It only marks the consultation as waiting for a physician review.

    The real physician input will come later from the FastAPI endpoint.
    """

    state["awaiting_physician_review"] = True
    state["physician_validated"] = False

    # The doctor still has not entered the treatment / conduite à tenir
    if not state.get("physician_treatment"):
        state["physician_treatment"] = ""

    if not state.get("physician_notes"):
        state["physician_notes"] = ""

    return state