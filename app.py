import streamlit as st
from groq import Groq
import PyPDF2
from docx import Document
from pptx import Presentation
import re

# 1. إعدادات الستايل والسرعة
st.set_page_config(page_title="Amal's Medical Brain", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #fff0f5; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #ff69b4; color: white; font-weight: bold; margin-bottom: 10px; }
    .course-summary { background-color: #ffffff; padding: 15px; border-radius: 15px; border: 2px solid #ff69b4; margin-top: 10px; font-size: 0.9em; }
    </style>
    """, unsafe_allow_html=True)

# 2. الدوال التقنية للقراءة (حل مشكلة البوربوينت)
def extract_text_from_file(file):
    file_type = file.name.split('.')[-1].lower()
    text = ""
    try:
        if file_type == 'pdf':
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages[:10]: text += page.extract_text() + " "
        elif file_type == 'docx':
            doc = Document(file)
            for para in doc.paragraphs[:100]: text += para.text + " "
        elif file_type in ['pptx', 'ppt']:
            prs = Presentation(file)
            for slide in prs.slides:
                for shape in slide.shapes:
                    if hasattr(shape, "text"): text += shape.text + " "
    except Exception as e:
        return f"Error reading file: {str(e)}"
    return text

# 3. إدارة الذاكرة والكورسات
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "course_data" not in st.session_state:
    st.session_state.course_data = {"General Medicine": {"files": [], "internal_summary": ""}}

# --- القائمة الجانبية ---
st.sidebar.title("📚 Course Management")
new_c = st.sidebar.text_input("Add New Course (e.g. Cardiology):")
if st.sidebar.button("Create Course"):
    if new_c and new_c not in st.session_state.course_data:
        st.session_state.course_data[new_c] = {"files": [], "internal_summary": ""}
        st.sidebar.success(f"{new_c} Created!")

# --- واجهة الرفع الذكية ---
st.title("🌸 Amal's Intelligent Medical Brain 🌸")
uploaded_file = st.file_uploader("Upload Lecture (PDF from GoodNotes, Word, PPTX)", type=["pdf", "docx", "pptx"])

if uploaded_file:
    # ميزة اختيار الكورس فور الرفع
    target_course = st.selectbox("📥 Which course should this belong to?", list(st.session_state.course_data.keys()))
    
    if st.button("🚀 Process & Save to Course"):
        with st.spinner("Analyzing and updating course memory..."):
            extracted_text = extract_text_from_file(uploaded_file)
            clean_content = re.sub(r'\s+', ' ', extracted_text).strip()[:6000]
            
            # تحديث قائمة ملفات الكورس
            if uploaded_file.name not in st.session_state.course_data[target_course]["files"]:
                st.session_state.course_data[target_course]["files"].append(uploaded_file.name)
            
            # تحديث "التلخيص الداخلي" للكورس باستخدام AI
            ai_update_prompt = f"""
            You are a medical knowledge manager. Based on this new lecture: {clean_content[:2000]}, 
            update the internal cumulative summary for the course '{target_course}'. 
            The previous summary was: {st.session_state.course_data[target_course]['internal_summary']}
            Create a unified, integrated summary of the course so far.
            """
            
            resp = client.chat.completions.create(
                messages=[{"role": "user", "content": ai_update_prompt}],
                model="llama-3.3-70b-versatile"
            )
            st.session_state.course_data[target_course]['internal_summary'] = resp.choices[0].message.content
            st.session_state.current_lecture_text = clean_content
            st.success(f"File added to {target_course} and internal memory updated!")

# --- عرض ملخص الكورس الذكي ---
st.divider()
active_view = st.selectbox("📂 View Course Insights:", list(st.session_state.course_data.keys()))
if st.session_state.course_data[active_view]['internal_summary']:
    st.subheader(f"🧠 {active_view} - Cumulative Internal Summary")
    st.markdown(f'<div class="course-summary">{st.session_state.course_data[active_view]["internal_summary"]}</div>', unsafe_allow_html=True)

# --- أزرار الدراسة المعتادة ---
if "current_lecture_text" in st.session_state:
    st.subheader("🛠️ Study Tools for Current File")
    c1, c2, c3 = st.columns(3)
    # (توضع هنا أزرار الكويز والتلخيص والترجمة كما في الأكواد السابقة)
