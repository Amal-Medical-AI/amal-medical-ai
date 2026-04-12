import streamlit as st
from groq import Groq
import PyPDF2
import re
import urllib.parse

# 1. إعدادات الستايل الطبي
st.set_page_config(page_title="Amal's Medical Brain", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #fff0f5; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #ff69b4; color: white; font-weight: bold; margin-bottom: 15px; height: 3.5em; border: none; }
    .stButton>button:hover { background-color: #e91e63; transform: scale(1.02); transition: 0.3s; }
    .result-box { background-color: white; padding: 20px; border-radius: 15px; border: 2px solid #ff69b4; color: #333; margin-bottom: 20px; }
    .flashcard { background-color: #fff9fb; border: 2px dashed #ff69b4; padding: 15px; border-radius: 10px; margin: 10px 0; text-align: center; }
    h1, h3 { color: #ff69b4; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# 2. إعداد الـ API والذاكرة
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "last_result" not in st.session_state: st.session_state.last_result = ""
if "current_text" not in st.session_state: st.session_state.current_text = ""

st.title("🌸 Amal's Medical Brain 🌸")

# 3. معالج الملفات
uploaded_file = st.file_uploader("Upload Medical Lecture (PDF)", type=["pdf"])

if uploaded_file:
    if not st.session_state.current_text:
        reader = PyPDF2.PdfReader(uploaded_file)
        raw = " ".join([p.extract_text() for p in reader.pages[:6]])
        st.session_state.current_text = re.sub(r'\s+', ' ', raw).strip()[:5000]
    
    topic = uploaded_file.name.replace(".pdf", "")

    def ask_ai(prompt):
        try:
            resp = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile"
            )
            return resp.choices[0].message.content
        except: return "⚠️ Error connecting to AI. Try again."

    # --- منطقة الأزرار (كلها ورا بعض تحت بعض) ---
    st.subheader("🚀 Study Command Center")

    # 1. زر التلخيص (Summarize)
    if st.button("📝 Summarize This Lecture"):
        with st.spinner('Summarizing...'):
            st.session_state.last_result = ask_ai(f"Provide a structured medical summary for: {st.session_state.current_text}")

    # 2. زر اليو اس ام لي (USMLE)
    if st.button("🩺 USMLE High-Yield Points"):
        with st.spinner('Extracting high-yield info...'):
            st.session_state.last_result = ask_ai(f"List the high-yield USMLE Step 1 & 2 facts about: {st.session_state.current_text}")

    # 3. زر الكويز (Interactive Quiz)
    if st.button("✍️ Start Interactive Quiz"):
        with st.spinner('Creating quiz...'):
            st.session_state.last_result = ask_ai(f"Create 3 USMLE multiple choice questions with answers from: {st.session_state.current_text}")

    # 4. زر الفلاش كاردز (Flashcards)
    if st.button("🧠 Create Flashcards"):
        with st.spinner('Generating cards...'):
            cards_text = ask_ai(f"Create 5 flashcards (Front/Back) from: {st.session_state.current_text}")
            st.session_state.last_result = cards_text

    # 5. زر الأبحاث (Research)
    if st.button("🔬 Recent Research & Breakthroughs (2024+)"):
        with st.spinner('Searching latest research...'):
            st.session_state.last_result = ask_ai(f"What are the latest (2024-2025) research developments or clinical trials regarding {topic}?")

    # 6. أزرار الروابط (يوتيوب وصور)
    yt_query = urllib.parse.quote(f"{topic} medical explanation")
    st.link_button("🎬 Watch Suggested YouTube Video", f"https://youtube.com{yt_query}")
    
    img_query = urllib.parse.quote(f"{topic} medical diagram anatomy")
    st.link_button("🖼️ View Medical Diagrams & Images", f"https://google.com{img_query}")

    # 7. أزرار الترجمة (تظهر دائماً لترجمة آخر نتيجة)
    st.divider()
    col_ar, col_he = st.columns(2)
    with col_ar:
        if st.button("🌐 Translate Result to Arabic"):
            st.session_state.last_result = ask_ai(f"Translate this to professional medical Arabic: {st.session_state.last_result}")
    with col_he:
        if st.button("🌐 Translate Result to Hebrew"):
            st.session_state.last_result = ask_ai(f"Translate this to professional medical Hebrew: {st.session_state.last_result}")

    # --- عرض النتائج ---
    if st.session_state.last_result:
        st.markdown("### 📋 Results Area")
        st.markdown(f'<div class="result-box">{st.session_state.last_result}</div>', unsafe_allow_html=True)

# 8. الدردشة في الأسفل
st.divider()
user_q = st.text_input("💬 Ask Amal's AI anything else:")
if user_q:
    st.write(ask_ai(f"Context: {st.session_state.current_text[:2000]}\nQuestion: {user_q}"))
