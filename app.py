import streamlit as st
from groq import Groq
import PyPDF2
import re

st.set_page_config(page_title="Amal's Medical Brain AI", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #fff0f5; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #ff69b4; color: white; font-weight: bold; height: 3.5em; border: none; transition: 0.3s; }
    .stButton>button:hover { background-color: #d81b60; transform: translateY(-2px); }
    .medical-card { background-color: white; padding: 20px; border-radius: 15px; border-left: 6px solid #ff69b4; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def stream_ai_response(prompt):
    """وظيفة البث السريع للإجابة (Streaming)"""
    response_placeholder = st.empty()
    full_response = ""
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are an elite Medical Professor. Provide high-density, accurate medical insights like Gemini/GPT-4 Turbo. Be concise but highly scientific."},
            {"role": "user", "content": prompt}
        ],
        stream=True,
    )
    for chunk in completion:
        if chunk.choices[0].delta.content:
            full_response += chunk.choices[0].delta.content
            response_placeholder.markdown(full_response + "▌")
    response_placeholder.markdown(full_response)
    return full_response

uploaded_file = st.file_uploader("Upload Lecture (High-Speed Analysis)", type=["pdf"])

if uploaded_file:
    reader = PyPDF2.PdfReader(uploaded_file)
    text = " ".join([p.extract_text() for p in reader.pages[:8]])
    clean_text = re.sub(r'\s+', ' ', text).strip()[:7000]

    if st.button("⚡ High-Yield Turbo Summary"):
        st.session_state.last_result = stream_ai_response(f"Provide an elite, high-density medical summary: {clean_text}")

    if st.button("🩺 USMLE Step 1/2 Expert Logic"):
        st.session_state.last_result = stream_ai_response(f"Extract must-know clinical pearls and USMLE logic from: {clean_text}")

    if st.button("✍️ Interactive IQ Quiz"):
        st.session_state.last_result = stream_ai_response(f"Create 3 complex clinical-vignette USMLE questions: {clean_text}")

    if st.button("🧠 Deep-Recall Flashcards"):
        st.session_state.last_result = stream_ai_response(f"Generate 5 active recall flashcards: {clean_text}")

    st.divider()
    col1, col2 = st.columns(2)
    if 'last_result' in st.session_state:
        with col1:
            if st.button("🌐 Arabic Translation"):
                stream_ai_response(f"Translate this medical text accurately to Arabic: {st.session_state.last_result}")
        with col2:
            if st.button("🌐 Hebrew Translation"):
                stream_ai_response(f"Translate this medical text accurately to Hebrew: {st.session_state.last_result}")

st.sidebar.title("🔗 Quick Links")
topic = uploaded_file.name.replace(".pdf", "") if uploaded_file else "Medicine"
st.sidebar.markdown(f"[🎬 YouTube Expert Videos](https://youtube.com{topic}+medical+lecture)")
st.sidebar.markdown(f"[🖼️ Google Medical Diagrams](https://google.com{topic}+anatomy+diagram)")
