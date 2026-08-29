import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

# Try Streamlit secrets first (for cloud deployment), then environment variables (for local development)
try:
    import streamlit as st
    SUPABASE_URL = st.secrets.get("SUPABASE_URL") or os.environ.get("SUPABASE_URL")
    SUPABASE_KEY = st.secrets.get("SUPABASE_KEY") or os.environ.get("SUPABASE_KEY")
except ImportError:
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in Streamlit secrets or environment variables")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
