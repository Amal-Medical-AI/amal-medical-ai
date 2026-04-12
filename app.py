import streamlit as st
from groq import Groq
import PyPDF2

# 1. Config
st.set_page_config(page_title="Amal's Medical Brain", layout="wide")
st.markdown("<style>.main { background-color: #fff0f5; } .stButton>button { background-color: #ff69b4; color: white; border-radius: 20px; font-weight: bold; }</style>", unsafe_allow_html=True)

# 2. Setup
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "medical_history" not in st.session_state:
    st.session_state.medical_history = []

st.title("🌸 Amal's Medical Brain 🌸")

# 3. Uploader
uploaded_file = st.file_uploader("Upload Lecture", type=["pdf", "docx", "pptx"])

if uploaded_file:
    # استخراج النص بطريقة "آمنة" جداً
    raw_text = ""
    try:
        reader = PyPDF2.PdfReader(uploaded_file)
        # نكتفي بأول صفحتين فقط لضمان عدم حدوث Error
        for i in range(min(len(reader.pages), 2)):
            raw_text += reader.pages[i].extract_text()
    except:
        raw_text = ""

    # تنظيف النص من أي رموز غريبة قد تسبب Error
    clean_text = "".join(i for i in raw_text if i.isalnum() or i.isspace())[:2000]

    if {"name": uploaded_file.name} not in st.session_state.medical_history:
        st.session_state.medical_history.append({"name": uploaded_file.name})
    
    st.success(f"✅ Loaded: {uploaded_file.name}")

    # 4. Buttons with Error Handling
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📝 Summarize"):
            with st.spinner('Processing...'):
                try:
                    resp = client.chat.completions.create(
                        messages=[{"role":"user","content":f"Summarize this medical text in Arabic: {clean_text}"}],
                        model="llama3-8b-8192"
                    )
                    st.markdown(resp.choices[0].message.content)
                except:
                    st.error("أمل، النص في هذا الملف معقد برمجياً. جربي سؤالي عنه في الأسفل 👇")

    with col2:
        if st.button("❓ Q&A Mode"):
            with st.spinner('Generating...'):
                try:
                    resp = client.chat.completions.create(
                        messages=[{"role":"user","content":f"Create 3 Q&A in Arabic from: {clean_text}"}],
                        model="llama3-8b-8192"
                    )
                    st.info(resp.choices[0].message.content)
                except:
                    st.error("عذراً، لم أستطع تحويل هذا الملف لأسئلة. جربي ملفاً آخر.")

    # 5. الشات المباشر (أقوى ميزة حالياً)
    st.divider()
    st.subheader("💬 اسألي 'دماغك الطبي' عن أي معلومة")
    user_input = st.text_input("مثلاً: اشرحي لي دور الـ ALAS1 في تصنيع الهيم؟")
    if user_input:
        try:
            resp = client.chat.completions.create(
                messages=[{"role":"user","content":f"Answer this medical question in Arabic: {user_input}"}],
                model="llama3-8b-8192"
            )
            st.chat_message("assistant").write(resp.choices[0].message.content)
        except:
            st.error("حاولت الإجابة ولكن هناك ضغط على الخدمة. جربي بعد لحظات.")
