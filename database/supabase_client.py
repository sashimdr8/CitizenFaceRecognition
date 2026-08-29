import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def get_supabase_client():
    """Get Supabase client with lazy initialization."""
    SUPABASE_URL = None
    SUPABASE_KEY = None

    try:
        import streamlit as st
        SUPABASE_URL = st.secrets["SUPABASE_URL"]
        SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    except Exception:
        # Streamlit not installed, or secrets not configured; fall back to env vars
        SUPABASE_URL = os.environ.get("SUPABASE_URL")
        SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in Streamlit secrets or environment variables")

    return create_client(SUPABASE_URL, SUPABASE_KEY)

# Lazy initialization - will be called when needed
supabase = None

def ensure_supabase():
    """Ensure Supabase client is initialized."""
    global supabase
    if supabase is None:
        supabase = get_supabase_client()
    return supabase
