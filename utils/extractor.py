import json

from anthropic import Anthropic

from utils.config import get_secret

SYSTEM_PROMPT = """Tu es un assistant spécialisé dans l'analyse d'offres d'emploi.
Retourne UNIQUEMENT un JSON valide, sans texte avant ou après.

Structure JSON attendue :
{
  "titre": "...",
  "entreprise": "...",
  "localisation": "...",
  "type_contrat": "CDI | CDD | Freelance | Stage | Alternance | Autre",
  "teletravail": "Oui | Non | Hybride | Non précisé",
  "salaire": "...",
  "competences": ["..."],
  "avantages": ["..."],
  "description_courte": "...",
  "lien": null
}"""


def _extract_json_text(raw: str) -> str:
    content = raw.strip()
    if content.startswith("```"):
        content = content.split("```", 2)[1]
        if content.startswith("json"):
            content = content[4:]
    return content.strip()


def _extract_with_anthropic(text: str) -> dict:
    client = Anthropic(api_key=get_secret("ANTHROPIC_API_KEY"))
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": f"Analyse cette offre :\n\n{text}"},
        ],
        max_tokens=1000,
        temperature=0.1,
    )

    text_blocks = [block.text for block in response.content if getattr(block, "type", None) == "text"]
    if not text_blocks:
        raise ValueError("La reponse Anthropic ne contient pas de texte exploitable.")

    return json.loads(_extract_json_text("\n".join(text_blocks)))


def _extract_with_groq(text: str) -> dict:
    from groq import Groq

    client = Groq(api_key=get_secret("GROQ_API_KEY"))
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Analyse cette offre :\n\n{text}"},
        ],
        max_tokens=1000,
        temperature=0.1,
    )

    raw = response.choices[0].message.content or ""
    return json.loads(_extract_json_text(raw))

def extract_job_info(text: str, source_url: str = None) -> dict:
    anthropic_api_key = get_secret("ANTHROPIC_API_KEY")
    groq_api_key = get_secret("GROQ_API_KEY")

    if anthropic_api_key:
        data = _extract_with_anthropic(text)
    elif groq_api_key:
        data = _extract_with_groq(text)
    else:
        raise ValueError(
            "Aucune cle API configuree. Ajoute ANTHROPIC_API_KEY ou GROQ_API_KEY dans .env ou dans les secrets Streamlit."
        )

    if source_url:
        data["lien"] = source_url
    return data