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
    .stProgress > div > div > div > div { background-color: #ff69b4; }
    </style>
    """, unsafe_allow_html=True)

# 2. Setup & Memory Initialization
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "lecture_memory" not in st.session_state:
    st.session_state.lecture_memory = []

st.title("🌸 Amal's Medical Brain 🌸")

# 3. Sidebar
st.sidebar.title("🧠 Study Memory")
if st.session_state.lecture_memory:
    for item in st.session_state.lecture_memory:
        st.sidebar.write(f"📖 {item['name']}")
else:
    st.sidebar.write("No history yet. Upload a lecture!")

# 4. File Uploader & Smart Processing
uploaded_file = st.file_uploader("Upload Medical Lecture (Large PDFs supported)", type=["pdf"])

if uploaded_file:
    raw_text = ""
    progress_bar = st.progress(0) # شريط تقدم لرفع الغموض
    
    try:
        reader = PyPDF2.PdfReader(uploaded_file)
        total_pages = len(reader.pages)
        # قراءة ذكية: نأخذ عينات من الملف إذا كان ضخماً جداً (أول 10 صفحات مثلاً)
        pages_to_read = min(total_pages, 10) 
        
        for i in range(pages_to_read):
            raw_text += reader.pages[i].extract_text() + " "
            progress_bar.progress((i + 1) / pages_to_read)
            
        st.success(f"Successfully processed {pages_to_read} pages of {uploaded_file.name}")
    except Exception as e:
        st.error(f"Error reading file: {e}")

    # تنظيف النص وتحديد حجمه (للمحافظة على الذاكرة)
    clean_text = re.sub(r'[^a-zA-Z0-9\s\u0590-\u05FF]', '', raw_text)[:6000] # زدنا السعة لـ 6000 حرف

    if uploaded_file.name not in [d['name'] for d in st.session_state.lecture_memory]:
        st.session_state.lecture_memory.append({"name": uploaded_file.name, "summary": clean_text[:500]})

    # 5. Buttons Logic
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📝 Summarize & Connect"):
            with st.spinner('Linking with previous knowledge...'):
                past_topics = ", ".join([d['name'] for d in st.session_state.lecture_memory[:-1]])
                prompt = f"Context: {clean_text}\n\nTask: Summarize and relate to: {past_topics}"
                resp = client.chat.completions.create(messages=[{"role":"user","content":prompt}], model="llama3-70b-8192")
                st.markdown(resp.choices[0].message.content)

    with col2:
        if st.button("❓ Active Recall Mode"):
            with st.spinner('Creating high-yield questions...'):
                prompt = f"Based on this: {clean_text}\nCreate 5 USMLE-style questions."
                resp = client.chat.completions.create(messages=[{"role":"user","content":prompt}], model="llama3-70b-8192")
                st.info(resp.choices[0].message.content)

    with col3:
        if st.button("🧠 Flashcards"):
            with st.spinner('Generating flashcards...'):
                prompt = f"Create 5 flashcards for: {clean_text}"
                resp = client.chat.completions.create(messages=[{"role":"user","content":prompt}], model="llama3-70b-8192")
                st.warning(resp.choices[0].message.content)

    # 6. Smart Chat
    st.divider()
    user_q = st.text_input("💬 Ask about this or previous lectures:")
    if user_q:
        with st.spinner('Searching your medical brain...'):
            context = "Previous studies: " + str([d['name'] for d in st.session_state.lecture_memory])
            resp = client.chat.completions.create(
                messages=[{"role":"system", "content": f"You are a medical AI assistant. Current Context: {clean_text}"},
                          {"role":"user","content":f"{context}\nQuestion: {user_q}"}],
                model="llama3-70b-8192"
            )
            st.chat_message("assistant").write(resp.choices[0].message.content)
