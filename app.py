import streamlit as st
from groq import Groq
import PyPDF2

# Page Config & Styling
st.set_page_config(page_title="Amal's Medical Brain", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #fff0f5; }
    .stButton>button { background-color: #ff69b4; color: white; border-radius: 20px; font-weight: bold; }
    h1, h3 { color: #ff69b4; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "medical_history" not in st.session_state:
    st.session_state.medical_history = []

st.title("🌸 Amal's Medical Brain 🌸")
st.sidebar.title("📚 Archived Lectures")

uploaded_file = st.file_uploader("Upload Medical File", type=["pdf", "docx", "pptx"])

if uploaded_file:
    # قراءة النص بطريقة ذكية لا تسبب تعليق
    text_content = ""
    if uploaded_file.type == "application/pdf":
        reader = PyPDF2.PdfReader(uploaded_file)
        # رح ناخد أول صفحات عشان نضمن السرعة
        num_pages = min(len(reader.pages), 5) 
        for i in range(num_pages):
            text_content += reader.pages[i].extract_text()
    
    st.success(f"✅ Received: {uploaded_file.name}")

    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📝 Summarize (Smart Mode)"):
            with st.spinner('Analyzing...'):
                try:
                    # نرسل فقط زبدة الموضوع
                    snippet = text_content[:5000]
                    response = client.chat.completions.create(
                        messages=[{"role": "user", "content": f"Summarize this medical text in Arabic, focus on USMLE points and PubMed 2024-2026 links: {snippet}"}],
                        model="llama3-8b-8192",
                    )
                    st.markdown(response.choices[0].message.content)
                except:
                    st.warning("آمال، الملف لسه كبير. جربي رفعه كـ PDF أصغر أو ملف Word.")

    with col2:
        if st.button("🧠 Quick Flashcards"):
            with st.spinner('Creating...'):
                try:
                    response = client.chat.completions.create(
                        messages=[{"role": "user", "content": f"Create 3 USMLE style flashcards in Arabic from: {text_content[:3000]}"}],
                        model="llama3-8b-8192",
                    )
                    st.info(response.choices[0].message.content)
                except:
                    st.error("Error creating flashcards.")
