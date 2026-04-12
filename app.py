import streamlit as st
from groq import Groq
import PyPDF2
import re

# 1. إعدادات الستايل
st.set_page_config(page_title="Amal's Medical Brain", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #fff0f5; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #ff69b4; color: white; font-weight: bold; margin-bottom: 10px; height: 3em; border: none; }
    .flashcard { background-color: white; border: 2px solid #ff69b4; padding: 20px; border-radius: 15px; text-align: center; margin: 10px 0; color: #333; }
    .quiz-container { background-color: #ffffff; padding: 15px; border-radius: 15px; border: 1px solid #ff69b4; margin-bottom: 15px; }
    .result-box { background-color: #fff9fb; padding: 15px; border-radius: 15px; border: 1px solid #ff69b4; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. إعداد الـ API والذاكرة
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "summary" not in st.session_state: st.session_state.summary = ""
if "translated_text" not in st.session_state: st.session_state.translated_text = ""
if "quiz_q" not in st.session_state: st.session_state.quiz_q = []
if "flashcards" not in st.session_state: st.session_state.flashcards = []

st.title("🌸 Amal's Medical Brain 🌸")

uploaded_file = st.file_uploader("Upload Medical Lecture (PDF)", type=["pdf"])

if uploaded_file:
    reader = PyPDF2.PdfReader(uploaded_file)
    text = " ".join([p.extract_text() for p in reader.pages[:5]])
    clean_text = re.sub(r'\s+', ' ', text).strip()[:4000]
    topic = uploaded_file.name.replace(".pdf", "")

    def ask_ai(prompt):
        resp = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
        return resp.choices[0].message.content

    # --- منطقة الأزرار (ورا بعض) ---
    
    # 1. التلخيص (بالإنجليزي فقط)
    if st.button("📝 Generate English Summary"):
        with st.spinner('Summarizing...'):
            st.session_state.summary = ask_ai(f"Summarize this medical lecture in professional English: {clean_text}")
            st.session_state.translated_text = "" # تصفير الترجمة القديمة

    # عرض التلخيص وتحته أزرار الترجمة
    if st.session_state.summary:
        st.subheader("📋 Lecture Summary")
        st.info(st.session_state.summary)
        
        # أزرار الترجمة منفصلة وتحت التلخيص مباشرة
        col_ar, col_he = st.columns(2)
        with col_ar:
            if st.button("🇸🇦 Translate Summary to Arabic"):
                st.session_state.translated_text = ask_ai(f"Translate this to professional medical Arabic: {st.session_state.summary}")
        with col_he:
            if st.button("🇮🇱 Translate Summary to Hebrew"):
                st.session_state.translated_text = ask_ai(f"Translate this to professional medical Hebrew: {st.session_state.summary}")
        
        # عرض نص الترجمة إذا وجد
        if st.session_state.translated_text:
            st.markdown(f'<div class="result-box" style="direction: rtl;">{st.session_state.translated_text}</div>', unsafe_allow_html=True)

    st.divider()

    # 2. الكويز التفاعلي
    if st.button("✍️ Generate Interactive Quiz"):
        with st.spinner('Creating Quiz...'):
            raw_q = ask_ai(f"Create 3 USMLE questions. Format: 'Q: [question] | A: [opt1] | B: [opt2] | C: [opt3] | D: [opt4] | Correct: [letter]'. Text: {clean_text}")
            st.session_state.quiz_q = raw_q.split("\n")

    if st.session_state.quiz_q:
        for i, q_line in enumerate(st.session_state.quiz_q):
            if "|" in q_line:
                st.markdown(f'<div class="quiz-container">{q_line.split("|")[0]}</div>', unsafe_allow_html=True)
                choice = st.radio(f"Choose answer for Question {i}:", ["A", "B", "C", "D"], key=f"quiz{i}")
                if st.button(f"Check Answer {i}", key=f"btn{i}"):
                    if f"Correct: {choice}" in q_line or f"Correct: {choice.lower()}" in q_line:
                        st.success("✅ Correct! Excellent Work.")
                    else:
                        st.error(f"❌ Try again! (The correct answer is in the lecture text)")

    # 3. الفلاش كاردز
    if st.button("🧠 Create Flashcards"):
        with st.spinner('Generating Cards...'):
            raw_f = ask_ai(f"Create 4 medical flashcards. Format: 'Front: [Q] | Back: [A]'. Text: {clean_text}")
            st.session_state.flashcards = raw_f.split("\n")

    if st.session_state.flashcards:
        for f in st.session_state.flashcards:
            if "|" in f:
                st.markdown(f'<div class="flashcard">{f}</div>', unsafe_allow_html=True)

    # 4. الروابط والأدوات الإضافية
    st.divider()
    if st.button("🩺 USMLE High-Yield Points"):
        st.write(ask_ai(f"Provide USMLE high-yield points for: {clean_text}"))
    
    if st.button("🔬 Recent Research (2024-2025)"):
        st.write(ask_ai(f"Search for recent breakthroughs about {topic}"))

    # روابط اليوتيوب والصور
    yt_link = f"https://youtube.com{topic.replace(' ', '+')}+medical"
    img_link = f"https://google.com{topic.replace(' ', '+')}+medical+diagram"
    st.markdown(f"🔗 **YouTube:** [Click Here]({yt_link}) | **Images:** [Click Here]({img_link})")

st.divider()
user_q = st.text_input("💬 Chat with Amal's AI Assistant:")
if user_q:
    st.write(ask_ai(user_q))
