import json
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from app.state import MedicalState
from app.prompts import next_question_prompt

load_dotenv()
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0
)


def format_conversation(messages: list) -> str:
    lines = []

    for msg in messages:
        role = "Patient" if msg["role"] == "user" else "Assistant"
        lines.append(f"{role} : {msg['content']}")

    return "\n".join(lines)


def ask_patient(state: MedicalState, patient_answer: str) -> MedicalState:
    updated_messages = state["messages"] + [
        {
            "role": "user",
            "content": patient_answer,
        }
    ]

    new_count = state["question_count"] + 1

    if new_count < 5:
        conversation_history = format_conversation(updated_messages)

        chain = next_question_prompt | llm

        response = chain.invoke({
            "question_count": new_count,
            "conversation_history": conversation_history,
            "next_question_number": new_count + 1,
        })

        try:
            parsed = json.loads(response.content)
            next_question = parsed.get(
                "next_question",
                "Pouvez-vous donner plus de détails sur vos symptômes ?"
            )
        except json.JSONDecodeError:
            next_question = response.content.strip()

        updated_messages.append({
            "role": "assistant",
            "content": next_question,
        })

        return {
            **state,
            "messages": updated_messages,
            "question_count": new_count,
            "current_question": next_question,
        }

    return {
        **state,
        "messages": updated_messages,
        "question_count": new_count,
        "current_question": "",
    }