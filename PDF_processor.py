import streamlit as st
import pdfplumber
import pandas as pd
import io

st.set_page_config(page_title="PDF to Sheets Converter", layout="wide")
st.title("📄 ממיר PDF לטבלה עבור Google Sheets")

uploaded_file = st.file_uploader("העלה קובץ PDF", type="pdf")

if uploaded_file:
    with pdfplumber.open(uploaded_file) as pdf:
        page = pdf.pages[0] # עמוד ראשון
        table = page.extract_table()
        
        if table:
            df = pd.DataFrame(table[1:], columns=table[0])
            st.success("הטבלה זוהתה!")
            st.dataframe(df)
            
            # יצירת קובץ אקסל בזיכרון
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            
            st.download_button(
                label="📥 הורד קובץ ל-Google Sheets",
                data=buffer.getvalue(),
                file_name="converted_data.xlsx",
                mime="application/vnd.ms-excel"
            )
        else:
            st.error("לא נמצאה טבלה ברורה בקובץ.")
