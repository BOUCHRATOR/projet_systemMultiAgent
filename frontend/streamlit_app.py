import base64
import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="Medical AI Consultation",
    page_icon="🩺",
    layout="wide"
)

st.title("🩺 Consultation médicale IA")
st.write("Consultation initiale patient")

# --- INITIALISATION DES ÉTATS DE SESSION (STREAMLIT SESSION STATE) ---
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

if "final_report" not in st.session_state:
    st.session_state.final_report = None


# --- FONCTION DE GÉNÉRATION DU MODÈLE PRINT/PDF EN HTML ---
def generer_html_rapport(report, session_id):
    recs = report.get('final_recommendations', [])
    recs_html = "".join([f"<li>{r}</li>" for r in recs]) if isinstance(recs, list) else f"<p>{recs}</p>"
    
    html_content = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #333; margin: 40px; line-height: 1.6; }}
            .header {{ text-align: center; border-bottom: 3px solid #007bff; padding-bottom: 20px; margin-bottom: 30px; }}
            .title {{ color: #007bff; margin: 0; font-size: 28px; text-transform: uppercase; letter-spacing: 1px; }}
            .meta {{ color: #666; font-size: 14px; margin-top: 8px; }}
            .section {{ background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 6px solid #007bff; margin-bottom: 25px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }}
            .section-title {{ color: #007bff; margin-top: 0; font-size: 18px; border-bottom: 1px solid #dee2e6; padding-bottom: 5px; text-transform: uppercase; }}
            .urgency {{ font-weight: bold; color: #dc3545; }}
            .footer {{ text-align: center; margin-top: 50px; font-size: 11px; color: #999; border-top: 1px solid #dee2e6; padding-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1 class="title">🩺 Rapport Médical de Consultation</h1>
            <div class="meta">ID Session : <strong>{session_id}</strong> | Généré via Système Multi-Agents Médical</div>
        </div>
        
        <div class="section">
            <h3 class="section-title">📋 Synthèse Clinique</h3>
            <p>{report.get('summary', '')}</p>
            <p><strong>🚨 Niveau d'urgence calculé :</strong> <span class="urgency">{report.get('urgency_level', 'Bénin')}</span></p>
        </div>
        
        <div class="section" style="border-left-color: #28a745;">
            <h3 class="section-title" style="color: #28a745;">💊 Directives Médicales Officielles</h3>
            <p>{report.get('physician_instructions', 'Aucune consigne spécifique renseignée par le médecin.')}</p>
        </div>
        
        <div class="section" style="border-left-color: #ffc107;">
            <h3 class="section-title" style="color: #ffc107;">🏠 Recommandations d'Hygiène & Suivi</h3>
            <ul>{recs_html}</ul>
        </div>
        
        <div class="footer">
            <p>⚠️ <strong>Clause de non-responsabilité :</strong> {report.get('disclaimer', "Ce document est un compte-rendu d'assistance généré par IA et validé par un professionnel. Il ne remplace pas une consultation physique complète en cas d'aggravation des symptômes.")}</p>
        </div>
        
        <script>window.print();</script>
    </body>
    </html>
    """
    return html_content


# --- BARRE LATÉRALE : HISTORIQUE DES CONSULTATIONS ---
with st.sidebar:
    st.header("📚 Historique Global")
    st.write("Sessions enregistrées en mémoire")
    
    if st.button("🔄 Actualiser l'historique"):
        st.rerun()
        
    try:
        history_response = requests.get(f"{API_URL}/consultation/history")
        if history_response.status_code == 200:
            all_sessions = history_response.json()
            if not all_sessions:
                st.info("Aucune consultation active en mémoire.")
            else:
                for idx, (sess_id, sess_data) in enumerate(all_sessions.items()):
                    status = "✅ Validée" if sess_data.get("physician_validated") else "⏳ En cours"
                    
                    with st.expander(f"Session {idx+1} : {sess_id[:8]}... ({status})"):
                        st.markdown(f"**Patient :** {sess_data.get('patient_input', '')[:50]}...")
                        st.markdown(f"**Urgence :** {sess_data.get('urgency_level', 'Non défini')}")
                        
                        if sess_data.get("final_report"):
                            st.success("📄 Rapport généré")
                            if st.button("Charger ce rapport", key=f"load_{sess_id}"):
                                st.session_state.session_id = sess_id
                                st.session_state.messages = sess_data.get("messages", [])
                                st.session_state.is_complete = sess_data.get("is_complete", True)
                                st.session_state.diagnostic_summary = sess_data.get("diagnostic_summary", "")
                                st.session_state.interim_care = sess_data.get("interim_care", "")
                                st.session_state.urgency_level = sess_data.get("urgency_level", "")
                                st.session_state.physician_validated = sess_data.get("physician_validated", True)
                                st.session_state.physician_treatment = sess_data.get("physician_treatment", "")
                                st.session_state.physician_notes = sess_data.get("physician_notes", "")
                                st.session_state.final_report = sess_data.get("final_report")
                                st.rerun()
        else:
            st.error("Impossible de récupérer l'historique.")
    except Exception as e:
        st.error(f"Erreur de connexion backend : {e}")


# --- ÉCRAN D'ACCUEIL : Saisie des symptômes initiaux ---
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


# --- ÉCRAN DE CONSULTATION ACTIVE (CHAT, VALIDATION ET RAPPORT) ---
else:
    # Création dynamique de la structure en colonnes si le médecin a validé
    if st.session_state.physician_validated:
        col_left, col_right = st.columns(2)
    else:
        col_left = st.container()
        col_right = None

    # --- COLONNE GAUCHE : Interface de Chat et Formulaire Médecin ---
    with col_left:
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

    # --- COLONNE DROITE : AFFICHAGE DU RAPPORT FINAL STRUCTURÉ ET EXPORT PDF ---
    # Imbriqué correctement à l'intérieur du grand bloc 'else:' global
    if col_right is not None:
        with col_right:
            st.subheader("📄 Rapport Médical Final Structuré")
            
            if not st.session_state.final_report:
                with st.spinner("Génération du rapport Pydantic en cours..."):
                    report_resp = requests.get(f"{API_URL}/consultation/{st.session_state.session_id}/report")
                    if report_resp.status_code == 200:
                        st.session_state.final_report = report_resp.json()
                        st.rerun()
            
            if st.session_state.final_report:
                report = st.session_state.final_report
                
                st.markdown(
                    f"""
                    <div style="background-color:#f8f9fa; padding:15px; border-radius:10px; border-left: 5px solid #007bff; margin-bottom:10px;">
                        <h4 style="color:#007bff; margin:0;">📋 Synthèse Clinique</h4>
                        <p style="color:#333; margin-top:5px;">{report.get('summary', '')}</p>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
                
                urgency = report.get('urgency_level', 'Bénin')
                color = "#dc3545" if "Red" in urgency or "Urgent" in urgency else ("#ffc107" if "Modéré" in urgency else "#28a745")
                st.markdown(f"**🚨 Niveau d'urgence calculé :** <span style='color:{color}; font-weight:bold;'>{urgency}</span>", unsafe_allow_html=True)
                
                st.markdown("---")
                st.markdown("### 💊 Directives Médicales Officielles")
                st.write(report.get('physician_instructions', ''))
                
                st.markdown("### 🏠 Recommandations d'hygiène & Suivi")
                recs = report.get('final_recommendations', [])
                if isinstance(recs, list):
                    for r in recs:
                        st.markdown(f"- {r}")
                else:
                    st.write(recs)
                    
                st.markdown("---")
                st.caption(f"⚠️ **Clause de non-responsabilité :** {report.get('disclaimer', 'Ce système ne remplace pas une consultation médicale.')}")
                
                # --- SECTION EXPORTATION PDF VIA INTERFACE D'IMPRESSION ---
                st.markdown("### 📥 Télécharger le document")
                html_rapport = generer_html_rapport(report, st.session_state.session_id)
                
                # Encodage en base64 pour permettre le téléchargement d'un fichier HTML exécutable (bouton d'impression automatique)
                b64 = base64.b64encode(html_rapport.encode('utf-8')).decode()
                filename = f"Rapport_Medical_{st.session_state.session_id[:8]}.html"
                
                download_href = f"""
                    <a href="data:text/html;base64,{b64}" download="{filename}" style="text-decoration:none;">
                        <button style="background-color:#28a745; color:white; padding:12px 20px; border:none; border-radius:6px; cursor:pointer; font-size:16px; font-weight:bold; width:100%; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                            🖨️ Sauvegarder / Exporter en PDF
                        </button>
                    </a>
                """
                st.markdown(download_href, unsafe_allow_html=True)
                st.caption("💡 _Clique sur le bouton pour télécharger le rapport. Ouvre ensuite le fichier téléchargé, la fenêtre d'impression s'ouvrira toute seule pour l'enregistrer au format PDF._")