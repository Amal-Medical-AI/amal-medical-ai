import streamlit as st
from groq import Groq
import PyPDF2
import re
import urllib.parse

# 1. إعدادات الصفحة والستايل
st.set_page_config(page_title="Amal's Medical Brain", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #fff0f5; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #ff69b4; color: white; font-weight: bold; height: 3em; border: none; }
    .stButton>button:hover { background-color: #e91e63; border: 2px solid white; }
    .info-box { background-color: #ffffff; padding: 15px; border-radius: 15px; border: 2px solid #ff69b4; margin-bottom: 10px; }
    h1, h3 { color: #ff69b4; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# 2. إعداد الـ API والذاكرة
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "lecture_memory" not in st.session_state:
    st.session_state.lecture_memory = []
if "last_result" not in st.session_state:
    st.session_state.last_result = "" 
if "current_topic" not in st.session_state:
    st.session_state.current_topic = ""

st.title("🌸 Amal's Medical Brain 🌸")

# 3. Sidebar
st.sidebar.title("🧠 Study Memory")
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
        st.session_state.current_topic = uploaded_file.name.replace(".pdf", "")

        if uploaded_file.name not in [d['name'] for d in st.session_state.lecture_memory]:
            st.session_state.lecture_memory.append({"name": uploaded_file.name})

        def ask_medical_ai(prompt_text):
            try:
                completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt_text}],
                    model="llama-3.3-70b-versatile",
                    temperature=0.3,
                )
                return completion.choices[0].message.content
            except:
                return "⚠️ Connection error. Please try again."

        # 5. الأزرار الأساسية
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📝 Summarize & Connect"):
                with st.spinner('Analyzing...'):
                    st.session_state.last_result = ask_medical_ai(f"Summarize this concisely: {clean_text}")
        with col2:
            if st.button("❓ Active Recall Mode"):
                with st.spinner('Generating...'):
                    st.session_state.last_result = ask_medical_ai(f"Create 4 USMLE questions: {clean_text}")
        with col3:
            if st.button("🧠 Flashcards"):
                with st.spinner('Creating...'):
                    st.session_state.last_result = ask_medical_ai(f"Create 5 flashcards: {clean_text}")

        # عرض النتيجة
        if st.session_state.last_result:
            st.info(st.session_state.last_result)

            # 6. الميزات الجديدة (الثلاث كبسات الإضافية)
            st.write("---")
            st.subheader("🚀 Extra High-Yield Features")
            btn1, btn2, btn3 = st.columns(3)

            with btn1:
                # زر يوتيوب: يبحث عن فيديوهات طبية موثوقة (Osmosis, Ninja Nerd, Khan Academy)
                search_query = urllib.parse.quote(f"{st.session_state.current_topic} medical lecture high views")
                youtube_url = f"https://youtube.com{search_query}"
                st.link_button("🎬 Search Top YouTube Videos", youtube_url)

            with btn2:
                if st.button("🩺 USMLE High-Yield Points"):
                    with st.spinner('Finding connections...'):
                        p = f"Based on this topic: {clean_text[:2000]}, list the 'Must-Know' points for USMLE Step 1/2 in English bullet points."
                        st.markdown(f'<div class="info-box">{ask_medical_ai(p)}</div>', unsafe_allow_html=True)

            with btn3:
                if st.button("🔬 Recent Research 2024"):
                    with st.spinner('Searching latest data...'):
                        p = f"What are the most recent research breakthroughs or clinical trials (2024-2025) related to: {st.session_state.current_topic}? Provide brief English points."
                        st.markdown(f'<div class="info-box">{ask_medical_ai(p)}</div>', unsafe_allow_html=True)

            # 7. أزرار الترجمة (القديمة)
            t_col1, t_col2 = st.columns(2)
            with t_col1:
                if st.button("🌐 Translate to Arabic"):
                    st.markdown(f'<div class="info-box" style="direction: rtl;">{ask_medical_ai("Translate to Arabic: " + st.session_state.last_result)}</div>', unsafe_allow_html=True)
            with t_col2:
                if st.button("🌐 Translate to Hebrew"):
                    st.markdown(f'<div class="info-box" style="direction: rtl; text-align: right;">{ask_medical_ai("Translate to Hebrew: " + st.session_state.last_result)}</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error: {e}")

# 8. الدردشة
st.divider()
user_q = st.text_input("💬 Ask a specific question about this lecture:")
if user_q and uploaded_file:
    with st.spinner('Thinking...'):
        st.chat_message("assistant").write(ask_medical_ai(f"Context: {clean_text[:2000]}\nQuestion: {user_q}"))
