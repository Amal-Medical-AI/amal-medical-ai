import streamlit as st
import os

# إعداد واجهة الموقع
st.set_page_config(page_title="Amal's Medical Brain 🌸", layout="wide")

# تصميم بسيط وجميل
st.markdown("""
    <style>
    .main { background-color: #fff0f5; }
    h1 { color: #ff69b4; text-align: center; }
    .stButton>button { background-color: #ff69b4; color: white; border-radius: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌸 Amal's Medical Brain 🌸")
st.subheader("مساعدكِ الطبي الشخصي للتلخيص والبحث")

# مكان رفع الملفات
uploaded_file = st.file_uploader("ارفعي محاضرة التكنيون (PDF)", type="pdf")

if uploaded_file:
    st.success("تم رفع الملف بنجاح! جاري التحليل...")
    
    # أزرار الوظائف
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📝 تلخيص المحاضرة"):
            st.info("هنا سيظهر التلخيص بأسلوب الطلاب الصينيين...")
            
    with col2:
        if st.button("🧠 إنشاء Flashcards"):
            st.info("سؤال 1: ما هو المبدأ الأساسي في هذه المادة؟")
            
    with col3:
        if st.button("🔍 أبحاث PubMed الجديدة"):
            st.info("جاري البحث عن أحدث أبحاث 2024-2026...")

st.sidebar.title("ذاكرة USMLE")
st.sidebar.write("هذا الموضوع مرتبط بـ Step 1.")
