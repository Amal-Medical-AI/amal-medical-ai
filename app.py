import streamlit as st
from groq import Groq
import PyPDF2
import re

# 1. إعدادات الصفحة والستايل الطبي
st.set_page_config(page_title="Amal's Medical Brain", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #fff0f5; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #ff69b4; color: white; font-weight: bold; height: 3em; border: none; }
    h1, h3 { color: #ff69b4; text-align: center; }
    .translation-box { background-color: #ffffff; padding: 20px; border-radius: 15px; border: 2px solid #ff69b4; color: #333; margin-top: 15px; }
    </style>
    """, unsafe_allow_html=True)

# 2. إعداد الـ API والذاكرة
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "lecture_memory" not in st.session_state:
    st.session_state.lecture_memory = []
if "last_result" not in st.session_state:
    st.session_state.last_result = "" 

st.title("🌸 Amal's Medical Brain 🌸")

# 3. القائمة الجانبية
st.sidebar.title("🧠 Study Memory")
if st.session_state.lecture_memory:
    for item in st.session_state.lecture_memory:
        st.sidebar.write(f"📖 {item['name']}")

# 4. معالج الملفات
uploaded_file = st.file_uploader("Upload Medical Lecture (PDF)", type=["pdf"])

if uploaded_file:
    raw_text = ""
    try:
        reader = PyPDF2.PdfReader(uploaded_file)
        pages_to_read = min(len(reader.pages), 6)
        for i in range(pages_to_read):
            raw_text += reader.pages[i].extract_text() + " "
        
        clean_text = re.sub(r'\s+', ' ', raw_text).strip()[:5000]

        if uploaded_file.name not in [d['name'] for d in st.session_state.lecture_memory]:
            st.session_state.lecture_memory.append({"name": uploaded_file.name})

        # دالة النداء الآمن (تم تصحيح اسم الموديل هنا)
        def ask_medical_ai(prompt_text):
            try:
                completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt_text}],
                    model="llama-3.3-70b-versatile",
                    temperature=0.3,
                )
                return completion.choices[0].message.content
            except Exception as e:
                return f"⚠️ Error: {str(e)}"

        # 5. الأزرار التفاعلية
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📝 Summarize & Connect"):
                with st.spinner('Analyzing...'):
                    past = ", ".join([d['name'] for d in st.session_state.lecture_memory[:-1]])
                    st.session_state.last_result = ask_medical_ai(f"Summarize this medical text and connect to: {past}. Text: {clean_text}")

        with col2:
            if st.button("❓ Active Recall Mode"):
                with st.spinner('Generating Questions...'):
                    st.session_state.last_result = ask_medical_ai(f"Create 4 USMLE questions from: {clean_text}")

        with col3:
            if st.button("🧠 Flashcards"):
                with st.spinner('Creating Cards...'):
                    st.session_state.last_result = ask_medical_ai(f"Create 5 flashcards for: {clean_text}")

        # عرض النتيجة
        if st.session_state.last_result:
            st.markdown("### 📋 Current Result:")
            st.info(st.session_state.last_result)

            # 6. أزرار الترجمة
            st.divider()
            t_col1, t_col2 = st.columns(2)
            
            with t_col1:
                if st.button("🌐 Translate to Arabic"):
                    with st.spinner('Translating...'):
                        translation = ask_medical_ai(f"Translate this medical content to Arabic: {st.session_state.last_result}")
                        st.markdown(f'<div class="translation-box" style="direction: rtl;">{translation}</div>', unsafe_allow_html=True)
            
            with t_col2:
                if st.button("🌐 Translate to Hebrew"):
                    with st.spinner('Translating...'):
                        translation = ask_medical_ai(f"Translate this medical content to Hebrew: {st.session_state.last_result}")
                        st.markdown(f'<div class="translation-box" style="direction: rtl; text-align: right;">{translation}</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error: {e}")

# 7. الدردشة
st.divider()
user_q = st.text_input("💬 Ask a question about this lecture:")
if user_q and uploaded_file:
    with st.spinner('Thinking...'):
        answer = ask_medical_ai(f"Context: {clean_text[:2000]}\nQuestion: {user_q}")
        st.chat_message("assistant").write(answer)
