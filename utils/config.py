import os

import streamlit as st
from dotenv import load_dotenv

load_dotenv()


def get_secret(name: str, default: str | None = None) -> str | None:
    if name in st.secrets:
        value = st.secrets[name]
        return str(value) if value is not None else default
    return os.getenv(name, default)