import streamlit as st
import pdfplumber
import pandas as pd
import requests
import io
import re

def reverse_hebrew(text):
    if isinstance(text, str):
        if any("\u0590" <= char <= "\u05FF" for char in text):
            return text[::-1]
    return text

def download_pdf_from_drive(url):
    # חילוץ ה-ID של הקובץ מתוך הקישור שהדבקת
    file_id_match = re.search(r'd/([^/]+)', url)
    if not file_id_match:
        st.error("הקישור לא נראה כמו קישור תקין של גוגל דרייב.")
        return None
    
    file_id = file_id_match.group(1)
    # יצירת קישור הורדה ישיר
    download_url = f'https://google.com{file_id}'
    
    response = requests.get(download_url)
    if response.status_code == 200:
        return io.BytesIO(response.content)
    else:
        st.error("גוגל חסם את ההורדה. וודא שהקובץ מוגדר כ-Anyone with the link.")
        return None

st.title("✂️ חילוץ ערכים מ-PDF")

source = st.radio("בחר מקור קובץ:", ("העלאה מהמכשיר", "קישור מגוגל דרייב"))

pdf_file = None

if source == "העלאה מהמכשיר":
    pdf_file = st.file_uploader("העלה PDF", type="pdf")
else:
    drive_url = st.text_input("הדבק כאן קישור לשיתוף מהגוגל דרייב:")
    if drive_url:
        pdf_file = download_pdf_from_drive(drive_url)

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
            else:
                st.error("לא נמצאה טבלה בקובץ.")
    except Exception as e:
        st.error(f"שגיאה בעיבוד: {e}")
