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
    .flashcard { background-color: white; border: 2px solid #ff69b4; padding: 20px; border-radius: 15px; text-align: center; margin: 10px 0; box-shadow: 2px 2px 8px rgba(0,0,0,0.1); color: #333; }
    .quiz-container { background-color: #fff0f5; padding: 15px; border-radius: 15px; border: 1px solid #ff69b4; margin-bottom: 15px; }
    .link-box { background-color: #fce4ec; padding: 10px; border-radius: 10px; border: 1px dashed #ff69b4; margin-bottom: 10px; word-break: break-all; }
    </style>
    """, unsafe_allow_html=True)

# 2. إعداد الـ API
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "quiz_q" not in st.session_state: st.session_state.quiz_q = []
if "flashcards" not in st.session_state: st.session_state.flashcards = []
if "summary" not in st.session_state: st.session_state.summary = ""

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
    
    # 1. التلخيص
    if st.button("📝 Summarize & Translate"):
        st.session_state.summary = ask_ai(f"Summarize this in English then translate the summary to Arabic: {clean_text}")
    
    # 2. إنشاء الكويز
    if st.button("✍️ Generate Interactive Quiz"):
        raw_q = ask_ai(f"Create 3 USMLE questions from this text. For each: 'Q: [question] | A: [opt1] | B: [opt2] | C: [opt3] | D: [opt4] | Correct: [letter]'. Text: {clean_text}")
        st.session_state.quiz_q = raw_q.split("\n")

    # 3. إنشاء الفلاش كاردز
    if st.button("🧠 Create Flashcards"):
        raw_f = ask_ai(f"Create 4 flashcards from this. Format: 'Front: [Question] | Back: [Answer]'. Text: {clean_text}")
        st.session_state.flashcards = raw_f.split("\n")

    # 4. الروابط (نصية للنسخ)
    st.markdown("### 🔗 Useful Links")
    yt_link = f"https://youtube.com{topic.replace(' ', '+')}+medical+lecture"
    img_link = f"https://google.com{topic.replace(' ', '+')}+medical+diagram"
    
    st.markdown(f'<div class="link-box"><b>YouTube Search:</b><br>{yt_link}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="link-box"><b>Medical Images:</b><br>{img_link}</div>', unsafe_allow_html=True)

    # --- عرض النتائج التفاعلية ---

    if st.session_state.summary:
        st.subheader("📋 Summary")
        st.info(st.session_state.summary)

    if st.session_state.quiz_q:
        st.subheader("✍️ Interactive Quiz")
        for i, q_line in enumerate(st.session_state.quiz_q):
            if "|" in q_line:
                parts = q_line.split("|")
                st.markdown(f'<div class="quiz-container"><b>{parts[0]}</b></div>', unsafe_allow_html=True)
                choice = st.radio(f"Select answer for Q{i}:", ["A", "B", "C", "D"], key=f"q{i}")
                if st.button(f"Check Answer Q{i}", key=f"btn{i}"):
                    if choice in q_line.split("Correct:")[1]:
                        st.success("✅ Correct!")
                    else:
                        st.error(f"❌ Wrong! {q_line.split('Correct:')[1]}")

    if st.session_state.flashcards:
        st.subheader("🗂️ Flashcards")
        for f in st.session_state.flashcards:
            if "|" in f:
                st.markdown(f'<div class="flashcard">{f}</div>', unsafe_allow_html=True)

    # 5. أزرار إضافية (تحت بعض)
    if st.button("🩺 USMLE High-Yield"):
        st.write(ask_ai(f"High-yield USMLE facts for: {clean_text}"))
    
    if st.button("🔬 Recent Research 2024"):
        st.write(ask_ai(f"Latest research 2024-2025 about: {topic}"))

st.divider()
user_q = st.text_input("💬 Ask any question:")
if user_q:
    st.write(ask_ai(user_q))
