import streamlit as st
import pdfplumber
import pandas as pd
import io

# פונקציה פשוטה להיפוך טקסט במידה והוא מכיל עברית
def reverse_hebrew(text):
    if isinstance(text, str):
        # בודק אם יש לפחות אות אחת בעברית
        if any("\u0590" <= char <= "\u05FF" for char in text):
            return text[::-1] # הופך את סדר האותיות
    return text

st.set_page_config(page_title="PDF to Sheets", layout="wide")
st.title("📄 ממיר PDF לטבלה")

uploaded_file = st.file_uploader("העלה קובץ PDF", type="pdf")

if uploaded_file:
    try:
        with pdfplumber.open(uploaded_file) as pdf:
            all_data = []
            for page in pdf.pages:
                table = page.extract_table()
                if table:
                    all_data.extend(table)
            
            if all_data:
                df = pd.DataFrame(all_data)
                
                # תיקון השגיאה: שימוש ב-map במקום applymap
                df = df.map(reverse_hebrew)
                
                df = df.dropna(how='all')
                
                st.success("הטבלה עובדה! בדוק אם העברית מסודרת בתיבה למטה:")
                
                # יצירת מחרוזת להעתקה
                text_to_copy = df.to_csv(index=False, sep='\t', header=False)
                st.code(text_to_copy, language=None)

                st.divider()
                
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, header=False)
                
                st.download_button(
                    label="📥 הורד קובץ אקסל",
                    data=buffer.getvalue(),
                    file_name="fixed_table.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.error("לא נמצאה טבלה בקובץ.")
    except Exception as e:
        st.error(f"שגיאה בעיבוד הקובץ: {e}")
