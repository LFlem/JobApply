import streamlit as st

from utils.auth import get_current_user
from utils.jobs import STATUS_COLORS, STATUS_EMOJI, STATUTS, get_all_candidatures, get_stats


def _rich_tags(values: list[str], max_items: int = 6) -> str:
    if not values:
        return "<span class='badge' style='background:var(--surface-muted);color:var(--text-muted)'>Aucune</span>"
    return " ".join(
        f"<span class='badge' style='background:var(--accent-soft);color:var(--accent)'>{v}</span>"
        for v in values[:max_items]
    )


def show() -> None:
    current_user = get_current_user()
    if not current_user:
        st.warning("Connecte-toi pour acceder a tes candidatures.")
        return

    st.markdown("# Tableau de bord")
    st.caption("Vue pipeline + apercu detaille des dernieres candidatures")

    try:
        stats = get_stats(current_user["id"])
        candidatures = get_all_candidatures(current_user["id"])
    except Exception as e:
        st.error(f"Connexion MongoDB impossible : {e}")
        st.info("Verifie ton fichier `.env` et la variable `MONGODB_URI`.")
        return

    total = stats.get("total", 0)
    if total == 0:
        st.info("Base vide pour le moment. Ajoute une premiere candidature depuis 'Ajouter une offre'.")
        return

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Total", total)
    k2.metric("A postuler", stats.get("À postuler", 0))
    k3.metric("Postule", stats.get("Postulé", 0))
    k4.metric("Entretien", stats.get("Entretien", 0))
    k5.metric("Accepte", stats.get("Accepté", 0))

    st.markdown("### Pipeline de candidatures")
    for statut in STATUTS:
        count = stats.get(statut, 0)
        pct = int((count / total) * 100) if total else 0
        color = STATUS_COLORS.get(statut, "#6b7280")
        emoji = STATUS_EMOJI.get(statut, "-")

        c1, c2 = st.columns([3, 1])
        with c1:
            st.markdown(f"**{emoji} {statut}**")
            st.progress(pct, text=f"{pct}% ({count}/{total})")
        with c2:
            st.markdown(
                f"<div class='badge' style='background:{color}22;color:{color};margin-top:24px'>{count} element(s)</div>",
                unsafe_allow_html=True,
            )

    st.markdown("### Dernieres candidatures")
    for c in candidatures[:8]:
        statut = c.get("statut", "À postuler")
        color = STATUS_COLORS.get(statut, "#6b7280")
        emoji = STATUS_EMOJI.get(statut, "-")

        st.markdown(
            f"""
            <div class="job-card">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px;">
                    <div>
                        <div class="job-title">{c.get('titre') or 'Sans titre'}</div>
                        <div class="job-company">{c.get('entreprise') or 'Entreprise non renseignee'} · {c.get('localisation') or 'Localisation non renseignee'}</div>
                    </div>
                    <span class="badge" style="background:{color}22;color:{color}">{emoji} {statut}</span>
                </div>
                <div style="margin-top:10px;display:flex;gap:8px;flex-wrap:wrap;">
                    <span class="badge" style="background:var(--surface-muted);color:var(--text)">Contrat: {c.get('type_contrat') or 'Non precise'}</span>
                    <span class="badge" style="background:var(--surface-muted);color:var(--text)">Teletravail: {c.get('teletravail') or 'Non precise'}</span>
                    <span class="badge" style="background:var(--surface-muted);color:var(--text)">Salaire: {c.get('salaire') or 'Non precise'}</span>
                </div>
                <div style="margin-top:10px;">{_rich_tags(c.get('competences') or [])}</div>
                <div style="margin-top:10px;">
                    {f"<a href='{c.get('lien')}' target='_blank' style='color:var(--link-color)'>Voir l'offre</a>" if c.get('lien') else "<span style='color:var(--text-muted)'>Lien non renseigne</span>"}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if len(candidatures) > 8:
        st.caption(f"... {len(candidatures) - 8} autre(s) candidature(s) disponibles dans 'Mes candidatures'.")
