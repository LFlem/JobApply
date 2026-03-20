import streamlit as st

from utils.auth import get_current_user
from utils.extractor import extract_job_info
from utils.jobs import STATUTS, add_candidature
from utils.scraper import scrape_job_url

CONTRATS = ["CDI", "CDD", "Freelance", "Stage", "Alternance", "Autre"]
TELETRAVAIL = ["Non précisé", "Oui", "Non", "Hybride"]


def _split_tags(raw: str) -> list[str]:
    if not raw:
        return []
    return [token.strip() for token in raw.replace("\n", ",").split(",") if token.strip()]


def _save_payload(payload: dict) -> None:
    current_user = get_current_user()
    if not current_user:
        st.warning("Connecte-toi pour enregistrer une candidature.")
        return

    if not payload.get("titre") or not payload.get("entreprise"):
        st.warning("Le titre et l'entreprise sont obligatoires.")
        return

    try:
        doc_id = add_candidature(payload, current_user["id"])
        st.success(f"Candidature enregistree (ID : `{doc_id}`).")
        st.balloons()
        # Rafraichir l'interface pour mettre a jour le dashboard
        st.sleep(1)
        st.rerun()
    except Exception as e:
        st.error(f"Erreur MongoDB : {e}")


def _job_form(initial: dict, form_key: str, submit_label: str) -> None:
    with st.form(form_key):
        c1, c2 = st.columns(2)
        with c1:
            titre = st.text_input(
                "Intitule du poste *",
                value=initial.get("titre") or "",
                placeholder="Data Analyst, Backend Python, Product Manager...",
            )
            entreprise = st.text_input(
                "Entreprise *",
                value=initial.get("entreprise") or "",
                placeholder="Nom de l'entreprise",
            )
            localisation = st.text_input(
                "Localisation",
                value=initial.get("localisation") or "",
                placeholder="Paris, Lyon, Remote...",
            )

        with c2:
            contrat_detected = initial.get("type_contrat", "Autre")
            contrat_idx = CONTRATS.index(contrat_detected) if contrat_detected in CONTRATS else len(CONTRATS) - 1
            type_contrat = st.selectbox("Type de contrat", CONTRATS, index=contrat_idx)

            tt_detected = initial.get("teletravail", "Non précisé")
            tt_idx = TELETRAVAIL.index(tt_detected) if tt_detected in TELETRAVAIL else 0
            teletravail = st.selectbox("Teletravail", TELETRAVAIL, index=tt_idx)

            salaire = st.text_input(
                "Salaire / Fourchette",
                value=initial.get("salaire") or "",
                placeholder="Ex: 45-55kEUR, TJM 550, Non precise",
            )

        competences = st.text_area(
            "Competences (separees par virgules)",
            value=", ".join(initial.get("competences") or []),
            placeholder="Python, SQL, Docker, FastAPI...",
            height=90,
        )
        avantages = st.text_area(
            "Avantages (separes par virgules)",
            value=", ".join(initial.get("avantages") or []),
            placeholder="RTT, mutuelle, BSPCE, formation...",
            height=75,
        )
        description = st.text_area(
            "Description courte",
            value=initial.get("description_courte") or "",
            placeholder="Resume en quelques lignes du poste et des attentes.",
            height=120,
        )
        lien = st.text_input(
            "Lien de l'offre",
            value=initial.get("lien") or "",
            placeholder="https://...",
        )

        b1, b2 = st.columns(2)
        with b1:
            statut = st.selectbox("Statut initial", STATUTS, index=0)
        with b2:
            notes = st.text_area(
                "Notes personnelles",
                value=initial.get("notes") or "",
                placeholder="Contact RH, prochaines etapes, points de vigilance...",
                height=95,
            )

        submitted = st.form_submit_button(submit_label, type="primary")

    if submitted:
        payload = {
            "titre": titre,
            "entreprise": entreprise,
            "localisation": localisation,
            "type_contrat": type_contrat,
            "teletravail": teletravail,
            "salaire": salaire,
            "competences": _split_tags(competences),
            "avantages": _split_tags(avantages),
            "description_courte": description,
            "lien": lien,
            "statut": statut,
            "notes": notes,
        }
        _save_payload(payload)


def _reset_state() -> None:
    for key in ["addjob_url", "addjob_extracted", "addjob_last_error"]:
        if key in st.session_state:
            del st.session_state[key]


def show() -> None:
    if not get_current_user():
        st.warning("Connecte-toi pour ajouter une offre.")
        return

    st.markdown("# Ajouter une offre")
    st.caption("Deux modes : extraction automatique par URL ou saisie manuelle en fallback.")

    st.session_state.setdefault("addjob_extracted", None)
    st.session_state.setdefault("addjob_url", "")
    st.session_state.setdefault("addjob_last_error", "")

    a, b = st.columns([4, 1])
    with b:
        if st.button("Reinitialiser", use_container_width=True):
            _reset_state()
            st.rerun()

    tab_url, tab_manual = st.tabs(["Via URL (auto)", "Saisie manuelle"])

    with tab_url:
        st.markdown("### Analyse automatique")
        st.session_state["addjob_url"] = st.text_input(
            "URL de l'offre",
            value=st.session_state.get("addjob_url", ""),
            placeholder="https://www.welcometothejungle.com/...",
        )

        c1, c2 = st.columns([3, 2])
        with c1:
            run_extract = st.button(
                "Scraper et analyser",
                type="primary",
                disabled=not st.session_state["addjob_url"],
                use_container_width=True,
            )
        with c2:
            st.caption("Pipeline: 1) scraping  2) analyse IA")

        if run_extract:
            progress = st.progress(0, text="Etape 1/2 - Scraping de la page")
            try:
                raw_text = scrape_job_url(st.session_state["addjob_url"])
                progress.progress(50, text="Etape 1/2 terminee - Scraping OK")
            except Exception as e:
                st.session_state["addjob_last_error"] = str(e)
                st.error(f"Scraping impossible: {e}")
                st.info(
                    "Aide: certains sites bloquent les robots (LinkedIn connecte, Cloudflare, anti-bot). "
                    "Utilise l'onglet 'Saisie manuelle' en fallback."
                )
                progress.empty()
                return

            try:
                progress.progress(70, text="Etape 2/2 - Analyse IA en cours")
                extracted = extract_job_info(raw_text, source_url=st.session_state["addjob_url"])
                st.session_state["addjob_extracted"] = extracted
                progress.progress(100, text="Etape 2/2 terminee - Offre pre-remplie")
                st.success("Extraction terminee. Verifie les champs puis enregistre.")
            except Exception as e:
                st.error(f"Analyse IA en echec: {e}")
                progress.empty()
                return

        if st.session_state.get("addjob_extracted"):
            st.markdown("### Formulaire pre-rempli")
            _job_form(st.session_state["addjob_extracted"], "job_form_auto", "Enregistrer la candidature")

    with tab_manual:
        st.markdown("### Saisie manuelle (fallback)")
        st.caption("A utiliser si le scraping est bloque ou si l'offre est privee.")
        _job_form({}, "job_form_manual", "Enregistrer manuellement")
