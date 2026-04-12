import streamlit as st
from groq import Groq
import PyPDF2
import re

# 1. إعدادات الصفحة والستايل الطبي
st.set_page_config(page_title="Amal's Medical Brain", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #fff0f5; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #ff69b4; color: white; font-weight: bold; height: 3em; border: none; }
    h1, h3 { color: #ff69b4; text-align: center; font-family: 'Arial'; }
    .stTextInput>div>div>input { border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# 2. إعداد الـ API والذاكرة
# تأكدي من وجود GROQ_API_KEY في ملف الـ secrets
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "lecture_memory" not in st.session_state:
    st.session_state.lecture_memory = []

st.title("🌸 Amal's Medical Brain 🌸")

# 3. القائمة الجانبية (Sidebar)
st.sidebar.title("🧠 Study Memory")
if st.session_state.lecture_memory:
    for item in st.session_state.lecture_memory:
        st.sidebar.write(f"📖 {item['name']}")
else:
    st.sidebar.write("No history yet. Upload a lecture!")

# 4. معالج الملفات الذكي
uploaded_file = st.file_uploader("Upload Medical Lecture (PDF)", type=["pdf"])

if uploaded_file:
    raw_text = ""
    # شريط تقدم لرفع "الغموض" عن المستخدم
    progress_bar = st.progress(0)
    
    try:
        reader = PyPDF2.PdfReader(uploaded_file)
        # نأخذ أول 6 صفحات لضمان عدم تجاوز حد الكلمات المسموح
        pages_to_read = min(len(reader.pages), 6)
        
        for i in range(pages_to_read):
            page_text = reader.pages[i].extract_text()
            if page_text:
                raw_text += page_text + " "
            progress_bar.progress((i + 1) / pages_to_read)
        
        # تنظيف النص: إزالة المسافات والرموز التي تعيق الـ AI
        clean_text = re.sub(r'\s+', ' ', raw_text).strip()
        clean_text = clean_text[:5000] # تحديد الحجم لضمان الاستقرار

        if uploaded_file.name not in [d['name'] for d in st.session_state.lecture_memory]:
            st.session_state.lecture_memory.append({"name": uploaded_file.name, "summary": clean_text[:500]})
        
        st.success(f"✅ Lecture '{uploaded_file.name}' loaded successfully!")

        # 5. دالة النداء الآمن للـ AI (باستخدام الموديل الجديد)
        def ask_medical_ai(prompt_text):
            try:
                # الموديل الجديد llama-3.3-70b-versatile بدلاً من القديم
                completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "You are a professional medical assistant for USMLE prep."},
                        {"role": "user", "content": prompt_text}
                    ],
                    model="llama-3.3-70b-versatile",
                    temperature=0.5,
                    max_tokens=1500
                )
                return completion.choices[0].message.content
            except Exception as e:
                return f"⚠️ API Error: {str(e)}"

        # 6. الأزرار التفاعلية
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📝 Summarize & Connect"):
                with st.spinner('Thinking...'):
                    past = ", ".join([d['name'] for d in st.session_state.lecture_memory[:-1]])
                    prompt = f"Summarize this medical text and connect it to previous topics ({past}): {clean_text}"
                    st.markdown(ask_medical_ai(prompt))

        with col2:
            if st.button("❓ Active Recall Mode"):
                with st.spinner('Generating Questions...'):
                    prompt = f"Create 4 high-yield USMLE questions based on: {clean_text}"
                    st.info(ask_medical_ai(prompt))

        with col3:
            if st.button("🧠 Flashcards"):
                with st.spinner('Creating Cards...'):
                    prompt = f"Create 5 active recall flashcards for: {clean_text}"
                    st.warning(ask_medical_ai(prompt))

        # 7. نظام الدردشة المباشرة
        st.divider()
        st.subheader("💬 Ask about this lecture")
        user_q = st.text_input("Type your medical question here...")
        if user_q:
            with st.spinner('Searching brain...'):
                full_prompt = f"Context: {clean_text[:2500]}\nQuestion: {user_q}"
                answer = ask_medical_ai(full_prompt)
                st.chat_message("assistant").write(answer)

    except Exception as e:
        st.error(f"Error processing file: {e}")
