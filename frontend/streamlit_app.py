import requests
import streamlit as st


API_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="Medical AI Consultation",
    page_icon="🩺",
    layout="centered"
)


st.title("🩺 Consultation médicale IA")
st.write("consultation initiale patient")


if "session_id" not in st.session_state:
    st.session_state.session_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "is_complete" not in st.session_state:
    st.session_state.is_complete = False

if "diagnostic_summary" not in st.session_state:
    st.session_state.diagnostic_summary = ""

if "interim_care" not in st.session_state:
    st.session_state.interim_care = ""

if "urgency_level" not in st.session_state:
    st.session_state.urgency_level = ""
    
if "physician_validated" not in st.session_state:
    st.session_state.physician_validated = False

if "physician_treatment" not in st.session_state:
    st.session_state.physician_treatment = ""

if "physician_notes" not in st.session_state:
    st.session_state.physician_notes = ""

if "resume_message" not in st.session_state:
    st.session_state.resume_message = ""


if st.session_state.session_id is None:
    st.subheader("Décrivez vos symptômes")

    patient_input = st.text_area(
        "Symptômes initiaux",
        placeholder="Exemple : J’ai mal à la tête et de la fièvre depuis hier..."
    )

    if st.button("Commencer la consultation"):
        if not patient_input.strip():
            st.warning("Veuillez saisir vos symptômes.")
        else:
            response = requests.post(
                f"{API_URL}/consultation/start",
                json={"patient_input": patient_input}
            )

            if response.status_code == 200:
                data = response.json()

                st.session_state.session_id = data["session_id"]
                st.session_state.messages.append({
                    "role": "user",
                    "content": patient_input
                })
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": data["first_question"]
                })

                st.rerun()
            else:
                st.error("Erreur lors du démarrage de la consultation.")


else:
    st.subheader("Chat Patient")

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.write(msg["content"])
        else:
            with st.chat_message("assistant"):
                st.write(msg["content"])

    if not st.session_state.is_complete:
        patient_answer = st.chat_input("Votre réponse...")

        if patient_answer:
            st.session_state.messages.append({
                "role": "user",
                "content": patient_answer
            })

            response = requests.post(
                f"{API_URL}/consultation/answer",
                json={
                    "session_id": st.session_state.session_id,
                    "patient_answer": patient_answer
                }
            )

            if response.status_code == 200:
                data = response.json()

                if data["is_complete"]:
                    st.session_state.is_complete = True
                    st.session_state.diagnostic_summary = data["diagnostic_summary"]
                    st.session_state.interim_care = data["interim_care"]
                    st.session_state.urgency_level = data["urgency_level"]
                else:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": data["next_question"]
                    })

                st.rerun()
            else:
                st.error("Erreur lors de l’envoi de la réponse.")

    else:
        st.success("Consultation initiale terminée.")

        st.subheader("Résumé médical initial")
        st.write(st.session_state.diagnostic_summary)

        st.subheader("Recommandations intermédiaires")
        st.write(st.session_state.interim_care)

        st.subheader("Niveau d’urgence")
        st.info(st.session_state.urgency_level)

        st.warning(
            "Ce résultat est généré par une IA et ne remplace pas l’avis d’un médecin."
        )
        
        st.divider()

        st.subheader("👨‍⚕️ Validation médecin")

        if not st.session_state.physician_validated:
            physician_treatment = st.text_area(
                "Conduite à tenir / traitement proposé par le médecin",
                placeholder="Exemple : Repos, hydratation, surveillance 48h..."
            )

            physician_notes = st.text_area(
                "Notes du médecin",
                placeholder="Exemple : Cas compatible avec syndrome respiratoire simple, à surveiller."
            )

            if st.button("Valider et reprendre la consultation"):
                if not physician_treatment.strip():
                    st.warning("Veuillez saisir la conduite à tenir.")
                else:
                    review_response = requests.post(
                        f"{API_URL}/consultation/review",
                        json={
                            "session_id": st.session_state.session_id,
                            "physician_treatment": physician_treatment,
                            "physician_notes": physician_notes,
                            "validated": True
                        }
                    )

                    if review_response.status_code == 200:
                        review_data = review_response.json()

                        st.session_state.physician_validated = review_data["physician_validated"]
                        st.session_state.physician_treatment = review_data["physician_treatment"]
                        st.session_state.physician_notes = review_data["physician_notes"]

                        resume_response = requests.post(
                            f"{API_URL}/consultation/resume",
                            json={
                                "session_id": st.session_state.session_id
                            }
                        )

                        if resume_response.status_code == 200:
                            resume_data = resume_response.json()
                            st.session_state.resume_message = resume_data["message"]
                            st.success(st.session_state.resume_message)
                            st.rerun()
                        else:
                            st.error("Erreur lors de la reprise de la consultation.")
                    else:
                        st.error("Erreur lors de la validation médecin.")

        else:
            st.success("Validation médecin effectuée.")

            st.subheader("Conduite à tenir validée")
            st.write(st.session_state.physician_treatment)

            if st.session_state.physician_notes:
                st.subheader("Notes médecin")
                st.write(st.session_state.physician_notes)

            if st.session_state.resume_message:
                st.info(st.session_state.resume_message)

        if st.button("Nouvelle consultation"):
            st.session_state.clear()
            st.rerun()