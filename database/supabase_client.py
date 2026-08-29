import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

# Try Streamlit secrets first (for cloud deployment), then environment variables (for local development)
SUPABASE_URL = None
SUPABASE_KEY = None

try:
    import streamlit as st
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
except Exception:
    # Streamlit not installed, or secrets not configured; fall back to env vars
    SUPABASE_URL = SUPABASE_URL or os.environ.get("SUPABASE_URL")
    SUPABASE_KEY = SUPABASE_KEY or os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in Streamlit secrets or environment variables")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
