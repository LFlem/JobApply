import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

def scrape_job_url(url: str) -> str:
    """
    Récupère le texte brut d'une offre d'emploi depuis une URL.
    Retourne le texte nettoyé ou lève une exception.
    """
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Impossible de charger la page : {e}")

    soup = BeautifulSoup(resp.text, "html.parser")

    # Supprimer scripts, styles, nav, footer
    for tag in soup(["script", "style", "nav", "footer", "header", "noscript", "iframe"]):
        tag.decompose()

    # Cibler les blocs principaux courants sur les jobboards
    candidates = []
    for selector in [
        "article", "main", '[class*="job"]', '[class*="offer"]',
        '[class*="description"]', '[id*="job"]', '[id*="offer"]',
    ]:
        found = soup.select(selector)
        for el in found:
            text = el.get_text(separator="\n", strip=True)
            if len(text) > 300:
                candidates.append(text)

    if candidates:
        # Prendre le plus long (le plus riche en contenu)
        raw = max(candidates, key=len)
    else:
        raw = soup.get_text(separator="\n", strip=True)

    # Nettoyer les lignes vides multiples
    lines = [l.strip() for l in raw.splitlines() if l.strip()]
    return "\n".join(lines)[:8000]  # limite raisonnable pour l'API
