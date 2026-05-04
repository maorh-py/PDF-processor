import streamlit as st
import pdfplumber
import pandas as pd

# פונקציה לתיקון עברית הפוכה מה-PDF
def reverse_hebrew(text):
    if isinstance(text, str):
        # בודק אם יש אותיות בעברית בתוך התא
        if any("\u0590" <= char <= "\u05FF" for char in text):
            return text[::-1]
    return text

st.set_page_config(page_title="PDF to Sheets Data", layout="wide")
st.title("✂️ חילוץ ערכים לסידור עבודה")
st.write("העתק את הערכים והדבק ב-Sheets באמצעות 'הדבקה מיוחדת' -> 'ערכים בלבד'")

uploaded_file = st.file_uploader("העלה את קובץ ה-PDF", type="pdf")

if uploaded_file:
    try:
        with pdfplumber.open(uploaded_file) as pdf:
            all_data = []
            for page in pdf.pages:
                table = page.extract_table()
                if table:
                    all_data.extend(table)
            
            if all_data:
                # יצירת הטבלה ותיקון עברית בכל התאים
                df = pd.DataFrame(all_data).map(reverse_hebrew).fillna("")

                # הצגת הנתונים בתיבת קוד להעתקה מהירה
                # sep='\t' מבטיח שהדבקה ב-Sheets תפצל את הנתונים לעמודות הנכונות
                clean_text = df.to_csv(index=False, sep='\t', header=False)
                
                st.success("הנתונים מוכנים להעתקה!")
                
                st.write("לחץ על כפתור ההעתקה (אייקון הדפים) למעלה מימין:")
                st.code(clean_text, language=None)
                
                st.divider()
                st.write("תצוגה מקדימה של הנתונים:")
                st.dataframe(df)
            else:
                st.error("לא הצלחתי למצוא טבלה בקובץ ה-PDF.")
    except Exception as e:
        st.error(f"שגיאה בעיבוד הקובץ: {e}")
