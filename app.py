import streamlit as st
from groq import Groq
import pdfplumber
import re

# 1. التصميم الزهري
st.set_page_config(page_title="Amal's Medical Brain", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #fff0f5; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #ff69b4; color: white; font-weight: bold; }
    h1, h2, h3 { color: #ff69b4; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# 2. إعداد المحرك
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "medical_history" not in st.session_state:
    st.session_state.medical_history = []

st.title("🌸 Amal's Medical Brain 🌸")

# 3. رفع الملفات
uploaded_file = st.file_uploader("Upload Lecture (Slides)", type=["pdf"])

if uploaded_file:
    raw_text = ""
    try:
        with pdfplumber.open(uploaded_file) as pdf:
            # نكتفي بأول صفحتين فقط لأنها تحتوي على أهم الخلاصة
            for page in pdf.pages[:2]:
                text = page.extract_text()
                if text:
                    raw_text += text + " "
    except:
        raw_text = "Error reading file."

    # أهم خطوة: الفلتر الفولاذي (إبقاء الحروف والأرقام فقط ومسح الرموز الكيميائية المعقدة)
    # هاد السطر هو اللي رح يمنع الـ Error الأحمر للأبد
    clean_text = re.sub(r'[^a-zA-Z0-9\s\u0590-\u05FF]', '', raw_text)[:2000]

    st.success(f"✅ Loaded: {uploaded_file.name}")

    # 4. الأزرار
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📝 Summarize Material"):
            with st.spinner('Analyzing...'):
                try:
                    # نستخدم موديل 70b لأنه أذكى في التعامل مع المصطلحات الطبية
                    resp = client.chat.completions.create(
                        messages=[{"role":"user","content":f"Summarize this medical text in English/Arabic: {clean_text}"}],
                        model="llama3-70b-8192"
                    )
                    st.markdown(resp.choices[0].message.content)
                except:
                    st.error("Text still too complex. Use the chat box below!")

    with col2:
        if st.button("🧠 Q&A Mode"):
            with st.spinner('Generating...'):
                try:
                    resp = client.chat.completions.create(
                        messages=[{"role":"user","content":f"Create 3 medical Q&As from: {clean_text}"}],
                        model="llama3-70b-8192"
                    )
                    st.info(resp.choices[0].message.content)
                except:
                    st.error("Could not generate Q&A for this file.")

    # 5. مربع الشات (المنقذ الدائم)
    st.divider()
    st.subheader("💬 Ask anything (If buttons fail, I'm here):")
    user_q = st.text_input("Ask a question about Heme Metabolism...")
    if user_q:
        with st.spinner('Searching...'):
            resp = client.chat.completions.create(
                messages=[{"role":"user","content":user_q}],
                model="llama3-70b-8192"
            )
            st.chat_message("assistant").write(resp.choices[0].message.content)
