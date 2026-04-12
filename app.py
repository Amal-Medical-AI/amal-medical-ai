import streamlit as st
from groq import Groq
import PyPDF2

# Page Config & Theme
st.set_page_config(page_title="Amal's Medical Brain", layout="wide")
st.markdown("<style>.main { background-color: #fff0f5; } .stButton>button { background-color: #ff69b4; color: white; border-radius: 20px; }</style>", unsafe_allow_html=True)

# API Setup
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "medical_history" not in st.session_state:
    st.session_state.medical_history = []

st.title("🌸 Amal's Medical Brain 🌸")
st.sidebar.title("📚 Archived Lectures")

uploaded_file = st.file_uploader("Upload Lecture", type=["pdf", "docx", "pptx", "png", "jpg"])

if uploaded_file:
    text_content = ""
    if uploaded_file.type == "application/pdf":
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        # أخذ أول 3 صفحات فقط لضمان عدم حدوث خطأ في الحجم
        for page in pdf_reader.pages[:3]:
            text_content += page.extract_text()
    
    st.success(f"Received: {uploaded_file.name}")

    if st.button("📝 Summarize & Link to USMLE"):
        with st.spinner('Analyzing...'):
            try:
                # تقليل كمية النص المرسلة لضمان استقرار الخدمة
                clean_text = text_content[:3000] 
                response = client.chat.completions.create(
                    messages=[{"role": "user", "content": f"Summarize in Arabic: {clean_text}. Link to USMLE and PubMed."}],
                    model="llama3-8b-8192",
                )
                st.markdown(response.choices[0].message.content)
            except Exception as e:
                st.error("آمال، يبدو أن الملف كبير جداً. جربي رفع ملف أصغر أو سأقوم بتحديث الكود لكِ.")

    if st.button("🧠 Flashcards"):
        with st.spinner('Creating...'):
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": f"Create 3 Arabic flashcards from: {text_content[:2000]}"}],
                model="llama3-8b-8192",
            )
            st.info(response.choices[0].message.content)
