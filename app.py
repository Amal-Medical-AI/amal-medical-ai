import streamlit as st
from groq import Groq
import PyPDF2
import re
import urllib.parse

# 1. إعدادات التصميم (CSS)
st.set_page_config(page_title="Amal's Medical Brain", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #fff0f5; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #ff69b4; color: white; font-weight: bold; margin-bottom: 10px; }
    .flashcard { background-color: white; border: 2px solid #ff69b4; padding: 20px; border-radius: 15px; text-align: center; margin: 10px 0; box-shadow: 3px 3px 10px rgba(0,0,0,0.1); }
    .quiz-box { background-color: #fce4ec; padding: 20px; border-radius: 15px; border-left: 5px solid #ff69b4; margin-bottom: 20px; }
    h1, h2, h3 { color: #ff69b4; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# 2. إعدادات الـ API والذاكرة
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "quiz_data" not in st.session_state: st.session_state.quiz_data = None
if "flashcards_data" not in st.session_state: st.session_state.flashcards_data = None

st.title("🌸 Amal's Medical Brain 🌸")

# 3. معالج الملفات
uploaded_file = st.file_uploader("Upload Medical Lecture (PDF)", type=["pdf"])

if uploaded_file:
    # استخراج النص (أول 5 صفحات)
    reader = PyPDF2.PdfReader(uploaded_file)
    raw_text = " ".join([p.extract_text() for p in reader.pages[:5]])
    clean_text = re.sub(r'\s+', ' ', raw_text)[:4000]
    topic_name = uploaded_file.name.replace(".pdf", "")

    # دالة AI
    def ask_ai(prompt):
        resp = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile"
        )
        return resp.choices[0].message.content

    # --- منطقة الكبسات (مرتبة ورا بعض) ---
    st.subheader("🛠️ Study Tools")
    
    # 1. زر اليوتيوب (تم الإصلاح)
    search_query = f"{topic_name} medical lecture high yield"
    yt_url = f"https://youtube.com{urllib.parse.quote(search_query)}"
    st.link_button("🎬 Watch Suggested YouTube Videos", yt_url)

    # 2. زر الكويز
    if st.button("📝 Generate Interactive Quiz"):
        with st.spinner('Preparing Quiz...'):
            prompt = f"Create 3 USMLE questions from this text: {clean_text}. Format: Question, Options A,B,C,D, and Correct Answer."
            st.session_state.quiz_data = ask_ai(prompt)

    # 3. زر الفلاش كاردز
    if st.button("🧠 Create Visual Flashcards"):
        with st.spinner('Creating Cards...'):
            prompt = f"Create 4 medical flashcards (Front: Question, Back: Answer) from: {clean_text}"
            st.session_state.flashcards_data = ask_ai(prompt)

    # 4. أزرار إضافية
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🩺 USMLE High-Yield"):
            st.write(ask_ai(f"List USMLE high yield points for: {clean_text}"))
    with col_b:
        if st.button("🔬 Recent Research 2024"):
            st.write(ask_ai(f"Recent research 2024 about: {topic_name}"))

    # --- عرض النتائج التفاعلية ---

    # عرض الكويز
    if st.session_state.quiz_data:
        st.divider()
        st.subheader("✍️ Practice Quiz")
        questions = st.session_state.quiz_data.split("Question")
        for q in questions[1:]:
            with st.container():
                st.markdown(f'<div class="quiz-box"><b>Question:</b> {q.split("Answer:")[0]}</div>', unsafe_allow_html=True)
                # إضافة أزرار اختيار حقيقية
                user_choice = st.radio("Choose your answer:", ["A", "B", "C", "D"], key=q[:20])
                if st.button(f"Check Answer", key="btn"+q[:20]):
                    correct = q.split("Answer:")[1][:5]
                    if user_choice in correct:
                        st.success("✅ Correct! Brilliant.")
                    else:
                        st.error(f"❌ Incorrect. The right answer is {correct}")

    # عرض الفلاش كاردز بشكل بطاقات
    if st.session_state.flashcards_data:
        st.divider()
        st.subheader("🗂️ Study Flashcards")
        cards = st.session_state.flashcards_data.split("\n\n")
        for card in cards:
            if ":" in card:
                st.markdown(f'<div class="flashcard">{card}</div>', unsafe_allow_html=True)

# 6. الدردشة (أسفل الصفحة)
st.divider()
user_input = st.text_input("💬 Ask any specific question:")
if user_input:
    st.write(ask_ai(user_input))
