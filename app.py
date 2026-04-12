import streamlit as st
from groq import Groq
import PyPDF2

# 1. Page Config
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

if "medical_history" not in st.session_state:
    st.session_state.medical_history = []

st.title("🌸 Amal's Medical Brain 🌸")
st.sidebar.title("📚 Archived Lectures")
for doc in st.session_state.medical_history:
    st.sidebar.write(f"📍 {doc['name']}")

# 3. File Uploader
uploaded_file = st.file_uploader("Upload Lecture", type=["pdf", "docx", "pptx"])

if uploaded_file:
    # استخراج النص بحذر شديد
    raw_text = ""
    try:
        reader = PyPDF2.PdfReader(uploaded_file)
        # رح ناخد أول 3 صفحات فقط لأنها الأهم ولضمان عدم تجاوز الحجم
        for page in reader.pages[:3]:
            content = page.extract_text()
            if content:
                raw_text += content
    except:
        raw_text = "Error reading PDF"

    # تنظيف النص وتحديده بـ 2500 حرف فقط لضمان استقرار الخدمة
    final_text = raw_text[:2500] if raw_text else "No text found"

    if {"name": uploaded_file.name} not in st.session_state.medical_history:
        st.session_state.medical_history.append({"name": uploaded_file.name})
    
    st.success(f"✅ Active: {uploaded_file.name}")

    # 4. Control Buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📝 Summarize"):
            with st.spinner('Summarizing...'):
                try:
                    resp = client.chat.completions.create(
                        messages=[{"role":"user","content":f"Summarize this medical text in Arabic: {final_text}"}],
                        model="llama3-8b-8192"
                    )
                    st.markdown(resp.choices[0].message.content)
                except:
                    st.error("Text still too large. Try a shorter PDF.")

    with col2:
        if st.button("❓ Q&A Mode"):
            with st.spinner('Generating...'):
                try:
                    resp = client.chat.completions.create(
                        messages=[{"role":"user","content":f"Convert to Arabic Q&A: {final_text}"}],
                        model="llama3-8b-8192"
                    )
                    st.info(resp.choices[0].message.content)
                except:
                    st.error("Error generating Q&A.")

    with col3:
        if st.button("🧠 Flashcards"):
            with st.spinner('Creating...'):
                try:
                    resp = client.chat.completions.create(
                        messages=[{"role":"user","content":f"Create 3 flashcards in Arabic: {final_text}"}],
                        model="llama3-8b-8192"
                    )
                    st.warning(resp.choices[0].message.content)

    # 5. Chat Interface
    st.divider()
    user_q = st.text_input("💬 اسألي أي سؤال عن المحاضرة:")
    if user_q:
        try:
            resp = client.chat.completions.create(
                messages=[{"role":"user","content":f"Text: {final_text}\nQuestion: {user_q}"}],
                model="llama3-8b-8192"
            )
            st.chat_message("assistant").write(resp.choices[0].message.content)
        except:
            st.error("Could not process question.")
