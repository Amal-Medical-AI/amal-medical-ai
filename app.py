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
    .sidebar .sidebar-content { background-image: linear-gradient(#fff0f5, #ffffff); }
    </style>
    """, unsafe_allow_html=True)

# 2. Setup & Memory Initialization
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "lecture_memory" not in st.session_state:
    st.session_state.lecture_memory = [] # يحفظ ملخصات المواضيع السابقة للربط

st.title("🌸 Amal's Medical Brain 🌸")

# 3. Sidebar (الذاكرة المستمرة)
st.sidebar.title("🧠 Study Memory")
if st.session_state.lecture_memory:
    for item in st.session_state.lecture_memory:
        st.sidebar.write(f"📖 {item['name']}")
else:
    st.sidebar.write("No history yet. Upload a lecture!")

# 4. File Uploader
uploaded_file = st.file_uploader("Upload Medical Lecture", type=["pdf"])

if uploaded_file:
    raw_text = ""
    try:
        reader = PyPDF2.PdfReader(uploaded_file)
        for page in reader.pages[:4]:
            raw_text += page.extract_text() + " "
    except:
        st.error("Error reading file.")

    clean_text = re.sub(r'[^a-zA-Z0-9\s\u0590-\u05FF]', '', raw_text)[:3000]

    # حفظ الملف في الذاكرة للربط مستقبلاً
    if uploaded_file.name not in [d['name'] for d in st.session_state.lecture_memory]:
        st.session_state.lecture_memory.append({"name": uploaded_file.name, "summary": clean_text[:500]})

    st.success(f"Ready to analyze: {uploaded_file.name}")

    # 5. الأزرار (كل الخصائص اللي طلبتيها)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📝 Summarize & Connect"):
            with st.spinner('Summarizing and linking...'):
                # نطلب منه يربط مع الملفات اللي في الذاكرة
                past_topics = ", ".join([d['name'] for d in st.session_state.lecture_memory[:-1]])
                prompt = f"Summarize this: {clean_text}. \nRelation to previous topics ({past_topics}): How does this connect to what Amal studied before?"
                resp = client.chat.completions.create(messages=[{"role":"user","content":prompt}], model="llama3-70b-8192")
                st.markdown(resp.choices[0].message.content)

    with col2:
        if st.button("❓ Active Recall Mode"):
            with st.spinner('Generating Q&A...'):
                prompt = f"Create a Q&A for learning and USMLE prep from: {clean_text}"
                resp = client.chat.completions.create(messages=[{"role":"user","content":prompt}], model="llama3-70b-8192")
                st.info(resp.choices[0].message.content)

    with col3:
        if st.button("🧠 Flashcards"):
            with st.spinner('Creating Cards...'):
                prompt = f"Create 5 high-yield flashcards from this text: {clean_text}"
                resp = client.chat.completions.create(messages=[{"role":"user","content":prompt}], model="llama3-70b-8192")
                st.warning(resp.choices[0].message.content)

    # 6. Chat Interface
    st.divider()
    user_q = st.text_input("💬 Ask a specific question about this or previous lectures:")
    if user_q:
        with st.spinner('Thinking...'):
            context = "Previous studies: " + str([d['name'] for d in st.session_state.lecture_memory])
            resp = client.chat.completions.create(
                messages=[{"role":"user","content":f"{context}\nNow answer: {user_q}"}],
                model="llama3-70b-8192"
            )
            st.chat_message("assistant").write(resp.choices[0].message.content)
