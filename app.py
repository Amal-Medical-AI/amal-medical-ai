import streamlit as st
from groq import Groq
import PyPDF2

# 1. Page Configuration & Theme
st.set_page_config(page_title="Amal's Medical Brain", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #fff0f5; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #ff69b4; color: white; border: none; font-weight: bold; }
    h1, h2, h3 { color: #ff69b4; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# 2. API Setup
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 3. Memory & History
if "medical_history" not in st.session_state:
    st.session_state.medical_history = []
if "current_text" not in st.session_state:
    st.session_state.current_text = ""

st.title("🌸 Amal's Medical Brain 🌸")
st.sidebar.title("📚 Archived Lectures")
for doc in st.session_state.medical_history:
    st.sidebar.write(f"📍 {doc['name']}")

# 4. File Uploader
uploaded_file = st.file_uploader("Upload Lecture (PDF, Word, PPT)", type=["pdf", "docx", "pptx"])

if uploaded_file:
    if st.session_state.current_text == "":
        if uploaded_file.type == "application/pdf":
            reader = PyPDF2.PdfReader(uploaded_file)
            st.session_state.current_text = "".join([p.extract_text() for p in reader.pages[:5]])
        
        if {"name": uploaded_file.name} not in st.session_state.medical_history:
            st.session_state.medical_history.append({"name": uploaded_file.name})
    
    st.success(f"✅ Active File: {uploaded_file.name}")

    # 5. Control Buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📝 Summarize & USMLE"):
            with st.spinner('Analyzing...'):
                prompt = f"Summarize in Arabic, link to USMLE and PubMed: {st.session_state.current_text[:4000]}"
                resp = client.chat.completions.create(messages=[{"role":"user","content":prompt}], model="llama3-8b-8192")
                st.markdown(resp.choices[0].message.content)

    with col2:
        if st.button("❓ Full Q&A Mode"):
            with st.spinner('Generating Questions...'):
                prompt = f"Convert this text into a comprehensive Q&A in Arabic: {st.session_state.current_text[:4000]}"
                resp = client.chat.completions.create(messages=[{"role":"user","content":prompt}], model="llama3-8b-8192")
                st.info(resp.choices[0].message.content)

    with col3:
        if st.button("🧠 Flashcards"):
            with st.spinner('Creating Cards...'):
                prompt = f"Create 5 medical flashcards in Arabic from: {st.session_state.current_text[:3000]}"
                resp = client.chat.completions.create(messages=[{"role":"user","content":prompt}], model="llama3-8b-8192")
                st.warning(resp.choices[0].message.content)

    # 6. Chat Interface (اسألي أي سؤال عن المادة)
    st.divider()
    user_question = st.text_input("💬 اسألي أي سؤال إضافي عن هذه المحاضرة:")
    if user_question:
        with st.spinner('Thinking...'):
            chat_prompt = f"Based on this text: {st.session_state.current_text[:4000]}, answer Amal's question in Arabic: {user_question}"
            resp = client.chat.completions.create(messages=[{"role":"user","content":chat_prompt}], model="llama3-8b-8192")
            st.chat_message("assistant").write(resp.choices[0].message.content)

# 7. Daily Review
if st.session_state.medical_history:
    st.divider()
    st.subheader("💡 Quick Daily Review")
    st.caption("AI: Don't forget to review the key clinical correlations from your history!")
