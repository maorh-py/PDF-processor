import streamlit as st
import pdfplumber
import pandas as pd
import requests
import io

def reverse_hebrew(text):
    if isinstance(text, str):
        if any("\u0590" <= char <= "\u05FF" for char in text):
            return text[::-1]
    return text

def download_pdf_from_drive(url):
    # המרת קישור שיתוף רגיל לקישור הורדה ישיר
    file_id = url.split('/')[-2]
    d_url = f'https://google.com{file_id}'
    response = requests.get(d_url)
    return io.BytesIO(response.content)

st.set_page_config(page_title="PDF to Sheets Data", layout="wide")
st.title("✂️ חילוץ ערכים מ-PDF (מקומי או דרייב)")

# בחירת מקור הקובץ
source = st.radio("בחר מקור קובץ:", ("העלאה מהמכשיר", "קישור מגוגל דרייב"))

pdf_file = None

if source == "העלאה מהמכשיר":
    pdf_file = st.file_uploader("העלה PDF", type="pdf")
else:
    drive_url = st.text_input("הדבק כאן קישור לשיתוף מהגוגל דרייב:")
    if drive_url:
        try:
            pdf_file = download_pdf_from_drive(drive_url)
        except:
            st.error("לא ניתן להוריד את הקובץ. וודא שהקישור מוגדר כ'ציבורי' (Anyone with the link).")

if pdf_file:
    try:
        with pdfplumber.open(pdf_file) as pdf:
            all_data = []
            for page in pdf.pages:
                table = page.extract_table()
                if table: all_data.extend(table)
            
            if all_data:
                df = pd.DataFrame(all_data).map(reverse_hebrew).fillna("")
                clean_text = df.to_csv(index=False, sep='\t', header=False)
                
                st.success("הנתונים מוכנים!")
                st.code(clean_text, language=None)
                st.dataframe(df)
    except Exception as e:
        st.error(f"שגיאה בעיבוד הקובץ: {e}")
