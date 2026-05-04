import streamlit as st
import pdfplumber
import pandas as pd
import io
import re
from bidi.algorithm import get_display

def fix_hebrew(text):
    if not isinstance(text, str):
        return text
    # בודק אם יש עברית בטקסט
    if re.search(r'[\u0590-\u05FF]', text):
        # הופך את סדר האותיות כדי שיוצג נכון
        return get_display(text)
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
                
                # החלת תיקון העברית על כל תא בטבלה
                df = df.applymap(fix_hebrew)
                
                df = df.dropna(how='all')
                
                st.success("הטבלה מוכנה עם תיקון עברית!")
                
                # העתקה בפורמט טאבים לשייטס
                text_to_copy = df.to_csv(index=False, sep='\t', header=False)
                st.code(text_to_copy, language=None)

                st.divider()
                
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, header=False)
                
                st.download_button(label="📥 הורד קובץ אקסל", data=buffer.getvalue(), 
                                 file_name="fixed_hebrew_table.xlsx", 
                                 mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            else:
                st.error("לא נמצאה טבלה בקובץ.")
    except Exception as e:
        st.error(f"שגיאה בעיבוד הקובץ: {e}")
