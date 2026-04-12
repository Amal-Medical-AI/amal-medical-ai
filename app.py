import streamlit as st
from groq import Groq
import PyPDF2
import re

# 1. Professional Medical Theme
st.set_page_config(page_title="Amal's Medical Brain", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #fff0f5; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #ff69b4; color: white; font-weight: bold; height: 3em; border: none; }
    h1, h3 { color: #ff69b4; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# 2. Setup
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "lecture_memory" not in st.session_state:
    st.session_state.lecture_memory = []

st.title("🌸 Amal's Medical Brain 🌸")

# 4. File Uploader
uploaded_file = st.file_uploader("Upload Medical Lecture", type=["pdf"])

if uploaded_file:
    raw_text = ""
    try:
        reader = PyPDF2.PdfReader(uploaded_file)
        # نأخذ أول 5 صفحات فقط لتجنب تجاوز حد الـ Tokens
        num_pages = min(len(reader.pages), 5)
        for i in range(num_pages):
            raw_text += reader.pages[i].extract_text() + " "
        
        # تنظيف النص: إزالة المسافات الزائدة والرموز الغريبة التي تزعج الـ API
        clean_text = re.sub(r'\s+', ' ', raw_text).strip()
        # تقليص النص لـ 4000 حرف كحد أقصى لضمان استقرار Groq
        clean_text = clean_text[:4000]

        if uploaded_file.name not in [d['name'] for d in st.session_state.lecture_memory]:
            st.session_state.lecture_memory.append({"name": uploaded_file.name, "summary": clean_text[:500]})
        
        st.success(f"File '{uploaded_file.name}' is ready!")

        col1, col2, col3 = st.columns(3)
        
        # دالة مساعدة لإرسال الطلبات وتجنب الـ BadRequestError
        def safe_groq_call(prompt):
            try:
                response = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama3-70b-8192",
                    max_tokens=1000 # تحديد عدد توكنز الرد
                )
                return response.choices[0].message.content
            except Exception as e:
                return f"⚠️ Error: The file might be too complex or the API is busy. (Details: {str(e)})"

        with col1:
            if st.button("📝 Summarize & Connect"):
                with st.spinner('Summarizing...'):
                    past = ", ".join([d['name'] for d in st.session_state.lecture_memory[:-1]])
                    p = f"Summarize this medical text and relate it to {past if past else 'general medicine'}: {clean_text}"
                    st.markdown(safe_groq_call(p))

        with col2:
            if st.button("❓ Active Recall Mode"):
                with st.spinner('Generating Q&A...'):
                    p = f"Create 3 USMLE style questions from this: {clean_text}"
                    st.info(safe_groq_call(p))

        with col3:
            if st.button("🧠 Flashcards"):
                with st.spinner('Creating Cards...'):
                    p = f"Create 5 high-yield flashcards from: {clean_text}"
                    st.warning(safe_groq_call(p))

    except Exception as e:
        st.error(f"Failed to process PDF: {e}")

# 6. Chat Interface
st.divider()
user_q = st.text_input("💬 Ask a specific question:")
if user_q and uploaded_file:
    with st.spinner('Thinking...'):
        prompt = f"Context: {clean_text[:2000]}\nQuestion: {user_q}"
        try:
            resp = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-70b-8192"
            )
            st.chat_message("assistant").write(resp.choices[0].message.content)
        except:
            st.error("Could not process this question. Try a shorter one.")
