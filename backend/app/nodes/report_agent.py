from langchain_groq import ChatGroq
from pydantic import BaseModel, Field
from typing import List
from dotenv import load_dotenv
from app.state import MedicalState

load_dotenv()

# Bonus Pydantic : Structure parfaite demandée par le cahier des charges
class MedicalReportSchema(BaseModel):
    summary: str = Field(description="Synthèse clinique préliminaire basée sur les échanges.")
    urgency_level: str = Field(description="Niveau d'urgence calculé : Bénin, Modéré, ou Red Flags (Urgent).")
    interim_care: str = Field(description="Recommandations intermédiaires (ex: hydratation, repos).")
    physician_instructions: str = Field(description="Conduite à tenir et traitement dictés par le médecin.")
    final_recommendations: List[str] = Field(description="Conseils de suivi et d'hygiène de vie pour le patient.")
    disclaimer: str = Field(
        default="Ce système ne remplace pas une consultation médicale.",
        description="Clause de non-responsabilité éthique obligatoire."
    )

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.1)

def report_agent(state: MedicalState) -> MedicalState:
    # On active la sortie structurée Pydantic
    structured_llm = llm.with_structured_output(MedicalReportSchema)
    
    # On prépare les données issues du State commun
    prompt = f"""Tu es un expert en documentation médicale. Tu dois compiler toutes les informations recueillies pour générer le rapport final structuré.
    
    Symptômes initiaux : {state['patient_input']}
    Synthèse diagnostique précédente : {state['diagnostic_summary']}
    Recommandations intermédiaires : {state['interim_care']}
    Traitement / Instructions du médecin traitant : {state.get('physician_treatment', 'Non spécifié')}
    Historique complet des messages : {state['messages']}
    
    Génère le rapport final en respectant scrupuleusement la structure demandée."""
    
    # Appel au LLM
    structured_report = structured_llm.invoke(prompt)
    
    # On retourne le state mis à jour avec le dictionnaire du rapport
    return {
        **state,
        "final_report": structured_report.model_dump()  # .dict() sous Pydantic v1
    }