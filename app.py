import streamlit as st
from groq import Groq
import pdfplumber

# 1. Page Styling (Pink & Professional)
st.set_page_config(page_title="Amal's Medical Brain", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #fff0f5; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #ff69b4; color: white; font-weight: bold; border: none; }
    h1, h2, h3 { color: #ff69b4; }
    </style>
    """, unsafe_allow_html=True)

# 2. API Setup
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "medical_history" not in st.session_state:
    st.session_state.medical_history = []

st.title("🌸 Amal's Medical Brain 🌸")
st.sidebar.title("📚 Course History")

# 3. Enhanced File Uploader
uploaded_file = st.file_uploader("Upload Medical Lecture (PDF, PPTX, DOCX)", type=["pdf", "docx", "pptx"])

if uploaded_file:
    extracted_text = ""
    try:
        # استخدام pdfplumber لأنه الأفضل في التعامل مع العبري والإنجليزي المتداخل
        with pdfplumber.open(uploaded_file) as pdf:
            # قراءة أول 4 صفحات لضمان الدقة وعدم تخطي الحجم
            for page in pdf.pages[:4]:
                extracted_text += page.extract_text() or ""
    except:
        extracted_text = "Complex layout detected. AI will focus on metadata."

    # تنظيف النص لضمان قبول الـ API له
    clean_text = extracted_text[:4000] 

    st.success(f"Loaded: {uploaded_file.name}")

    # 4. Action Buttons (The core features you loved)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📝 Summarize & USMLE"):
            with st.spinner('Analyzing...'):
                prompt = f"Summarize this medical content. Highlight USMLE high-yield points and link to relevant PubMed studies: {clean_text}"
                resp = client.chat.completions.create(messages=[{"role":"user","content":prompt}], model="llama3-8b-8192")
                st.markdown(resp.choices[0].message.content)

    with col2:
        if st.button("🧠 Active Recall Flashcards"):
            with st.spinner('Generating Cards...'):
                prompt = f"Create 5 high-yield medical flashcards (Question/Answer) from this text: {clean_text}"
                resp = client.chat.completions.create(messages=[{"role":"user","content":prompt}], model="llama3-8b-8192")
                st.info(resp.choices[0].message.content)

    with col3:
        if st.button("❓ Detailed Q&A"):
            with st.spinner('Creating Q&A...'):
                prompt = f"Convert the following into a detailed Question and Answer format for study: {clean_text}"
                resp = client.chat.completions.create(messages=[{"role":"user","content":prompt}], model="llama3-8b-8192")
                st.write(resp.choices[0].message.content)

    # 5. Interactive Chat for specific questions
    st.divider()
    user_q = st.text_input("💬 Ask any specific question about this lecture:")
    if user_q:
        with st.spinner('Thinking...'):
            resp = client.chat.completions.create(
                messages=[{"role":"user","content":f"Based on the lecture text: {clean_text}, answer this: {user_q}"}],
                model="llama3-8b-8192"
            )
            st.chat_message("assistant").write(resp.choices[0].message.content)

# 6. Sidebar update
if uploaded_file and uploaded_file.name not in [d['name'] for d in st.session_state.medical_history]:
    st.session_state.medical_history.append({"name": uploaded_file.name})
