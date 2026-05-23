import json
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from app.state import MedicalState
from app.prompts import interim_care_prompt
from app.tools.patient_tools import format_conversation

load_dotenv()
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0
)


def recommend_interim_care(state: MedicalState) -> MedicalState:
    conversation_history = format_conversation(state["messages"])

    chain = interim_care_prompt | llm

    response = chain.invoke({
        "patient_input": state["patient_input"],
        "conversation_history": conversation_history,
    })

    try:
        parsed = json.loads(response.content)

        diagnostic_summary = parsed.get(
            "diagnostic_summary",
            "Résumé non disponible."
        )

        interim_care = parsed.get(
            "interim_care",
            "Consultez un professionnel de santé pour une évaluation adaptée."
        )

        urgency_level = parsed.get(
            "urgency_level",
            "modéré"
        )

    except json.JSONDecodeError:
        diagnostic_summary = response.content.strip()
        interim_care = "Consultez un professionnel de santé pour confirmer l’évaluation."
        urgency_level = "modéré"

    return {
        **state,
        "diagnostic_summary": diagnostic_summary,
        "interim_care": interim_care,
        "urgency_level": urgency_level,
        "is_complete": True,
    }