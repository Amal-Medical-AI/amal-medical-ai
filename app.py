import streamlit as st
from groq import Groq
import fitz  # PyMuPDF
import re

# 1. Page Config & Styling
st.set_page_config(page_title="Amal's Medical Brain", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #fff0f5; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #ff69b4; color: white; font-weight: bold; border: none; height: 3em; }
    h1, h2, h3 { color: #ff69b4; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# 2. Setup
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "medical_history" not in st.session_state:
    st.session_state.medical_history = []

st.title("🌸 Amal's Medical Brain 🌸")

# 3. File Uploader
uploaded_file = st.file_uploader("Upload Lecture (PDF)", type=["pdf"])

if uploaded_file:
    full_text = ""
    try:
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
            for page in doc:
                full_text += page.get_text()
        st.success(f"✅ Loaded: {uploaded_file.name}")
    except:
        st.error("Error reading file. I will use general knowledge to help you.")

    # تنظيف النص لإرساله للذكاء الاصطناعي
    clean_text = re.sub(r'[^a-zA-Z0-9\s\u0590-\u05FF]', '', full_text)[:3000]

    # 4. الأزرار - كل زر له مهمة منفصلة
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📝 Summary & USMLE"):
            with st.spinner('Summarizing...'):
                prompt = f"Summarize this and link to USMLE High-yield: {clean_text}"
                resp = client.chat.completions.create(messages=[{"role":"user","content":prompt}], model="llama3-70b-8192")
                st.markdown(resp.choices[0].message.content)

    with col2:
        if st.button("🧠 Flashcards (Active Recall)"):
            with st.spinner('Creating Cards...'):
                prompt = f"Create 5 medical flashcards (Q&A) from: {clean_text}"
                resp = client.chat.completions.create(messages=[{"role":"user","content":prompt}], model="llama3-70b-8192")
                st.info(resp.choices[0].message.content)

    with col3:
        if st.button("🔍 PubMed & Research"):
            with st.spinner('Searching Research...'):
                prompt = f"Find 3 PubMed research topics (2024-2026) related to this material: {clean_text}"
                resp = client.chat.completions.create(messages=[{"role":"user","content":prompt}], model="llama3-70b-8192")
                st.warning(resp.choices[0].message.content)

    # 5. مربع الدردشة (للأسئلة المباشرة)
    st.divider()
    st.subheader("💬 Chat with your Lecture")
    user_q = st.text_input("Ask a specific question (e.g., Explain the Porphyrias):")
    if user_q:
        with st.spinner('Thinking...'):
            resp = client.chat.completions.create(
                messages=[{"role":"user","content":f"Context: {clean_text}\nQuestion: {user_q}"}],
                model="llama3-70b-8192"
            )
            st.chat_message("assistant").write(resp.choices[0].message.content)

# 6. تذكير المراجعة (الذاكرة)
if uploaded_file:
    st.sidebar.success(f"Archived: {uploaded_file.name}")
    st.sidebar.write("💡 Reminder: Review the rate-limiting enzyme from this lecture today!")
