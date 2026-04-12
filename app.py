import streamlit as st
from groq import Groq
import PyPDF2

# 1. إعدادات الصفحة والتصميم
st.set_page_config(page_title="Amal's Medical Brain", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #fff0f5; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #ff69b4; color: white; font-weight: bold; }
    h1, h2, h3 { color: #ff69b4; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# 2. تشغيل المحرك
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "medical_history" not in st.session_state:
    st.session_state.medical_history = []

st.title("🌸 Amal's Medical Brain 🌸")
st.sidebar.title("📚 Archived Lectures")
for doc in st.session_state.medical_history:
    st.sidebar.write(f"📍 {doc['name']}")

# 3. رفع الملفات
uploaded_file = st.file_uploader("Upload Lecture", type=["pdf", "docx", "pptx"])

if uploaded_file:
    # استخراج النص بذكاء (أول 3 صفحات لتجنب الخطأ)
    raw_text = ""
    try:
        reader = PyPDF2.PdfReader(uploaded_file)
        pages_to_read = min(len(reader.pages), 3)
        for i in range(pages_to_read):
            page_content = reader.pages[i].extract_text()
            if page_content:
                raw_text += page_content
    except:
        raw_text = "Error reading file content."

    final_text = raw_text[:3000] if raw_text else "No content found."

    if {"name": uploaded_file.name} not in st.session_state.medical_history:
        st.session_state.medical_history.append({"name": uploaded_file.name})
    
    st.success(f"✅ Active: {uploaded_file.name}")

    # 4. الأزرار الثلاثة
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📝 Summarize"):
            with st.spinner('Working...'):
                resp = client.chat.completions.create(
                    messages=[{"role":"user","content":f"Summarize in Arabic: {final_text}"}],
                    model="llama3-8b-8192"
                )
                st.markdown(resp.choices[0].message.content)

    with col2:
        if st.button("❓ Q&A Mode"):
            with st.spinner('Working...'):
                resp = client.chat.completions.create(
                    messages=[{"role":"user","content":f"Create Arabic Q&A from: {final_text}"}],
                    model="llama3-8b-8192"
                )
                st.info(resp.choices[0].message.content)

    with col3:
        if st.button("🧠 Flashcards"):
            with st.spinner('Working...'):
                resp = client.chat.completions.create(
                    messages=[{"role":"user","content":f"Create 3 Arabic flashcards from: {final_text}"}],
                    model="llama3-8b-8192"
                )
                st.warning(resp.choices[0].message.content)

    # 5. دردشة مباشرة مع المادة
    st.divider()
    user_q = st.text_input("💬 اسألي أي سؤال عن هذه المحاضرة:")
    if user_q:
        with st.spinner('Thinking...'):
            resp = client.chat.completions.create(
                messages=[{"role":"user","content":f"Context: {final_text}\nQuestion: {user_q}"}],
                model="llama3-8b-8192"
            )
            st.chat_message("assistant").write(resp.choices[0].message.content)

# 6. تذكير المراجعة
if st.session_state.medical_history:
    st.divider()
    st.caption("AI: Ready for your next study session, Amal!")
