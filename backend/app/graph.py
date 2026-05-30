from langgraph.graph import StateGraph, START, END

from app.state import MedicalState
from app.nodes.diagnostic_agent import diagnostic_agent
from app.nodes.supervisor import supervisor, route_next
from app.nodes.physician_review import physician_review


def build_graph():
    builder = StateGraph(MedicalState)

    # Nodes
    builder.add_node("supervisor", supervisor)
    builder.add_node("diagnostic_agent", diagnostic_agent)
    builder.add_node("physician_review", physician_review)

    # Entry point
    builder.add_edge(START, "supervisor")

    # Supervisor decides the next step
    builder.add_conditional_edges(
        "supervisor",
        route_next,
        {
            "diagnostic_agent": "diagnostic_agent",
            "physician_review": "physician_review",

            # ReportAgent is not Abdellah's part.
            # For now, we stop here until the report agent is added.
            "report_agent": END,

            "FINISH": END,
        }
    )

    # These nodes return control to the workflow ending point for now.
    # The patient question loop is still managed by FastAPI in the existing project.
    builder.add_edge("diagnostic_agent", END)
    builder.add_edge("physician_review", END)

    return builder.compile()


graph = build_graph()