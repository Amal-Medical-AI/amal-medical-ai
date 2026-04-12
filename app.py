import streamlit as st
from groq import Groq
import PyPDF2
import re
import urllib.parse

# 1. رجعنا الستايل المميز والوردي اللي بيفتح النفس للدراسة
st.set_page_config(page_title="Amal's Medical Brain", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #fff0f5; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #ff69b4; color: white; font-weight: bold; margin-bottom: 10px; height: 3.2em; border: none; }
    .flashcard { background-color: white; border: 2px solid #ff69b4; padding: 20px; border-radius: 15px; text-align: center; margin: 10px 0; color: #333; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }
    .quiz-container { background-color: white; padding: 20px; border-radius: 15px; border: 1px solid #ff69b4; margin-bottom: 15px; }
    .result-box { background-color: #fff9fb; padding: 20px; border-radius: 15px; border: 1px solid #ff69b4; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. إعداد الـ API (استخدام موديل قوي وسريع)
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "last_result" not in st.session_state: st.session_state.last_result = ""
if "quiz_q" not in st.session_state: st.session_state.quiz_q = []
if "flashcards" not in st.session_state: st.session_state.flashcards = []

st.title("🌸 Amal's Medical Brain 🌸")

uploaded_file = st.file_uploader("Upload Medical Lecture (PDF)", type=["pdf"])

if uploaded_file:
    reader = PyPDF2.PdfReader(uploaded_file)
    text = " ".join([p.extract_text() for p in reader.pages[:7]])
    # تنظيف احترافي للنص عشان جودة Gemini
    clean_text = re.sub(r'\s+', ' ', text).strip()[:6000]
    topic = uploaded_file.name.replace(".pdf", "")

    # دالة ذكية (بمستوى Gemini)
    def ask_smart_ai(prompt):
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an elite Medical Professor. Provide high-density, accurate USMLE-style insights. Be professional, structured, and highly scientific."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.4 # دقة عالية
        )
        return completion.choices[0].message.content

    # --- منطقة الكبسات اللي ورا بعض ---
    st.subheader("🚀 Study Command Center")

    # 1. التلخيص الاحترافي
    if st.button("📝 Elite Medical Summary"):
        with st.spinner('Analyzing like a Pro...'):
            st.session_state.last_result = ask_smart_ai(f"Provide a high-yield medical summary with key mechanisms for: {clean_text}")

    # 2. الكويز التفاعلي (رجعنا الأزرار!)
    if st.button("✍️ Interactive USMLE Quiz"):
        with st.spinner('Creating Quiz...'):
            raw = ask_smart_ai(f"Create 3 USMLE questions. Format: 'Q: [question] | A: [opt1] | B: [opt2] | C: [opt3] | D: [opt4] | Correct: [letter]'. Text: {clean_text}")
            st.session_state.quiz_q = raw.split("\n")

    # 3. الفلاش كاردز (شكل البطاقات الحقيقي)
    if st.button("🧠 Brain-Recall Flashcards"):
        with st.spinner('Generating Cards...'):
            raw_f = ask_smart_ai(f"Create 4 high-yield flashcards. Format: 'Front: [Q] | Back: [A]'. Text: {clean_text}")
            st.session_state.flashcards = raw_f.split("\n")

    # 4. كبسات إضافية
    if st.button("🩺 USMLE Must-Know Points"):
        st.session_state.last_result = ask_smart_ai(f"List MUST-KNOW USMLE Step 1/2 points for: {clean_text}")

    if st.button("🔬 2024-2025 Research Brief"):
        st.session_state.last_result = ask_smart_ai(f"Recent breakthroughs 2024 about: {topic}")

    # 5. الروابط (نصية وجميلة)
    st.divider()
    yt_url = f"https://youtube.com{topic.replace(' ', '+')}+medical"
    img_url = f"https://google.com{topic.replace(' ', '+')}+diagram"
    st.markdown(f"🔗 **Resources:** [🎬 Video]({yt_url}) | [🖼️ Diagrams]({img_url})")

    # --- عرض النتائج التفاعلية ---
    
    # عرض التلخيص أو أي نتيجة مع أزرار الترجمة
    if st.session_state.last_result:
        st.markdown(f'<div class="result-box">{st.session_state.last_result}</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🌐 Arabic"):
                st.session_state.last_result = ask_smart_ai(f"Translate this to medical Arabic: {st.session_state.last_result}")
        with c2:
            if st.button("🌐 Hebrew"):
                st.session_state.last_result = ask_smart_ai(f"Translate this to medical Hebrew: {st.session_state.last_result}")

    # عرض الكويز التفاعلي
    if st.session_state.quiz_q:
        st.divider()
        for i, q in enumerate(st.session_state.quiz_q):
            if "|" in q:
                st.markdown(f'<div class="quiz-container"><b>Question {i+1}:</b> {q.split("|")[0]}</div>', unsafe_allow_html=True)
                choice = st.radio(f"Select answer for Q{i+1}:", ["A", "B", "C", "D"], key=f"q{i}")
                if st.button(f"Check Answer {i+1}", key=f"b{i}"):
                    correct_ans = q.split("Correct: ")[1].strip() if "Correct:" in q else "Check Text"
                    if choice == correct_ans: st.success("✅ Brilliant!")
                    else: st.error(f"❌ Correct is {correct_ans}")

    # عرض الفلاش كاردز
    if st.session_state.flashcards:
        st.divider()
        for f in st.session_state.flashcards:
            if "|" in f:
                st.markdown(f'<div class="flashcard"><b>{f.split("|")[0]}</b><br><hr style="border:0.5px solid #eee">{f.split("|")[1]}</div>', unsafe_allow_html=True)

# 6. الشات
st.divider()
user_q = st.text_input("💬 Ask anything else:")
if user_q: st.write(ask_smart_ai(user_q))
