from langgraph.graph import StateGraph, END

from app.state import MedicalState
from app.nodes.diagnostic_agent import diagnostic_agent
from app.tools.care_tools import recommend_interim_care


def build_graph():
    builder = StateGraph(MedicalState)

    builder.add_node("diagnostic_agent", diagnostic_agent)
    builder.add_node("recommend_interim_care", recommend_interim_care)

    builder.set_entry_point("diagnostic_agent")

    builder.add_edge("diagnostic_agent", END)
    builder.add_edge("recommend_interim_care", END)

    return builder.compile()


graph = build_graph()