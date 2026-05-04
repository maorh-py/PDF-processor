import streamlit as st
import pdfplumber
import pandas as pd
import io

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
                # יצירת DataFrame ללא הגדרת כותרות בשלב הראשון
                df = pd.DataFrame(all_data)
                
                # ניקוי שורות ריקות לחלוטין
                df = df.dropna(how='all')
                
                st.success("הטבלה חולצה בהצלחה!")
                
                # הצגת הטבלה ללא כותרות כדי למנוע את השגיאה
                st.write("תצוגה מקדימה:")
                st.dataframe(df) 
                
                # יצירת קובץ אקסל להורדה
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    # כאן אנחנו שומרים את הנתונים כמו שהם
                    df.to_excel(writer, index=False, header=False)
                
                st.download_button(
                    label="📥 הורד קובץ ל-Google Sheets",
                    data=buffer.getvalue(),
                    file_name="converted_data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.error("לא נמצאה טבלה בקובץ.")
    except Exception as e:
        st.error(f"שגיאה בעיבוד הקובץ: {e}")
