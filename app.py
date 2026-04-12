import streamlit as st
from groq import Groq
import pdfplumber
import re

# 1. Page Styling
st.set_page_config(page_title="Amal's Medical Brain", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #fff0f5; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #ff69b4; color: white; font-weight: bold; border: none; }
    h1, h2, h3 { color: #ff69b4; }
    </style>
    """, unsafe_allow_html=True)

# 2. Setup
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "medical_history" not in st.session_state:
    st.session_state.medical_history = []

st.title("🌸 Amal's Medical Brain 🌸")
st.sidebar.title("📚 Course History")

# 3. Enhanced File Uploader
uploaded_file = st.file_uploader("Upload Medical Lecture", type=["pdf", "docx", "pptx"])

if uploaded_file:
    raw_text = ""
    try:
        with pdfplumber.open(uploaded_file) as pdf:
            # نكتفي بأول صفحتين لضمان عدم حدوث Error بسبب الحجم أو الرموز
            for page in pdf.pages[:2]:
                raw_text += page.extract_text() or ""
    except:
        raw_text = "Processing error"

    # أهم خطوة: تنظيف النص من أي رمز غريب (إبقاء الحروف والأرقام فقط)
    clean_text = re.sub(r'[^\x00-\x7F]+', ' ', raw_text)[:2000]

    st.success(f"Loaded: {uploaded_file.name}")

    # 4. Action Buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📝 Summarize"):
            with st.spinner('Summarizing...'):
                try:
                    resp = client.chat.completions.create(
                        messages=[{"role":"user","content":f"Summarize this medical text in Arabic (keep medical terms in English): {clean_text}"}],
                        model="llama3-8b-8192"
                    )
                    st.markdown(resp.choices[0].message.content)
                except:
                    st.error("Text still contains invalid characters. Try another part.")

    with col2:
        if st.button("🧠 Flashcards"):
            with st.spinner('Creating...'):
                try:
                    resp = client.chat.completions.create(
                        messages=[{"role":"user","content":f"Create 3 USMLE flashcards from: {clean_text}"}],
                        model="llama3-8b-8192"
                    )
                    st.info(resp.choices[0].message.content)
                except:
                    st.error("Flashcards failed.")

    with col3:
        if st.button("❓ Detailed Q&A"):
            with st.spinner('Thinking...'):
                try:
                    resp = client.chat.completions.create(
                        messages=[{"role":"user","content":f"Create a Q&A from this text: {clean_text}"}],
                        model="llama3-8b-8192"
                    )
                    st.write(resp.choices[0].message.content)
                except:
                    st.error("Q&A failed.")

    # 5. Direct Question (Chat)
    st.divider()
    user_q = st.text_input("💬 Ask about any medical concept (e.g. Porphyrias):")
    if user_q:
        with st.spinner('Searching Brain...'):
            resp = client.chat.completions.create(
                messages=[{"role":"user","content":f"Answer this medical question clearly: {user_q}"}],
                model="llama3-8b-8192"
            )
            st.chat_message("assistant").write(resp.choices[0].message.content)
