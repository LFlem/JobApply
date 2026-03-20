import hashlib
import hmac
import re
import secrets
from datetime import datetime, timezone, timedelta

import streamlit as st
from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from utils.db import get_collection

COLLECTION = "users"
EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def _users_collection():
    col = get_collection(COLLECTION)
    col.create_index("email", unique=True)
    return col


def _serialize_user(user: dict) -> dict:
    return {
        "id": str(user["_id"]),
        "display_name": user.get("display_name", "Utilisateur"),
        "email": user["email"],
    }


def _hash_password(password: str, salt: str | None = None) -> str:
    password_salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        password_salt.encode("utf-8"),
        390000,
    ).hex()
    return f"{password_salt}${digest}"


def _verify_password(password: str, stored_hash: str) -> bool:
    salt, _, _ = stored_hash.partition("$")
    expected = _hash_password(password, salt)
    return hmac.compare_digest(expected, stored_hash)


def validate_registration(display_name: str, email: str, password: str, password_confirm: str) -> str | None:
    if not display_name.strip():
        return "Le nom d'affichage est obligatoire."
    if len(display_name.strip()) < 2:
        return "Le nom d'affichage doit contenir au moins 2 caracteres."
    normalized_email = email.strip().lower()
    if not normalized_email:
        return "L'email est obligatoire."
    if not EMAIL_RE.match(normalized_email):
        return "L'email n'est pas valide."
    if len(password) < 8:
        return "Le mot de passe doit contenir au moins 8 caracteres."
    if password != password_confirm:
        return "Les mots de passe ne correspondent pas."
    return None


def register_user(display_name: str, email: str, password: str) -> tuple[bool, str, dict | None]:
    col = _users_collection()
    normalized_email = email.strip().lower()
    user = {
        "display_name": display_name.strip(),
        "email": normalized_email,
        "password_hash": _hash_password(password),
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }

    try:
        result = col.insert_one(user)
    except DuplicateKeyError:
        return False, "Un compte existe deja avec cet email.", None

    user["_id"] = result.inserted_id
    return True, "Compte cree avec succes.", _serialize_user(user)


def authenticate_user(email: str, password: str) -> tuple[bool, str, dict | None]:
    col = _users_collection()
    normalized_email = email.strip().lower()
    if not normalized_email or not password:
        return False, "Email et mot de passe obligatoires.", None

    user = col.find_one({"email": normalized_email})
    if not user or not _verify_password(password, user.get("password_hash", "")):
        return False, "Identifiants invalides.", None

    col.update_one(
        {"_id": user["_id"]},
        {"$set": {"updated_at": datetime.now(timezone.utc), "last_login_at": datetime.now(timezone.utc)}},
    )
    return True, "Connexion reussie.", _serialize_user(user)


def get_current_user() -> dict | None:
    return st.session_state.get("auth_user")


def is_authenticated() -> bool:
    return get_current_user() is not None


def login_user(user: dict) -> None:
    st.session_state["auth_user"] = user
    st.session_state["auth_user_id"] = user["id"]
    # Initialiser le timestamp d'activité pour détection d'inactivité
    st.session_state["auth_last_activity"] = datetime.now(timezone.utc)


def logout_user() -> None:
    st.session_state.pop("auth_user", None)
    st.session_state.pop("auth_user_id", None)
    st.session_state.pop("auth_last_activity", None)


def update_last_activity() -> None:
    """Met à jour le timestamp de la dernière activité."""
    if is_authenticated():
        st.session_state["auth_last_activity"] = datetime.now(timezone.utc)


def check_session_timeout(timeout_minutes: int = 30) -> bool:
    """
    Vérifie si la session a expiré due à l'inactivité.
    Retourne True si la session est toujours valide, False si elle a expiré.
    """
    if not is_authenticated():
        return True  # Pas de session, donc pas besoin de vérifier
    
    last_activity = st.session_state.get("auth_last_activity")
    if not last_activity:
        return True  # Pas de timestamp, laisser passer
    
    time_elapsed = datetime.now(timezone.utc) - last_activity
    timeout = timedelta(minutes=timeout_minutes)
    
    if time_elapsed > timeout:
        # Session expirée
        logout_user()
        try:
            from streamlit_cookies_manager import CookieManager
            cookies = CookieManager()
            cookies.delete("auth_user_id")
        except Exception:
            pass
        return False  # Session expiree
    
    return True  # Session toujours valide


def restore_session_from_cookie() -> bool:
    """Restaure la session utilisateur depuis le cookie."""
    try:
        from streamlit_cookies_manager import CookieManager
        cookies = CookieManager()
        
        user_id = cookies.get("auth_user_id", "")
        if not user_id:
            return False
            
        # Récupérer l'utilisateur depuis la BD
        col = _users_collection()
        user = col.find_one({"_id": ObjectId(user_id)})
        
        if user:
            login_user(_serialize_user(user))
            return True
        else:
            # Le cookie est expiré ou invalide
            cookies.delete("auth_user_id")
            return False
    except Exception:
        return False


def save_session_to_cookie(user_id: str) -> None:
    """Sauvegarde l'ID utilisateur dans un cookie."""
    try:
        from streamlit_cookies_manager import CookieManager
        cookies = CookieManager()
        cookies["auth_user_id"] = user_id
    except Exception:
        pass
