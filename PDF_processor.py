import streamlit as st
import pdfplumber
import pandas as pd
import io
from streamlit_components_auth import st_copy_to_clipboard # אופציונלי, נשתמש בשיטה פשוטה יותר

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
                df = df.dropna(how='all')
                
                st.success("הטבלה מוכנה!")
                
                # יצירת מחרוזת טקסט להעתקה (מופרדת בטאבים - מתאים בול לשייטס)
                text_to_copy = df.to_csv(index=False, sep='\t', header=False)
                
                # כפתור העתקה מובנה של Streamlit (זמין בגרסאות חדשות)
                st.code(text_to_copy, language=None)
                st.info("לחץ על כפתור ההעתקה בפינה הימנית של תיבת הטקסט למעלה, ואז הדבק ב-Sheets")

                st.divider()
                
                # כפתור הורדה כגיבוי
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, header=False)
                
                st.download_button(
                    label="📥 או הורד כקובץ אקסל",
                    data=buffer.getvalue(),
                    file_name="converted_data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.error("לא נמצאה טבלה בקובץ.")
    except Exception as e:
        st.error(f"שגיאה בעיבוד הקובץ: {e}")
