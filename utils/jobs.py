from datetime import datetime, timezone
from bson import ObjectId
from utils.db import get_collection

COLLECTION = "candidatures"

STATUTS = ["À postuler", "Postulé", "Entretien", "Refusé", "Accepté"]

STATUS_COLORS = {
    "À postuler": "#6B7280",
    "Postulé":    "#3B82F6",
    "Entretien":  "#F59E0B",
    "Refusé":     "#EF4444",
    "Accepté":    "#10B981",
}

STATUS_EMOJI = {
    "À postuler": "📋",
    "Postulé":    "📨",
    "Entretien":  "🗣️",
    "Refusé":     "❌",
    "Accepté":    "✅",
}


def _build_query(user_id: str | None, filters: dict | None = None) -> dict:
    query = dict(filters or {})
    if user_id:
        query["owner_id"] = user_id
    return query


def add_candidature(data: dict, user_id: str | None = None) -> str:
    col = get_collection(COLLECTION)
    if user_id:
        data["owner_id"] = user_id
    data["created_at"] = datetime.now(timezone.utc)
    data["updated_at"] = datetime.now(timezone.utc)
    data.setdefault("statut", "À postuler")
    data.setdefault("notes", "")
    result = col.insert_one(data)
    return str(result.inserted_id)


def get_all_candidatures(user_id: str | None = None, filters: dict = None) -> list:
    col = get_collection(COLLECTION)
    query = _build_query(user_id, filters)
    docs = col.find(query).sort("created_at", -1)
    result = []
    for d in docs:
        d["_id"] = str(d["_id"])
        result.append(d)
    return result


def get_candidature(doc_id: str, user_id: str | None = None) -> dict | None:
    col = get_collection(COLLECTION)
    query = _build_query(user_id)
    query["_id"] = ObjectId(doc_id)
    doc = col.find_one(query)
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc


def update_candidature(doc_id: str, updates: dict, user_id: str | None = None) -> bool:
    col = get_collection(COLLECTION)
    updates["updated_at"] = datetime.now(timezone.utc)
    query = _build_query(user_id)
    query["_id"] = ObjectId(doc_id)
    result = col.update_one(query, {"$set": updates})
    return result.modified_count > 0


def delete_candidature(doc_id: str, user_id: str | None = None) -> bool:
    col = get_collection(COLLECTION)
    query = _build_query(user_id)
    query["_id"] = ObjectId(doc_id)
    result = col.delete_one(query)
    return result.deleted_count > 0


def get_stats(user_id: str | None = None) -> dict:
    col = get_collection(COLLECTION)
    base_query = _build_query(user_id)
    total = col.count_documents(base_query)
    stats = {"total": total}
    for statut in STATUTS:
        stats[statut] = col.count_documents({**base_query, "statut": statut})
    return stats
