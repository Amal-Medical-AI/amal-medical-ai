import streamlit as st
from groq import Groq
import PyPDF2
import re
import urllib.parse

# 1. الستايل المميز (الوردي والمنظم)
st.set_page_config(page_title="Amal's Medical Brain", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #fff0f5; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #ff69b4; color: white; font-weight: bold; margin-bottom: 10px; height: 3.2em; border: none; }
    .course-box { background-color: #ffffff; padding: 15px; border-radius: 15px; border: 2px solid #ff69b4; margin-bottom: 10px; }
    .flashcard { background-color: white; border: 2px solid #ff69b4; padding: 20px; border-radius: 15px; text-align: center; margin: 10px 0; color: #333; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }
    .quiz-container { background-color: white; padding: 20px; border-radius: 15px; border: 1px solid #ff69b4; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

# 2. إعداد الـ API والذاكرة السحابية للمواد
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "courses" not in st.session_state:
    st.session_state.courses = {"General Medicine": []} # كورس افتراضي
if "active_course" not in st.session_state:
    st.session_state.active_course = "General Medicine"
if "last_result" not in st.session_state: st.session_state.last_result = ""
if "quiz_q" not in st.session_state: st.session_state.quiz_q = []
if "flashcards" not in st.session_state: st.session_state.flashcards = []

# --- القائمة الجانبية لإدارة الكورسات ---
st.sidebar.title("📚 My Medical Courses")

# إضافة كورس جديد
new_course = st.sidebar.text_input("➕ Add New Course:")
if st.sidebar.button("Create Course"):
    if new_course and new_course not in st.session_state.courses:
        st.session_state.courses[new_course] = []
        st.sidebar.success(f"Course {new_course} Added!")

# اختيار الكورس الحالي
st.session_state.active_course = st.sidebar.selectbox("📂 Select Course to Study:", list(st.session_state.courses.keys()))

# عرض المواد المحملة في الكورس المختار
st.sidebar.divider()
st.sidebar.subheader(f"📖 Materials in {st.session_state.active_course}:")
for doc in st.session_state.courses[st.session_state.active_course]:
    st.sidebar.write(f"📄 {doc}")

# --- الصفحة الرئيسية ---
st.title(f"🌸 {st.session_state.active_course} Brain 🌸")

uploaded_file = st.file_uploader(f"Upload Lecture to {st.session_state.active_course}", type=["pdf"])

if uploaded_file:
    # حفظ اسم الملف في الكورس المختار إذا لم يكن موجوداً
    if uploaded_file.name not in st.session_state.courses[st.session_state.active_course]:
        st.session_state.courses[st.session_state.active_course].append(uploaded_file.name)

    # معالجة النص
    reader = PyPDF2.PdfReader(uploaded_file)
    text = " ".join([p.extract_text() for p in reader.pages[:7]])
    clean_text = re.sub(r'\s+', ' ', text).strip()[:6000]
    topic = uploaded_file.name.replace(".pdf", "")

    def ask_smart_ai(prompt):
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an elite Medical Professor. Provide high-density, accurate USMLE-style insights. Be professional and structured."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.4
        )
        return completion.choices[0].message.content

    # --- منطقة الأزرار ---
    st.subheader("🛠️ Study Command Center")

    if st.button("📝 Elite Medical Summary"):
        with st.spinner('Analyzing...'):
            st.session_state.last_result = ask_smart_ai(f"Provide a high-yield summary for: {clean_text}")

    if st.button("✍️ Interactive USMLE Quiz"):
        with st.spinner('Preparing Questions...'):
            raw = ask_smart_ai(f"Create 3 USMLE questions. Format: 'Q: [question] | A: [opt1] | B: [opt2] | C: [opt3] | D: [opt4] | Correct: [letter]'. Text: {clean_text}")
            st.session_state.quiz_q = raw.split("\n")

    if st.button("🧠 Brain-Recall Flashcards"):
        with st.spinner('Generating Cards...'):
            raw_f = ask_smart_ai(f"Create 4 flashcards. Format: 'Front: [Q] | Back: [A]'. Text: {clean_text}")
            st.session_state.flashcards = raw_f.split("\n")

    if st.button("🩺 USMLE Must-Know Points"):
        st.session_state.last_result = ask_smart_ai(f"List MUST-KNOW USMLE Step 1/2 points for: {clean_text}")

    if st.button("🔬 Recent Research 2024-2025"):
        st.session_state.last_result = ask_smart_ai(f"What's new in 2024 research regarding: {topic}")

    # الروابط
    st.divider()
    yt_url = f"https://youtube.com{topic.replace(' ', '+')}+medical"
    img_url = f"https://google.com{topic.replace(' ', '+')}+diagram"
    st.markdown(f"🔗 **Resources:** [🎬 Watch Video]({yt_url}) | [🖼️ View Diagrams]({img_url})")

    # --- النتائج ---
    if st.session_state.last_result:
        st.markdown(f'<div class="course-box">{st.session_state.last_result}</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🌐 Translate to Arabic"):
                st.session_state.last_result = ask_smart_ai(f"Translate this to medical Arabic: {st.session_state.last_result}")
        with c2:
            if st.button("🌐 Translate to Hebrew"):
                st.session_state.last_result = ask_smart_ai(f"Translate this to medical Hebrew: {st.session_state.last_result}")

    if st.session_state.quiz_q:
        st.divider()
        for i, q in enumerate(st.session_state.quiz_q):
            if "|" in q:
                st.markdown(f'<div class="quiz-container"><b>Q{i+1}:</b> {q.split("|")[0]}</div>', unsafe_allow_html=True)
                choice = st.radio(f"Select answer for Q{i+1}:", ["A", "B", "C", "D"], key=f"q{i}")
                if st.button(f"Check Answer {i+1}", key=f"b{i}"):
                    if f"Correct: {choice}" in q: st.success("✅ Excellent!")
                    else: st.error(f"❌ Check the correct answer in the explanation.")

    if st.session_state.flashcards:
        st.divider()
        for f in st.session_state.flashcards:
            if "|" in f:
                st.markdown(f'<div class="flashcard"><b>Front:</b> {f.split("|")[0]}<br><hr><b>Back:</b> {f.split("|")[1]}</div>', unsafe_allow_html=True)

# 6. الشات
st.divider()
user_q = st.text_input("💬 Ask Amal's AI Assistant:")
if user_q: st.write(ask_smart_ai(user_q))
