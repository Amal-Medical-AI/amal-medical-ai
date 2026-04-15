import streamlit as st
from groq import Groq
import PyPDF2
from docx import Document
from pptx import Presentation
import re
import json
import os

# 1. إعدادات الستايل والسرعة
st.set_page_config(page_title="Amal's Medical Brain", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #fff0f5; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #ff69b4; color: white; font-weight: bold; margin-bottom: 10px; }
    .master-box { background-color: white; padding: 20px; border-radius: 15px; border: 2px solid #ff69b4; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# 2. نظام حفظ البيانات (Database)
if "db" not in st.session_state:
    st.session_state.db = {} # القاموس الذي سيحفظ كل تلاخيص الكورسات

# 3. دوال قراءة الملفات المتنوعة
def get_file_text(file):
    ext = file.name.split('.')[-1].lower()
    text = ""
    if ext == 'pdf':
        r = PyPDF2.PdfReader(file)
        for p in r.pages[:8]: text += p.extract_text() + " "
    elif ext == 'docx':
        d = Document(file)
        for p in d.paragraphs: text += p.text + " "
    elif ext in ['pptx', 'ppt']:
        prs = Presentation(file)
        for s in prs.slides:
            for shp in s.shapes:
                if hasattr(shp, "text"): text += shp.text + " "
    return text

# --- القائمة الجانبية (إدارة الكورسات) ---
st.sidebar.title("📚 Course Management")
course_name = st.sidebar.text_input("New Course Name:")
if st.sidebar.button("Add Course"):
    if course_name and course_name not in st.session_state.db:
        st.session_state.db[course_name] = {"summary": "", "questions": ""}
        st.sidebar.success(f"{course_name} Created!")

active_c = st.sidebar.selectbox("Active Course:", list(st.session_state.db.keys()))

# --- الصفحة الرئيسية ---
st.title(f"🌸 {active_c} Study Lab 🌸")

uploaded_file = st.file_uploader("Upload Lecture (GoodNotes PDF, Word, PPTX)", type=["pdf", "docx", "pptx"])

if uploaded_file:
    with st.spinner("Processing High-Speed Analysis..."):
        raw_text = get_file_text(uploaded_file)
        clean_text = re.sub(r'\s+', ' ', raw_text).strip()[:6000]

    # أزرار العمليات (تحت بعضها)
    if st.button("📝 Summarize & Add to Master File"):
        with st.spinner('AI is merging knowledge...'):
            prompt = f"Previous Course Content: {st.session_state.db[active_c]['summary']}\nNew Material: {clean_text}\nUpdate the cumulative summary."
            resp = client.chat.completions.create(messages=[{"role":"user","content":prompt}], model="llama-3.3-70b-versatile")
            st.session_state.db[active_c]['summary'] = resp.choices[0].message.content
            st.success("Internal Master File Updated!")

    if st.button("❓ Add Questions to Question Bank"):
        with st.spinner('Generating USMLE Bank...'):
            prompt = f"Add 3 USMLE questions based on this new material to the existing bank: {clean_text}"
            resp = client.chat.completions.create(messages=[{"role":"user","content":prompt}], model="llama-3.3-70b-versatile")
            st.session_state.db[active_c]['questions'] += "\n\n" + resp.choices[0].message.content

    # عرض التراكمي
    st.divider()
    st.subheader(f"🧠 Cumulative Knowledge: {active_c}")
    with st.expander("View Master Summary"):
        st.write(st.session_state.db[active_c]['summary'])
    
    with st.expander("View Question Bank"):
        st.write(st.session_state.db[active_c]['questions'])

    # زر التحميل الذهبي (لأخذه لـ OneDrive)
    full_data = f"MASTER SUMMARY:\n{st.session_state.db[active_c]['summary']}\n\nQUESTION BANK:\n{st.session_state.db[active_c]['questions']}"
    st.download_button(label="📥 Download Master Guide for OneDrive", data=full_data, file_name=f"{active_c}_Master_Guide.txt")

# الترجمة (تحت بعض)
st.sidebar.divider()
if st.sidebar.button("🌐 Translate Master to Arabic"):
    st.write(st.session_state.db[active_c]['summary'][:2000]) # نموذج ترجمة
