import streamlit as st
from pypdf import PdfReader
import os
from google import genai
from dotenv import load_dotenv
import json
import time

# --- INITIALIZATION ---
st.set_page_config(
    page_title="ResumeIntel Pro",
    page_icon="💼",
    layout="wide"
)

# --- REFINED COLOR PALETTE & LAYOUT STYLING ---
st.markdown("""
    <style>
    /* Hiding Streamlit Default UI */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* Top Padding Reduction */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
    }

    /* Core Theme - Main Area */
    .stApp {
        background-color: #121824;
        color: #F1F5F9;
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar Styling - Distinct Color */
    section[data-testid="stSidebar"] {
        background-color: #0c111d !important;
        border-right: 1px solid #1E2530;
    }

    /* Tab Title Spacing */
    .stTabs [data-baseweb="tab-list"] {
        gap: 30px !important;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border: none !important;
        padding: 10px 15px !important;
    }

    /* Score Color Coding */
    .match-best { border: 2px solid #22c55e !important; background: rgba(34, 197, 94, 0.05) !important; }
    .match-med { border: 2px solid #f97316 !important; background: rgba(249, 115, 22, 0.05) !important; }
    .match-weak { border: 2px solid #ef4444 !important; background: rgba(239, 68, 68, 0.05) !important; }

    /* Balanced Metric Boxes */
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

    /* Separated Blocks */
    .content-box {
        background: #1E2530;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
    }
    .bright-border { border: 1px solid #38BDF8; }

    /* AI Suggestions High Visibility */
    .sug-box {
        font-weight: 500;
        color: #F1F5F9;
        background: #1E2530;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 10px;
        border: 1px solid #38BDF8;
    }
    </style>
    """, unsafe_allow_html=True)

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key = api_key)

if "all_results" not in st.session_state:
    st.session_state.all_results = {}
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- UTILS ---

@st.cache_data
def extract_text(file_bytes):
    from io import BytesIO
    reader = PdfReader(BytesIO(file_bytes))
    return " ".join([page.extract_text() for page in reader.pages if page.extract_text()])

def get_match_class(score):
    if score >= 80: return "match-best"
    if score >= 50: return "match-med"
    return "match-weak"

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### :material/upload_file: UPLOAD DETAILS")
    res_files = st.file_uploader("Upload Resumes (PDF)", type="pdf", accept_multiple_files=True)
    jd_input = st.text_area("Job Requirements", height=200)
    run_btn = st.button("START ANALYSIS", use_container_width=True)
    
    if st.button("WIPE ALL DATA"):
        st.session_state.all_results = {}
        st.session_state.chat_history = []
        st.rerun()

# --- MAIN ---
st.markdown("<h2 style='margin-bottom:0;'>RESUME INTELLIGENCE PRO</h2>", unsafe_allow_html=True)
st.caption("Advanced AI Recruitment & Document Assistant")
st.divider()

if run_btn:
    if not res_files or not jd_input:
        st.error("Please provide both inputs.")
    else:
        for f in res_files:
            text = extract_text(f.getvalue())
            prompt = f"""
            Analyze resume vs JD. Return STRICT JSON:
            {{
                "match_pct": number,
                "recommendation": "Strong Match | Moderate Match | Weak Match",
                "matching_skills": ["skill1", ...],
                "missing_skills": ["skill1", ...],
                "strengths": ["string"],
                "improvements": ["string"],
                "ai_suggestions": ["string"],
                "ats_checks": [
                    {{"category": "Keyword Density", "status": "Pass/Fail", "advice": "short string"}},
                    {{"category": "Formatting", "status": "Pass/Fail", "advice": "short string"}},
                    {{"category": "Quantification", "status": "Pass/Fail", "advice": "short string"}}
                ]
            }}
            Resume: {text}
            JD: {jd_input}
            """
            with st.spinner(f"Analyzing {f.name}..."):
                try:
                    time.sleep(1)
                    resp = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
                    raw_text = resp.text.strip().replace("```json","").replace("```","")
                    st.session_state.all_results[f.name] = json.loads(raw_text)
                except:
                    st.error(f"Analysis failed for {f.name}")

# --- DASHBOARD ---
t1, t2, t3, t4 = st.tabs([
    ":material/insights: AUDIT", 
    ":material/leaderboard: RANK", 
    ":material/rule: ATS",
    ":material/chat: AI CHAT"
])

if st.session_state.all_results:
    with t1:
        sel = st.selectbox("Active Candidate", options=list(st.session_state.all_results.keys()))
        data = st.session_state.all_results[sel]
        match_class = get_match_class(data['match_pct'])
        
        # HEADLINE METRICS - Same Size
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"<div class='metric-card {match_class}'><div class='metric-lbl'>Match score</div><div class='metric-val'>{data['match_pct']}%</div></div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div class='metric-card {match_class}'><div class='metric-lbl'>Recommendation</div><div style='font-size: 1.4rem; font-weight: 600; color: #38BDF8;'>{data['recommendation']}</div></div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # NESTED ANALYSIS BLOCKS (Sub-Tabs)
        s1, s2, s3 = st.tabs([":material/list_alt: Skill Matrix", ":material/analytics: SWOT Analysis", ":material/auto_awesome: AI Path"])
        
        with s1:
            st.markdown("#### :material/check_circle: Matching Skills")
            with st.container(border=True):
                # Using a bright border if matching
                m_skills = data.get('matching_skills', [])
                if m_skills:
                    cols = st.columns(3)
                    for i, skill in enumerate(m_skills):
                        cols[i % 3].markdown(f"• {skill}")
                else: st.write("No direct skill matches found.")
            
            st.markdown("#### :material/cancel: Missing Requirements")
            with st.container(border=True):
                miss_skills = data.get('missing_skills', [])
                if miss_skills:
                    cols_m = st.columns(3)
                    for i, m in enumerate(miss_skills):
                        cols_m[i % 3].markdown(f"• {m}")
                else: st.write("All requirements met.")

        with s2:
            st.markdown("#### :material/star: Strengths")
            with st.container(border=True):
                for s in data.get('strengths', []): st.markdown(f"**+** {s}")
            
            st.markdown("#### :material/construction: Improvements")
            with st.container(border=True):
                for i in data.get('improvements', []): st.markdown(f"**-** {i}")

        with s3:
            st.markdown("#### :material/lightbulb: Actionable Suggestions")
            for sug in data.get('ai_suggestions', []):
                st.markdown(f"<div class='sug-box'>{sug}</div>", unsafe_allow_html=True)

    with t2:
        st.markdown("### Talent Leaderboard")
        ranked = sorted(st.session_state.all_results.items(), key=lambda x: x[1]['match_pct'], reverse=True)
        for i, (name, d) in enumerate(ranked):
            m_c = get_match_class(d['match_pct'])
            with st.container(border=True):
                ca, cb = st.columns([4, 1])
                ca.markdown(f"**#{i+1}** {name}")
                cb.markdown(f"<span style='font-weight:800;'>{d['match_pct']}%</span>", unsafe_allow_html=True)
                st.progress(d['match_pct']/100)

    with t3:
        st.markdown("### ATS Structural Audit")
        sel_ats = st.selectbox("Review for", options=list(st.session_state.all_results.keys()), key="ats_sel")
        checks = st.session_state.all_results[sel_ats].get('ats_checks', [])
        for chk in checks:
            if isinstance(chk, dict):
                with st.container(border=True):
                    st.markdown(f"**{chk.get('category', 'Category')}** — {chk.get('status', 'Pending')}")
                    st.caption(chk.get('advice', 'No advice provided.'))

    with t4:
        st.subheader("💬 AI Interaction Vault")
        st.caption("Ask questions about the uploaded resumes or job description.")
        
        # Build context from uploaded resumes
        context_text = "Context from uploaded resumes:\n"
        resume_data = {}
        if res_files:
            for rf in res_files:
                txt = extract_text(rf.getvalue())
                context_text += f"\nResume {rf.name}:\n{txt}\n"
        
        # Chat display
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        
        if prompt := st.chat_input("Ask about candidate experience, skills, or comparisons..."):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            full_prompt = f"{context_text}\n\nUser Question: {prompt}\n\nAnswer concisely based on the context above."
            
            with st.chat_message("assistant"):
                try:
                    response = client.models.generate_content(model="gemini-2.5-flash", contents=full_prompt)
                    st.markdown(response.text)
                    st.session_state.chat_history.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"Chat error: {e}")

else:
    st.info("Analysis triggers will display here.")