import streamlit as st
from groq import Groq
import fitz  # PyMuPDF
import re

# 1. Styling
st.set_page_config(page_title="Amal's Medical Brain", layout="wide")
st.markdown("<style>.main { background-color: #fff0f5; } .stButton>button { background-color: #ff69b4; color: white; border-radius: 20px; font-weight: bold; }</style>", unsafe_allow_html=True)

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.title("🌸 Amal's Medical Brain 🌸")

uploaded_file = st.file_uploader("Upload Lecture", type=["pdf"])

if uploaded_file:
    full_text = ""
    try:
        # فتح الملف باستخدام PyMuPDF لقراءة النصوص بذكاء أعلى
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
            for page in doc:
                full_text += page.get_text()
    except:
        full_text = "Reading error"

    # السطر السحري: بيمسح أي شيء مش حرف أو رقم (بشيل كل الرموز الكيميائية اللي بتعمل Error)
    clean_text = re.sub(r'[^a-zA-Z0-9\s\u0590-\u05FF]', '', full_text)[:3000]

    st.success(f"✅ Ready: {uploaded_file.name}")

    if st.button("📝 Summarize"):
        with st.spinner('Analyzing...'):
            try:
                # استخدمنا موديل Llama 3 70B لأنه بيتحمل ملفات أكبر وأذكى
                resp = client.chat.completions.create(
                    messages=[{"role":"user","content":f"Summarize this medical text clearly: {clean_text}"}],
                    model="llama3-70b-8192"
                )
                st.markdown(resp.choices[0].message.content)
            except:
                st.error("Text complexity error. Please use the chat box below.")

    st.divider()
    st.subheader("💬 Chat with your Lecture")
    user_q = st.text_input("Ask a question about the material:")
    if user_q:
        with st.spinner('Thinking...'):
            resp = client.chat.completions.create(
                messages=[{"role":"user","content":f"Context: {clean_text}\nQuestion: {user_q}"}],
                model="llama3-70b-8192"
            )
            st.chat_message("assistant").write(resp.choices[0].message.content)
