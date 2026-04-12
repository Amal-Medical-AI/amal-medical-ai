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
    h1, h3 { color: #ff69b4; text-align: center; font-family: 'Arial'; }
    .stTextInput>div>div>input { border-radius: 15px; }
    .translation-box { background-color: #fce4ec; padding: 15px; border-radius: 15px; border: 1px solid #ff69b4; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. إعداد الـ API والذاكرة
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "lecture_memory" not in st.session_state:
    st.session_state.lecture_memory = []
if "last_result" not in st.session_state:
    st.session_state.last_result = "" # ذاكرة لحفظ آخر نتيجة ظهرت

st.title("🌸 Amal's Medical Brain 🌸")

# 3. القائمة الجانبية (Sidebar)
st.sidebar.title("🧠 Study Memory")
if st.session_state.lecture_memory:
    for item in st.session_state.lecture_memory:
        st.sidebar.write(f"📖 {item['name']}")
else:
    st.sidebar.write("No history yet.")

# 4. معالج الملفات
uploaded_file = st.file_uploader("Upload Medical Lecture (PDF)", type=["pdf"])

if uploaded_file:
    raw_text = ""
    progress_bar = st.progress(0)
    
    try:
        reader = PyPDF2.PdfReader(uploaded_file)
        pages_to_read = min(len(reader.pages), 6)
        
        for i in range(pages_to_read):
            page_text = reader.pages[i].extract_text()
            if page_text:
                raw_text += page_text + " "
            progress_bar.progress((i + 1) / pages_to_read)
        
        clean_text = re.sub(r'\s+', ' ', raw_text).strip()[:5000]

        if uploaded_file.name not in [d['name'] for d in st.session_state.lecture_memory]:
            st.session_state.lecture_memory.append({"name": uploaded_file.name})
        
        st.success(f"✅ Lecture '{uploaded_file.name}' loaded!")

        # دالة النداء الآمن
        def ask_medical_ai(prompt_text):
            try:
                completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "You are a professional medical assistant for USMLE prep."},
                        {"role": "user", "content": prompt_text}
                    ],
                    model="llama-3.3-70b-8192", # تأكدي من كتابة الموديل بشكل صحيح
                    temperature=0.5,
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
                    prompt = f"Summarize this medical text and connect to previous topics ({past}): {clean_text}"
                    st.session_state.last_result = ask_medical_ai(prompt)

        with col2:
            if st.button("❓ Active Recall Mode"):
                with st.spinner('Generating...'):
                    prompt = f"Create 4 high-yield USMLE questions based on: {clean_text}"
                    st.session_state.last_result = ask_medical_ai(prompt)

        with col3:
            if st.button("🧠 Flashcards"):
                with st.spinner('Creating...'):
                    prompt = f"Create 5 active recall flashcards for: {clean_text}"
                    st.session_state.last_result = ask_medical_ai(prompt)

        # عرض النتيجة الأساسية
        if st.session_state.last_result:
            st.markdown("### 📋 Result:")
            st.write(st.session_state.last_result)

            # 6. أزرار الترجمة (تظهر فقط بعد وجود نتيجة)
            st.write("---")
            t_col1, t_col2 = st.columns(2)
            
            with t_col1:
                if st.button("🌐 Translate to Arabic"):
                    with st.spinner('Translating...'):
                        t_prompt = f"Translate the following medical content to professional Arabic accurately: {st.session_state.last_result}"
                        translation = ask_medical_ai(t_prompt)
                        st.markdown(f'<div class="translation-box">{translation}</div>', unsafe_allow_html=True)
            
            with t_col2:
                if st.button("🌐 Translate to Hebrew"):
                    with st.spinner('Translating...'):
                        t_prompt = f"Translate the following medical content to professional Hebrew accurately: {st.session_state.last_result}"
                        translation = ask_medical_ai(t_prompt)
                        st.markdown(f'<div class="translation-box" style="direction: rtl; text-align: right;">{translation}</div>', unsafe_allow_html=True)

        # 7. الدردشة
        st.divider()
        user_q = st.text_input("💬 Question about this lecture?")
        if user_q:
            with st.spinner('Searching brain...'):
                answer = ask_medical_ai(f"Context: {clean_text[:2000]}\nQuestion: {user_q}")
                st.chat_message("assistant").write(answer)

    except Exception as e:
        st.error(f"Error: {e}")
