from pymongo import MongoClient

from utils.config import get_secret

_client = None

def get_db():
    global _client
    if _client is None:
        uri = get_secret("MONGODB_URI")
        if not uri:
            raise ValueError("MONGODB_URI manquant dans .env ou dans les secrets Streamlit")
        _client = MongoClient(uri)
    db_name = get_secret("MONGODB_DB", "job_tracker")
    return _client[db_name]

def get_collection(name: str):
    return get_db()[name]
