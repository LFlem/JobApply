import streamlit as st

from utils.auth import get_current_user
from utils.jobs import (
    STATUS_COLORS,
    STATUS_EMOJI,
    STATUTS,
    delete_candidature,
    get_all_candidatures,
    update_candidature,
)

CONTRATS = ["CDI", "CDD", "Freelance", "Stage", "Alternance", "Autre"]
TT = ["Non précisé", "Oui", "Non", "Hybride"]


def _split_tags(raw: str) -> list[str]:
    if not raw:
        return []
    return [token.strip() for token in raw.replace("\n", ",").split(",") if token.strip()]


def _apply_filters(candidatures: list[dict], statuts: list[str], contrats: list[str], query: str) -> list[dict]:
    filtered = candidatures

    if statuts:
        filtered = [c for c in filtered if c.get("statut") in statuts]
    if contrats:
        filtered = [c for c in filtered if c.get("type_contrat") in contrats]
    if query:
        q = query.lower().strip()
        filtered = [
            c
            for c in filtered
            if q in (c.get("titre") or "").lower()
            or q in (c.get("entreprise") or "").lower()
            or q in (c.get("description_courte") or "").lower()
            or q in (c.get("notes") or "").lower()
        ]

    return filtered


def show() -> None:
    current_user = get_current_user()
    if not current_user:
        st.warning("Connecte-toi pour voir tes candidatures.")
        return

    st.markdown("# Mes candidatures")

    f1, f2, f3 = st.columns([2, 2, 3])
    with f1:
        filtre_statut = st.multiselect("Filtre statut", STATUTS)
    with f2:
        filtre_contrat = st.multiselect("Filtre contrat", CONTRATS)
    with f3:
        filtre_recherche = st.text_input("Recherche texte", placeholder="Titre, entreprise, notes, description...")

    try:
        candidatures = get_all_candidatures(current_user["id"])
    except Exception as e:
        st.error(f"Erreur MongoDB : {e}")
        return

    candidatures = _apply_filters(candidatures, filtre_statut, filtre_contrat, filtre_recherche)
    st.caption(f"{len(candidatures)} candidature(s) trouvee(s)")

    if not candidatures:
        st.info("Aucune candidature ne correspond a tes filtres.")
        return

    for c in candidatures:
        doc_id = c["_id"]
        statut = c.get("statut", "À postuler")
        color = STATUS_COLORS.get(statut, "#6b7280")
        emoji = STATUS_EMOJI.get(statut, "-")

        with st.expander(f"{emoji} {c.get('titre') or 'Sans titre'} - {c.get('entreprise') or 'Entreprise inconnue'}"):
            st.markdown(
                f"<span class='badge' style='background:{color}22;color:{color}'>{emoji} {statut}</span>",
                unsafe_allow_html=True,
            )

            tab_infos, tab_statut, tab_edit, tab_notes, tab_delete = st.tabs(
                ["Infos", "Statut", "Modifier", "Notes", "Supprimer"]
            )

            with tab_infos:
                i1, i2 = st.columns(2)
                with i1:
                    st.markdown(f"**Poste:** {c.get('titre') or 'Non renseigne'}")
                    st.markdown(f"**Entreprise:** {c.get('entreprise') or 'Non renseigne'}")
                    st.markdown(f"**Localisation:** {c.get('localisation') or 'Non renseignee'}")
                    st.markdown(f"**Contrat:** {c.get('type_contrat') or 'Non precise'}")
                with i2:
                    st.markdown(f"**Teletravail:** {c.get('teletravail') or 'Non precise'}")
                    st.markdown(f"**Salaire:** {c.get('salaire') or 'Non precise'}")
                    st.markdown(f"**Lien:** {c.get('lien') or 'Non renseigne'}")

                if c.get("competences"):
                    st.markdown("**Competences:** " + ", ".join(c.get("competences") or []))
                if c.get("avantages"):
                    st.markdown("**Avantages:** " + ", ".join(c.get("avantages") or []))
                if c.get("description_courte"):
                    st.markdown("**Description:**")
                    st.write(c.get("description_courte"))

            with tab_statut:
                st.caption("Actions rapides: le statut actuel est mis en evidence.")
                cols = st.columns(len(STATUTS))
                for idx, s in enumerate(STATUTS):
                    with cols[idx]:
                        is_current = s == statut
                        if st.button(
                            f"{STATUS_EMOJI.get(s, '-') } {s}",
                            key=f"quick_status_{doc_id}_{s}",
                            type="primary" if is_current else "secondary",
                            use_container_width=True,
                        ):
                            if is_current:
                                st.info("Ce statut est deja actif.")
                            elif update_candidature(doc_id, {"statut": s}, current_user["id"]):
                                st.success(f"Statut mis a jour: {s}")
                                st.rerun()
                            else:
                                st.error("Echec de la mise a jour du statut.")

            with tab_edit:
                with st.form(f"edit_form_{doc_id}"):
                    c1, c2 = st.columns(2)
                    with c1:
                        new_titre = st.text_input("Intitule du poste", value=c.get("titre") or "")
                        new_entreprise = st.text_input("Entreprise", value=c.get("entreprise") or "")
                        new_loc = st.text_input("Localisation", value=c.get("localisation") or "")
                        new_lien = st.text_input("Lien", value=c.get("lien") or "")
                    with c2:
                        new_contrat = st.selectbox(
                            "Type de contrat",
                            CONTRATS,
                            index=CONTRATS.index(c.get("type_contrat")) if c.get("type_contrat") in CONTRATS else 0,
                        )
                        new_tt = st.selectbox(
                            "Teletravail",
                            TT,
                            index=TT.index(c.get("teletravail")) if c.get("teletravail") in TT else 0,
                        )
                        new_salaire = st.text_input("Salaire", value=c.get("salaire") or "")
                        new_statut = st.selectbox(
                            "Statut",
                            STATUTS,
                            index=STATUTS.index(statut) if statut in STATUTS else 0,
                        )

                    new_comp = st.text_area(
                        "Competences (virgules)",
                        value=", ".join(c.get("competences") or []),
                        height=90,
                    )
                    new_adv = st.text_area(
                        "Avantages (virgules)",
                        value=", ".join(c.get("avantages") or []),
                        height=80,
                    )
                    new_desc = st.text_area(
                        "Description courte",
                        value=c.get("description_courte") or "",
                        height=120,
                    )
                    new_notes_inline = st.text_area(
                        "Notes (edition rapide)",
                        value=c.get("notes") or "",
                        height=90,
                    )

                    save_edit = st.form_submit_button("Sauvegarder les modifications", type="primary")

                if save_edit:
                    updates = {
                        "titre": new_titre,
                        "entreprise": new_entreprise,
                        "localisation": new_loc,
                        "lien": new_lien,
                        "type_contrat": new_contrat,
                        "teletravail": new_tt,
                        "salaire": new_salaire,
                        "statut": new_statut,
                        "competences": _split_tags(new_comp),
                        "avantages": _split_tags(new_adv),
                        "description_courte": new_desc,
                        "notes": new_notes_inline,
                    }
                    if update_candidature(doc_id, updates, current_user["id"]):
                        st.success("Candidature mise a jour.")
                        st.rerun()
                    else:
                        st.error("Aucun changement detecte ou erreur de mise a jour.")

            with tab_notes:
                notes_value = st.text_area(
                    "Notes de suivi",
                    value=c.get("notes") or "",
                    key=f"notes_area_{doc_id}",
                    height=180,
                )
                if st.button("Enregistrer les notes", key=f"save_notes_{doc_id}"):
                    if update_candidature(doc_id, {"notes": notes_value}, current_user["id"]):
                        st.success("Notes mises a jour.")
                        st.rerun()
                    else:
                        st.error("Aucun changement detecte ou erreur de mise a jour.")

            with tab_delete:
                st.warning("Suppression irreversible.")
                confirm = st.checkbox(
                    "Je confirme la suppression definitive de cette candidature.",
                    key=f"confirm_delete_{doc_id}",
                )
                if st.button(
                    "Supprimer la candidature",
                    key=f"delete_btn_{doc_id}",
                    disabled=not confirm,
                    type="primary",
                ):
                    if delete_candidature(doc_id, current_user["id"]):
                        st.success("Candidature supprimee.")
                        st.rerun()
                    else:
                        st.error("Echec de la suppression.")
