from langgraph.graph import StateGraph, START, END

from app.state import MedicalState
from app.nodes.diagnostic_agent import diagnostic_agent
from app.nodes.supervisor import supervisor, route_next
from app.nodes.physician_review import physician_review


from app.nodes.report_agent import report_agent

def build_graph():
    builder = StateGraph(MedicalState)

    # Nodes
    builder.add_node("supervisor", supervisor)
    builder.add_node("diagnostic_agent", diagnostic_agent)
    builder.add_node("physician_review", physician_review)

    builder.add_node("report_agent", report_agent)

    # Entry point
    builder.add_edge(START, "supervisor")

    # Supervisor decides the next step
    builder.add_conditional_edges(
        "supervisor",
        route_next,
        {
            "diagnostic_agent": "diagnostic_agent",
            "physician_review": "physician_review",
            #done
            "report_agent": "report_agent",

            "FINISH": END,
        }
    )

    # These nodes return control to the workflow ending point for now.
    # The patient question loop is still managed by FastAPI in the existing project.
    builder.add_edge("diagnostic_agent", END)
    builder.add_edge("physician_review", END)
    
    builder.add_edge("report_agent", END)

    return builder.compile()


graph = build_graph()