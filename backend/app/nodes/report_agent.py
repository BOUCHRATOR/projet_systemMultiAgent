import os
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field
from typing import List
from dotenv import load_dotenv

from app.state import MedicalState

from app.prompts import final_report_prompt

load_dotenv()

# Schéma Pydantic pour la sortie structurée (Validation du Bonus)
class MedicalReportSchema(BaseModel):
    summary: str = Field(description="Synthèse clinique préliminaire basée sur les échanges.")
    urgency_level: str = Field(description="Niveau d'urgence calculé ou réévalué : Bénin, Modéré, ou Red Flags (Urgent).")
    interim_care: str = Field(description="Recommandations intermédiaires et soins d'attente initiaux.")
    physician_instructions: str = Field(description="Conduite à tenir, prescriptions et traitement dictés par le médecin.")
    final_recommendations: List[str] = Field(description="Conseils de suivi personnalisés et hygiène de vie pour le patient.")
    disclaimer: str = Field(
        default="Ce système ne remplace pas une consultation médicale.",
        description="Clause de non-responsabilité éthique obligatoire selon le cahier des charges."
    )

# Configuration du LLM
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.1)

def report_agent(state: MedicalState) -> MedicalState:
    """
    Nœud du rapport final (Fatima).
    Compile l'intégralité de la session et applique la validation Pydantic.
    """
    # Liaison du LLM avec la structure Pydantic
    structured_llm = llm.with_structured_output(MedicalReportSchema)
    
    # Création de la chaîne d'exécution (Syntaxe LCEL)
    chain = final_report_prompt | structured_llm
    
    # Appel de la chaîne en injectant les variables d'état du graphe
    structured_report = chain.invoke({
        "patient_input": state.get("patient_input", ""),
        "diagnostic_summary": state.get("diagnostic_summary", ""),
        "interim_care": state.get("interim_care", ""),
        "physician_treatment": state.get("physician_treatment", "Non spécifié"),
        "physician_notes": state.get("physician_notes", "Aucune note additionnelle"),
        "conversation_history": str(state.get("messages", []))
    })
    
    # Enregistrement du rapport converti en dictionnaire dans l'état global
    state["final_report"] = structured_report.model_dump() # type: ignore
    
    return state