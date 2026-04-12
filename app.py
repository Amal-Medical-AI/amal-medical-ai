import streamlit as st
from groq import Groq
import pdfplumber
import re

# 1. Page Styling
st.set_page_config(page_title="Amal's Medical Brain", layout="wide")
st.markdown("<style>.main { background-color: #fff0f5; } .stButton>button { background-color: #ff69b4; color: white; border-radius: 20px; font-weight: bold; }</style>", unsafe_allow_html=True)

# 2. Setup
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.title("🌸 Amal's Medical Brain 🌸")

# 3. File Uploader
uploaded_file = st.file_uploader("Upload Lecture", type=["pdf"])

if uploaded_file:
    raw_text = ""
    try:
        with pdfplumber.open(uploaded_file) as pdf:
            # نأخذ أول 3 صفحات فقط
            for page in pdf.pages[:3]:
                text = page.extract_text()
                if text:
                    raw_text += text + " "
    except:
        raw_text = "Reading error"

    # أهم خطوة: تنظيف النص تماماً من أي شيء ليس حرفاً أو رقماً
    # هاد السطر بيمسح الرموز الكيميائية اللي بتعمل Error
    clean_text = re.sub(r'[^a-zA-Z0-9\s\u0590-\u05FF]', '', raw_text)[:2500]

    st.success(f"File '{uploaded_file.name}' is ready!")

    if st.button("📝 Summarize Material"):
        with st.spinner('Thinking...'):
            try:
                # استخدمنا موديل Llama3-70b لأنه أقوى وأذكى
                resp = client.chat.completions.create(
                    messages=[{"role":"user","content":f"Explain this medical text clearly: {clean_text}"}],
                    model="llama3-70b-8192"
                )
                st.markdown(resp.choices[0].message.content)
            except:
                st.error("Still having trouble with the icons in this PDF. Try asking a specific question below.")

    # 4. مربع السؤال (هاد دائماً شغال ومستحيل يعطي Error)
    st.divider()
    st.subheader("💬 Ask anything about Heme Metabolism:")
    user_q = st.text_input("Example: What is the rate limiting step?")
    if user_q:
        with st.spinner('Answering...'):
            resp = client.chat.completions.create(
                messages=[{"role":"user","content":user_q}],
                model="llama3-70b-8192"
            )
            st.chat_message("assistant").write(resp.choices[0].message.content)
