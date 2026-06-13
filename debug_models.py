import streamlit as st
from pypdf import PdfReader
import os
from google import genai
from dotenv import load_dotenv
import json
import time

# --- INITIALIZATION ---
st.set_page_config(page_title="ResumeIntel Pro", layout="wide")

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("Missing GEMINI_API_KEY")
    st.stop()

client = genai.Client(api_key=api_key)

# --- DEBUG: LIST MODELS ---
with st.sidebar:
    st.markdown("### 🔍 Model Discovery")
    if st.button("List Available Models"):
        try:
            models = client.models.list()
            for m in models:
                st.write(f"`{m.name}`") # Use backticks to see exact string
        except Exception as e:
            st.error(f"ListModels failed: {e}")

# --- REST OF APP ---
# ... (Continuing with the prompt logic but with a manual override for testing)
model_id = st.sidebar.text_input("Manual Model ID", "gemini-1.5-flash")

# Logic to catch the text and execute
st.write("### Ready. Click 'List Available Models' to find the correct ID.")
