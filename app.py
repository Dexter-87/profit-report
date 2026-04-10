import pandas as pd
import streamlit as st

st.set_page_config(page_title="МАМА Я ТЕБЯ ЛЮБЛЮ)))))", layout="wide")

# ссылки
sales_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTVCDzAu1DphzNCs2AzlpsjgJyRfzYWEAicdYbqMEFCcjjcxo4WyjVkcKa2-6G2BDyhM2GaBRx23DvO/pub?gid=1240951053&single=true&output=csv"

# загрузка данных
@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(sales_url)
    df.columns = df.columns.str.strip()
    return df

st.title("Отчет по прибыли")

try:
    df = load_data()

    st.success("Данные успешно загружены ✅")
    st.write(df.head())

except Exception as e:
    st.error("Ошибка загрузки данных")
    st.write(e)
