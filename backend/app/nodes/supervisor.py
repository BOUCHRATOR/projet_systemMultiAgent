from app.state import MedicalState


def supervisor(state: MedicalState) -> MedicalState:
    """
    SupervisorAgent.

    This node decides the next step of the workflow based on the current state.
    It does not generate medical content.
    It only routes the workflow.
    """

    # If the final report already exists, the workflow can finish
    if state.get("final_report"):
        state["next"] = "FINISH"
        return state

    # If the doctor has validated the consultation, go to the report agent
    if state.get("physician_validated") is True and state.get("physician_treatment"):
        state["next"] = "report_agent"
        return state

    # If the diagnostic summary and interim care are ready,
    # the consultation must wait for physician review
    if state.get("diagnostic_summary") and state.get("interim_care"):
        state["next"] = "physician_review"
        return state

    # Otherwise, continue with the diagnostic agent
    state["next"] = "diagnostic_agent"
    return state


def route_next(state: MedicalState) -> str:
    """
    Conditional routing function used by LangGraph.
    """
    return state["next"]