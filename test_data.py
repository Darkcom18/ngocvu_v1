import streamlit as st
import pandas as pd
from datetime import datetime

# Thay thế 'your_csv_url' bằng URL CSV bạn đã sao chép từ Google Sheets
url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQjF-vOUyngQKPRXkYvKwIDMAAoK5Jm_RGblSz2FLJsRDmu8IwfwJpfgcPgAY16FmXMN3tBKIPslHem/pub?gid=568267471&single=true&output=csv'
data = pd.read_csv(url,sep=',',header=0)
data.info()
print(data.head())
# Chuyển đổi cột ngày từ chuỗi sang định dạng datetime
data['Ngày'] = pd.to_datetime(data['Ngày'], format='%d/%m/%y', errors='coerce')
data.info()