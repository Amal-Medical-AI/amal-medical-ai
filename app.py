import streamlit as st
from groq import Groq
import PyPDF2

# إعدادات الصفحة والتصميم الزهري
st.set_page_config(page_title="Amal's Medical Brain", layout="wide")
st.markdown("<style>.main { background-color: #fff0f5; } .stButton>button { background-color: #ff69b4; color: white; border-radius: 20px; }</style>", unsafe_allow_html=True)

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.title("🌸 Amal's Medical Brain 🌸")
st.subheader("تحويل المحاضرات إلى نظام سؤال وجواب")

uploaded_file = st.file_uploader("ارفعي ملف المحاضرة هنا", type=["pdf", "docx"])

if uploaded_file:
    text_content = ""
    if uploaded_file.type == "application/pdf":
        reader = PyPDF2.PdfReader(uploaded_file)
        # رح يقرأ المحتوى لغاية 5 صفحات لضمان السرعة
        for page in reader.pages[:5]:
            text_content += page.extract_text()
    
    st.success(f"✅ تم استلام: {uploaded_file.name}")

    # الخيار الجديد اللي طلبتيه
    if st.button("❓ تحويل المادة إلى (سؤال وجواب) تفصيلي"):
        with st.spinner('جاري استخراج الأسئلة من صلب المحاضرة...'):
            try:
                # طلب محدد من الذكاء الاصطناعي لتحويل المادة لأسئلة وأجوبة
                prompt = f"قم بتحويل المادة الطبية التالية إلى قائمة شاملة من الأسئلة والأجوبة (Q&A) باللغة العربية. ركز على النقاط السريرية (Clinical points) وما يهم آمال في USMLE: {text_content[:6000]}"
                
                response = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama3-8b-8192",
                )
                
                st.markdown("### 📝 بنك الأسئلة والأجوبة الخاص بمحاضرتك:")
                st.write(response.choices[0].message.content)
            except:
                st.error("آمال، الملف دسم جداً. جربي رفعه كملف أصغر.")

    # زر إضافي للتلخيص السريع
    if st.button("📋 ملخص سريع للموضوع"):
        with st.spinner('جاري التلخيص...'):
            prompt = f"لخص هذه المادة باختصار شديد لآمال: {text_content[:3000]}"
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-8b-8192",
            )
            st.info(response.choices[0].message.content)
