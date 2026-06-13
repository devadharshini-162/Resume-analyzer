import streamlit as st
from pypdf import PdfReader
import os
from google import genai
from dotenv import load_dotenv
import json
import time

# --- INITIALIZATION ---
st.set_page_config(
    page_title="ResumeIntel Pro | AI Suite",
    page_icon="🎯",
    layout="wide"
)

# --- PREMIUM UI SYSTEM ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
    }

    .stApp {
        background-color: #121824;
        color: #F1F5F9;
        font-family: 'Inter', sans-serif;
    }
    
    section[data-testid="stSidebar"] {
        background-color: #000000 !important;
        border-right: 1px solid #1E2530;
    }

    [data-testid="stFileUploadDropzone"] {
        border: 2px dashed #38BDF8 !important;
        background: #121824 !important;
        border-radius: 10px;
    }

    /* Container for Wrap Fix */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border: 1px solid #38BDF8 !important;
        background-color: #1E2530 !important;
        border-radius: 12px !important;
        padding: 15px !important;
        margin-bottom: 10px;
    }

    /* Custom Progress Bar */
    .custom-progress-bg {
        width: 100%;
        background-color: #334155;
        border-radius: 10px;
        height: 8px;
        margin-top: 8px;
    }
    .custom-progress-fill {
        height: 8px;
        border-radius: 10px;
        background: linear-gradient(90deg, #38BDF8, #818CF8);
    }

    /* Ranking Cards */
    .ranking-card {
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 15px;
        background: #1E2530;
    }
    .match-best { border: 2px solid #22c55e !important; }
    .match-med { border: 2px solid #f97316 !important; }
    .match-weak { border: 2px solid #ef4444 !important; }

    .metric-card {
        height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        background: #1E2530;
        border-radius: 10px;
        border: 1px solid #334155;
    }
    .metric-val { font-size: 2.2rem; font-weight: 800; color: #38BDF8; }
    .metric-lbl { color: #94A3B8; font-size: 0.8rem; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("Missing GEMINI_API_KEY. Please check your .env file.")
    st.stop()

client = genai.Client(api_key=api_key)

if "all_results" not in st.session_state:
    st.session_state.all_results = {}
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- MODEL DISCOVERY ---
available_models = []
try:
    models = client.models.list()
    available_models = [m.name for m in models if 'generateContent' in m.supported_methods]
except:
    pass

# --- UTILS ---
@st.cache_data
def extract_text(file_bytes):
    from io import BytesIO
    reader = PdfReader(BytesIO(file_bytes))
    return " ".join([page.extract_text() for page in reader.pages if page.extract_text()])

def clean_and_parse(text):
    try:
        raw = text.strip()
        if "```json" in raw: raw = raw.split("```json")[-1].split("```")[0]
        start = raw.find('{')
        end = raw.rfind('}') + 1
        return json.loads(raw[start:end])
    except: return None

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### :material/dataset: ENGINE CONFIG")
    
    if available_models:
        # Default to 2.5-flash if available, otherwise first in list
        def_idx = available_models.index("models/gemini-2.5-flash") if "models/gemini-2.5-flash" in available_models else 0
        target_model = st.selectbox("Active AI Model", available_models, index=def_idx)
    else:
        target_model = st.text_input("Manual Model ID", "models/gemini-flash-latest")
        
    res_files = st.file_uploader("Upload Resumes (PDF)", type="pdf", accept_multiple_files=True)
    jd_input = st.text_area("Job Requirements", height=150, placeholder="Paste requirements here...")
    run_btn = st.button("RUN INTELLIGENCE ENGINE", use_container_width=True)
    
    if st.button("WIPE SYSTEM DATA"):
        st.session_state.all_results = {}
        st.session_state.chat_history = []
        st.rerun()

# --- MAIN ---
st.markdown("<h2 style='margin-bottom:0;'>RESUME INTELLIGENCE PRO</h2>", unsafe_allow_html=True)
st.caption("Industrial Grade AI Recruitment & Document Assistant")
st.divider()

current_res_context = ""
if res_files:
    for rf in res_files:
        current_res_context += f"\nFile {rf.name}: {extract_text(rf.getvalue())}\n"

if run_btn:
    if not res_files or not jd_input:
        st.warning("Please provide both resumes and a Job Description.")
    else:
        for f in res_files:
            txt = extract_text(f.getvalue())
            with st.spinner(f"Analyzing {f.name}..."):
                prompt = f"""
                Analyze resume vs JD. Return STRICT JSON:
                {{
                    "match_pct": 0-100,
                    "recommendation": "Strong|Moderate|Weak Match",
                    "matching_skills": [],
                    "missing_skills": [],
                    "strengths": [],
                    "improvements": [],
                    "ai_suggestions": [],
                    "ats_checks": [
                        {{"category": "Keyword Density", "status": "Pass/Fail", "advice": "..."}},
                        {{"category": "Formatting", "status": "Pass/Fail", "advice": "..."}},
                        {{"category": "Quantification", "status": "Pass/Fail", "advice": "..."}}
                    ]
                }}
                Resume: {txt}
                JD: {jd_input}
                """
                try:
                    time.sleep(1) # Rate limit safety
                    resp = client.models.generate_content(model=target_model, contents=prompt)
                    data = clean_and_parse(resp.text)
                    if data:
                        st.session_state.all_results[f.name] = data
                        st.success(f"Success: {f.name}")
                    else:
                        st.error(f"Failed to parse AI response for {f.name}")
                except Exception as e:
                    st.error(f"API Error ({f.name}): {e}")

# --- TABS ---
t1, t2, t3, t4, t5 = st.tabs([
    ":material/insights: AUDIT", 
    ":material/leaderboard: RANK", 
    ":material/filter_list: SMART FILTER",
    ":material/verified: ATS", 
    ":material/chat: AI CHAT"
])

if st.session_state.all_results:
    with t1:
        sel = st.selectbox("Candidate Profile", options=list(st.session_state.all_results.keys()), key="audit_sel")
        res = st.session_state.all_results[sel]
        
        score = res.get('match_pct', 0)
        m_cl = "match-weak"
        if score >= 80: m_cl = "match-best"
        elif score >= 50: m_cl = "match-med"
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"<div class='metric-card {m_cl}'><div class='metric-lbl'>Match score</div><div class='metric-val'>{score}%</div></div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div class='metric-card {m_cl}'><div class='metric-lbl'>Verdict</div><div style='font-size: 1.4rem; font-weight: 600; color: #38BDF8;'>{res.get('recommendation', 'N/A')}</div></div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        s1, s2, s3 = st.tabs([":material/extension: Skills", ":material/analytics: SWOT", ":material/auto_awesome: Advice"])
        
        with s1:
            st.markdown("#### :material/check_circle: Matching Skills")
            with st.container(border=True):
                m_sk = res.get('matching_skills', [])
                if m_sk:
                    co = st.columns(3)
                    for i, sk in enumerate(m_sk): co[i%3].markdown(f"• {sk}")
                else: st.write("No matches.")
            
            st.markdown("#### :material/cancel: Missing Requirements")
            with st.container(border=True):
                mi_sk = res.get('missing_skills', [])
                if mi_sk:
                    cm = st.columns(3)
                    for i, sk in enumerate(mi_sk): cm[i%3].markdown(f"• {sk}")
                else: st.write("All met.")

        with s2:
            st.markdown("#### :material/star: Strengths")
            with st.container(border=True):
                for s in res.get('strengths', []): st.markdown(f"+ {s}")
            st.markdown("#### :material/edit_note: Necessary Improvements")
            with st.container(border=True):
                for i in res.get('improvements', []): st.markdown(f"! {i}")

        with s3:
            st.markdown("#### :material/lightbulb: Actionable AI Suggestions")
            for sug in res.get('ai_suggestions', []):
                with st.container(border=True): st.markdown(sug)

    with t2:
        st.markdown("### Talent Leaderboard")
        ranked = sorted(st.session_state.all_results.items(), key=lambda x: int(float(x[1].get('match_pct', 0))), reverse=True)
        for i, (name, d) in enumerate(ranked):
            sc = d.get('match_pct', 0)
            m_cl = "match-weak"
            if sc >= 80: m_cl = "match-best"
            elif sc >= 50: m_cl = "match-med"
            st.markdown(f"""
                <div class='ranking-card {m_cl}'>
                    <div style='display: flex; justify-content: space-between;'>
                        <span><b>#{i+1}</b> {name}</span>
                        <span style='font-weight:800;'>{sc}%</span>
                    </div>
                    <div class='custom-progress-bg'>
                        <div class='custom-progress-fill' style='width: {sc}%'></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    with t3:
        st.subheader(":material/psychology: Smart Filter")
        query = st.text_input("Example: 'Candidates with Computer Vision skills'", key="smart_q")
        if query:
            with st.spinner("Bulk Parsing..."):
                try:
                    resp = client.models.generate_content(model=target_model, contents=f"Data: {current_res_context}\nQuery: {query}")
                    st.write(resp.text)
                except Exception as e: st.error(f"Error: {e}")

    with t4:
        st.markdown("### ATS Structural Audit")
        sel_ats = st.selectbox("Audit For:", options=list(st.session_state.all_results.keys()), key="ats_sel")
        for chk in st.session_state.all_results[sel_ats].get('ats_checks', []):
            with st.container(border=True):
                st.markdown(f"**{chk.get('category')}** — {chk.get('status')}")
                st.caption(chk.get('advice'))

    with t5:
        st.subheader("💬 AI Interaction Vault")
        cont = st.container(height=450)
        with cont:
            for msg in st.session_state.chat_history:
                with st.chat_message(msg["role"]): st.markdown(msg["content"])
        
        if prompt := st.chat_input("Ask about any candidate..."):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with cont:
                with st.chat_message("user"): st.markdown(prompt)
                with st.chat_message("assistant"):
                    try:
                        resp = client.models.generate_content(model=target_model, contents=f"Resumes: {current_res_context}\nQ: {prompt}")
                        st.markdown(resp.text)
                        st.session_state.chat_history.append({"role": "assistant", "content": resp.text})
                    except Exception as e: st.error(f"Chat failed: {e}")
else:
    st.info("Awaiting file uploads and analysis...")