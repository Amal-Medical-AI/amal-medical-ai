import streamlit as st
from groq import Groq
import PyPDF2
import re

# 1. Styling
st.set_page_config(page_title="Amal's Medical Brain", layout="wide")
st.markdown("<style>.main { background-color: #fff0f5; } .stButton>button { background-color: #ff69b4; color: white; border-radius: 20px; font-weight: bold; height: 3em; }</style>", unsafe_allow_html=True)

# 2. API Setup
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.title("🌸 Amal's Medical Brain 🌸")

uploaded_file = st.file_uploader("Upload Lecture (PDF)", type=["pdf"])

if uploaded_file:
    # قراءة النص بأبسط وأخف طريقة ممكنة لمنع الـ Connection Error
    text = ""
    try:
        reader = PyPDF2.PdfReader(uploaded_file)
        for page in reader.pages[:4]: # نكتفي بأول 4 صفحات لضمان السرعة
            text += page.extract_text() + " "
        st.success(f"✅ Loaded: {uploaded_file.name}")
    except:
        st.error("Error reading PDF. Use the Chat below.")

    # تنظيف النص من "الألغام" البرمجية
    clean_text = re.sub(r'[^a-zA-Z0-9\s\u0590-\u05FF]', '', text)[:3000]

    # 3. الميزات الثلاث (الأزرار)
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📝 Summarize & USMLE"):
            with st.spinner('Summarizing...'):
                prompt = f"Summarize this and link to USMLE High-yield: {clean_text}"
                resp = client.chat.completions.create(messages=[{"role":"user","content":prompt}], model="llama3-70b-8192")
                st.markdown(resp.choices[0].message.content)

    with col2:
        if st.button("🧠 Flashcards"):
            with st.spinner('Creating Cards...'):
                prompt = f"Create 5 medical flashcards from: {clean_text}"
                resp = client.chat.completions.create(messages=[{"role":"user","content":prompt}], model="llama3-70b-8192")
                st.info(resp.choices[0].message.content)

    # 4. الدردشة المباشرة (المنقذ الدائم)
    st.divider()
    st.subheader("💬 Ask anything (Best for complex slides)")
    user_q = st.text_input("Example: Explain the steps of Heme Synthesis")
    if user_q:
        with st.spinner('Answering...'):
            resp = client.chat.completions.create(
                messages=[{"role":"user","content":f"Context: {clean_text}\nQuestion: {user_q}"}],
                model="llama3-70b-8192"
            )
            st.chat_message("assistant").write(resp.choices[0].message.content)
