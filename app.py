import streamlit as st
from groq import Groq
import pdfplumber

# 1. Page Setup
st.set_page_config(page_title="Amal's Medical Brain", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #fff0f5; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #ff69b4; color: white; font-weight: bold; }
    h1, h2, h3 { color: #ff69b4; }
    </style>
    """, unsafe_allow_html=True)

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "medical_history" not in st.session_state:
    st.session_state.medical_history = []

st.title("🌸 Amal's Medical Brain 🌸")
st.sidebar.title("📚 Course History")

# 2. File Uploader
uploaded_file = st.file_uploader("Upload Technion Slides", type=["pdf"])

if uploaded_file:
    extracted_text = ""
    try:
        # استخدام pdfplumber لأنه الأفضل في التعامل مع السلايدات والجداول
        with pdfplumber.open(uploaded_file) as pdf:
            # نكتفي بأول 5 سلايدات لضمان عدم حدوث Error بسبب حجم البيانات
            for page in pdf.pages[:5]:
                text = page.extract_text()
                if text:
                    extracted_text += text + "\n"
    except:
        extracted_text = "Complex slide layout detected."

    # تنظيف النص من الرموز الغريبة اللي بتخرب الـ API
    clean_text = "".join(char for char in extracted_text if ord(char) < 65535)[:3000]

    st.success(f"Loaded: {uploaded_file.name}")

    # 3. Action Buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📝 Summarize & USMLE"):
            with st.spinner('Summarizing...'):
                prompt = f"Analyze these medical slides. Extract high-yield USMLE info and PubMed links. Respond in English (medical) and Arabic (explanation): {clean_text}"
                resp = client.chat.completions.create(messages=[{"role":"user","content":prompt}], model="llama3-8b-8192")
                st.markdown(resp.choices[0].message.content)

    with col2:
        if st.button("🧠 Q&A Mode"):
            with st.spinner('Creating Questions...'):
                prompt = f"Based on these slides, create 5 important Questions and Answers for a medical exam: {clean_text}"
                resp = client.chat.completions.create(messages=[{"role":"user","content":prompt}], model="llama3-8b-8192")
                st.info(resp.choices[0].message.content)

    with col3:
        if st.button("🃏 Flashcards"):
            with st.spinner('Creating Cards...'):
                prompt = f"Create 3 active recall flashcards from: {clean_text}"
                resp = client.chat.completions.create(messages=[{"role":"user","content":prompt}], model="llama3-8b-8192")
                st.warning(resp.choices[0].message.content)

    # 4. Chat Interface
    st.divider()
    user_q = st.text_input("💬 Ask about any slide content (e.g., Porphyria Cutanea Tarda):")
    if user_q:
        resp = client.chat.completions.create(
            messages=[{"role":"user","content":f"Based on: {clean_text}, answer: {user_q}"}],
            model="llama3-8b-8192"
        )
        st.chat_message("assistant").write(resp.choices[0].message.content)
