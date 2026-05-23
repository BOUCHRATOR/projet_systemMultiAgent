import json
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from app.state import MedicalState
from app.prompts import symptom_analysis_prompt

load_dotenv()
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0
)


def diagnostic_agent(state: MedicalState) -> MedicalState:
    chain = symptom_analysis_prompt | llm

    response = chain.invoke({
        "patient_input": state["patient_input"]
    })

    try:
        parsed = json.loads(response.content)
        first_question = parsed.get(
            "first_question",
            "Pouvez-vous préciser vos symptômes principaux ?"
        )
    except json.JSONDecodeError:
        first_question = response.content.strip()

    return {
        **state,
        "current_question": first_question,
        "messages": state["messages"] + [
            {
                "role": "assistant",
                "content": first_question,
            }
        ],
    }