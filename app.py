import streamlit as st
from groq import Groq
import PyPDF2
import re

# 1. Theme & Professional Look
st.set_page_config(page_title="Amal's Medical Brain", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #fff0f5; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #ff69b4; color: white; font-weight: bold; height: 3.5em; border: none; }
    h1, h3 { color: #ff69b4; text-align: center; font-family: 'Arial'; }
    .stTextInput>div>div>input { border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Setup
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.title("🌸 Amal's Medical Brain 🌸")

# 3. File Handler
uploaded_file = st.file_uploader("Upload Medical Slides", type=["pdf"])

if uploaded_file:
    raw_text = ""
    try:
        reader = PyPDF2.PdfReader(uploaded_file)
        # نأخذ أول 5 صفحات لضمان شمولية المادة وثبات الموقع
        for page in reader.pages[:5]:
            raw_text += page.extract_text() + " "
        st.success(f"Successfully Loaded: {uploaded_file.name}")
    except:
        st.error("Error reading PDF content.")

    # تنظيف النص لضمان عدم حدوث Error
    clean_text = re.sub(r'[^a-zA-Z0-9\s\u0590-\u05FF]', '', raw_text)[:3500]

    # 4. الميزات الأساسية (الأزرار الثلاثة)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📝 Summarize & USMLE"):
            with st.spinner('Analyzing...'):
                prompt = f"Summarize this and link to USMLE & PubMed 2024-2026: {clean_text}"
                resp = client.chat.completions.create(messages=[{"role":"user","content":prompt}], model="llama3-70b-8192")
                st.markdown(resp.choices[0].message.content)

    with col2:
        # خيار التعلم عن طريق الأسئلة اللي كان يختفي
        if st.button("❓ Q&A Learning Mode"):
            with st.spinner('Generating Questions...'):
                prompt = f"Create a detailed Q&A for learning from this material: {clean_text}"
                resp = client.chat.completions.create(messages=[{"role":"user","content":prompt}], model="llama3-70b-8192")
                st.info(resp.choices[0].message.content)

    with col3:
        if st.button("🧠 Flashcards"):
            with st.spinner('Creating Cards...'):
                prompt = f"Create 5 active recall flashcards from: {clean_text}"
                resp = client.chat.completions.create(messages=[{"role":"user","content":prompt}], model="llama3-70b-8192")
                st.warning(resp.choices[0].message.content)

    # 5. مربع السؤال المباشر
    st.divider()
    st.subheader("💬 Ask Amal's AI Assistant")
    user_input = st.text_input("Ask any medical question about this lecture...")
    if user_input:
        with st.spinner('Thinking...'):
            resp = client.chat.completions.create(
                messages=[{"role":"user","content":f"Context: {clean_text}\nQuestion: {user_input}"}],
                model="llama3-70b-8192"
            )
            st.chat_message("assistant").write(resp.choices[0].message.content)
