import streamlit as st
from groq import Groq
import PyPDF2

# Page Config
st.set_page_config(page_title="Amal's Medical Brain", layout="wide")

# Custom Design (Pink Theme)
st.markdown("""
    <style>
    .main { background-color: #fff0f5; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #ff69b4; color: white; border: none; }
    h1, h2, h3 { color: #ff69b4; }
    </style>
    """, unsafe_allow_html=True)

# API Setup
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Memory System
if "medical_history" not in st.session_state:
    st.session_state.medical_history = []

st.title("🌸 Amal's Medical Brain 🌸")
st.sidebar.title("📚 Archived Lectures")

# Sidebar History
for i, doc in enumerate(st.session_state.medical_history):
    st.sidebar.write(f"{i+1}. {doc['name']}")

uploaded_file = st.file_uploader("Upload Technion Lecture (PDF)", type="pdf")

if uploaded_file:
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    text_content = "".join([page.extract_text() for page in pdf_reader.pages])
    
    if {"name": uploaded_file.name, "content": text_content} not in st.session_state.medical_history:
        st.session_state.medical_history.append({"name": uploaded_file.name, "content": text_content})
    
    st.success(f"Successfully added: {uploaded_file.name}")

    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📝 Summarize & Link to USMLE"):
            with st.spinner('Analyzing...'):
                past_topics = ", ".join([d['name'] for d in st.session_state.medical_history[:-1]])
                prompt = f"Summarize this in Arabic: {text_content[:4000]}. Link it to USMLE and find 3 PubMed studies (2023-2026). Note: Amal previously studied {past_topics}, link this new material to them."
                response = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama3-8b-8192")
                st.markdown(response.choices[0].message.content)

    with col2:
        if st.button("🧠 Generate Flashcards"):
            with st.spinner('Creating Questions...'):
                prompt = f"Create 5 flashcards (Question/Answer) in Arabic from this text: {text_content[:4000]}"
                response = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama3-8b-8192")
                st.info(response.choices[0].message.content)

# Daily Review Section
if st.session_state.medical_history:
    st.divider()
    st.subheader("💡 Quick Daily Review")
    st.write(f"Amal, don't forget to review this from ({st.session_state.medical_history[0]['name']}):")
    st.caption("AI will pick a random point from your history here.")
