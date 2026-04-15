import streamlit as st
from groq import Groq
import PyPDF2
from docx import Document
from pptx import Presentation
import re

# 1. إعدادات الصفحة والسرعة
st.set_page_config(page_title="Amal's Medical Brain", layout="wide")

# دالة لقراءة الملفات بمختلف أنواعها
def extract_text_from_file(file):
    file_type = file.name.split('.')[-1].lower()
    text = ""
    if file_type == 'pdf':
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages[:7]: text += page.extract_text() + " "
    elif file_type == 'docx':
        doc = Document(file)
        for para in doc.paragraphs[:50]: text += para.text + " "
    elif file_type in ['pptx', 'ppt']:
        prs = Presentation(file)
        for slide in prs.slides[:15]:
            for shape in slide.shapes:
                if hasattr(shape, "text"): text += shape.text + " "
    return text

# 2. الواجهة والستايل
st.markdown("""
    <style>
    .main { background-color: #fff0f5; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #ff69b4; color: white; font-weight: bold; }
    .course-box { background-color: white; padding: 15px; border-radius: 15px; border: 2px solid #ff69b4; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# إدارة الذاكرة والكورسات
if "courses" not in st.session_state: st.session_state.courses = {"General": []}
if "active_course" not in st.session_state: st.session_state.active_course = "General"

# القائمة الجانبية
st.sidebar.title("📚 Course Management")
new_c = st.sidebar.text_input("Add Course:")
if st.sidebar.button("Create"): 
    if new_c: st.session_state.courses[new_c] = []
st.session_state.active_course = st.sidebar.selectbox("Active Course:", list(st.session_state.courses.keys()))

st.title(f"🌸 {st.session_state.active_course} Lab 🌸")

# رفع الملفات (يدعم كل الأنواع)
uploaded_file = st.file_uploader("Upload (PDF, Word, PowerPoint)", type=["pdf", "docx", "pptx"])

if uploaded_file:
    with st.spinner("⚡ High-Speed Processing..."):
        full_text = extract_text_from_file(uploaded_file)
        clean_text = re.sub(r'\s+', ' ', full_text).strip()[:7000]
        
    st.success(f"Loaded: {uploaded_file.name}")

    def ask_ai(prompt):
        resp = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile"
        )
        return resp.choices[0].message.content

    # أزرار العمليات تحت بعضها
    if st.button("📝 Elite Medical Summary"):
        st.info(ask_ai(f"Provide a high-density summary: {clean_text}"))

    if st.button("✍️ Interactive USMLE Quiz"):
        st.write(ask_ai(f"Create a USMLE quiz from: {clean_text}"))

    if st.button("🧠 Medical Flashcards"):
        st.warning(ask_ai(f"Create 5 flashcards for: {clean_text}"))

    # الترجمة
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🌐 Arabic"): st.write(ask_ai(f"Translate to Arabic: {clean_text[:2000]}"))
    with col2:
        if st.button("🌐 Hebrew"): st.write(ask_ai(f"Translate to Hebrew: {clean_text[:2000]}"))

st.divider()
user_q = st.text_input("💬 Ask anything about this material:")
if user_q: st.write(ask_ai(user_q))
