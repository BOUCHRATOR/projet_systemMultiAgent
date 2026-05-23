# Medical AI Consultation System

Projet intelligent de consultation médicale basé sur :

* LangGraph
* FastAPI
* Streamlit
* Groq LLM

##  Description du projet

Cette application permet de :

1. Saisir les symptômes initiaux d’un patient
2. Générer automatiquement des questions médicales
3. Réaliser une consultation IA structurée
4. Générer un résumé médical initial
5. Fournir des recommandations intermédiaires

Ce système ne remplace pas un médecin professionnel.

---

# Architecture du projet

```bash
project/
├── backend/
│   ├── app/
│   │   ├── api.py
│   │   ├── state.py
│   │   ├── graph.py
│   │   ├── prompts.py
│   │   ├── nodes/
│   │   │   └── diagnostic_agent.py
│   │   └── tools/
│   │       ├── patient_tools.py
│   │       └── care_tools.py
│   └── requirements.txt
│
├── frontend/
│   └── streamlit_app.py
│
└── README.md
```

---

# Installation

## Cloner le projet

```bash
git clone <repo_url>
cd projet
```

---

##  Créer un environnement virtuel avec uv

```bash
uv venv
```

---

##  Activer l’environnement

### Windows CMD

```bash
.venv\Scripts\activate
```
---

## 4. Installer les dépendances

```bash
uv add fastapi uvicorn streamlit langgraph langchain langchain-core langchain-groq python-dotenv pydantic requests
```

---

# Configuration API

Créer un fichier `.env` à la racine du projet :

```env
GROQ_API_KEY=votre_cle_api_groq
```

---

# Lancement du Backend

Aller dans le dossier backend :

```bash
cd backend
```

Lancer FastAPI :

```bash
uv run uvicorn app.api:app --reload --port 8000
```

Le backend sera disponible sur :

```text
http://127.0.0.1:8000
```

---

# Lancement du Frontend

Ouvrir un nouveau terminal :

```bash
cd frontend
```

Lancer Streamlit :

```bash
uv run streamlit run streamlit_app.py
```

Le frontend sera disponible sur :

```text
http://localhost:8501
```

---

#  Technologies utilisées

* Python
* FastAPI
* Streamlit
* LangGraph
* LangChain
* Groq API
* Pydantic

---

#  Répartition des tâches

## Bouchra

* Consultation IA patient
* DiagnosticAgent
* Questions dynamiques
* Backend consultation
* Frontend chatbot

## Abdellah

* Supervision médicale
* Workflow LangGraph
* Validation médecin

## Fatima

* Rapport final
* Historique consultations
* Export des données

---

# Mention légale

Ce système est un prototype académique basé sur l’intelligence artificielle.
Il ne remplace pas un avis médical professionnel.
