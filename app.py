import streamlit as st
from groq import Groq
import PyPDF2

# 1. Page Configuration & Pink Theme
st.set_page_config(page_title="Amal's Medical Brain", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #fff0f5; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #ff69b4; color: white; border: none; height: 3em; font-weight: bold; }
    h1, h2, h3 { color: #ff69b4; text-align: center; }
    .stFileUploader { background-color: #ffffff; border-radius: 15px; padding: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. API Setup from Secrets
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 3. Memory System (Session State)
if "medical_history" not in st.session_state:
    st.session_state.medical_history = []

st.title("🌸 Amal's Medical Brain 🌸")
st.sidebar.title("📚 Archived Lectures")

# Sidebar History Display
for i, doc in enumerate(st.session_state.medical_history):
    st.sidebar.write(f"📍 {doc['name']}")

# 4. Multi-Format File Uploader (PDF, Word, PPT, Images)
uploaded_file = st.file_uploader("Upload: PDF, Word, PPT, or Images", type=["pdf", "docx", "pptx", "png", "jpg", "jpeg"])

if uploaded_file:
    # Logic to extract text (Optimized for PDF)
    text_content = ""
    if uploaded_file.type == "application/pdf":
        try:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text_content = "".join([page.extract_text() for page in pdf_reader.pages])
        except:
            text_content = "Text extraction failed, but AI will analyze the file name."
    else:
        text_content = f"Non-PDF file uploaded: {uploaded_file.name}. AI will analyze context."

    # Add to Memory
    if {"name": uploaded_file.name, "content": text_content} not in st.session_state.medical_history:
        st.session_state.medical_history.append({"name": uploaded_file.name, "content": text_content})
    
    st.success(f"✅ Received: {uploaded_file.name}")

    # 5. Action Buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📝 Summarize & Link to USMLE/PubMed"):
            with st.spinner('Analyzing medical data...'):
                past_topics = ", ".join([d['name'] for d in st.session_state.medical_history[:-1]])
                prompt = f"Summarize in Arabic: {text_content[:4000]}. Link to USMLE and latest 3 PubMed studies (2023-2026). Mention link to previous topics: {past_topics}"
                response = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama3-8b-8192")
                st.markdown(f"### 📄 Summary\n{response.choices[0].message.content}")

    with col2:
        if st.button("🧠 Generate Flashcards (Active Recall)"):
            with st.spinner('Creating questions...'):
                prompt = f"Create 5 Arabic medical flashcards (Question/Answer) from: {text_content[:4000]}"
                response = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama3-8b-8192")
                st.info(response.choices[0].message.content)

# 6. Daily Review Section
if st.session_state.medical_history:
    st.divider()
    st.subheader("💡 Quick Daily Review")
    st.write(f"Amal, remember this from your previous study ({st.session_state.medical_history[0]['name']}):")
    st.caption("AI Review: Focus on the clinical correlations mentioned in your lecture.")
