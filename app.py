import streamlit as st
import pandas as pd

st.set_page_config(page_title="Отчет по прибыли", layout="wide")

st.title("Отчет по прибыли")

# ===== ССЫЛКИ НА GOOGLE DRIVE =====
sales_url = "https://docs.google.com/spreadsheets/d/1G3uWX47NGYgEYWhV6yZkW-Aca_6wRz-e/export?format=csv"
expenses_url = "https://docs.google.com/spreadsheets/d/1N28HP0kI22xru71rBiHKpuo9M1HRo8YC/export?format=csv"

# ===== ЗАГРУЗКА ДАННЫХ =====
@st.cache_data
def load_data():
    sales = pd.read_csv(sales_url)
    expenses = pd.read_csv(expenses_url)
    return sales, expenses

sales, expenses = load_data()

# ===== ВЫВОД =====
st.subheader("Продажи")
st.dataframe(sales)

st.subheader("Расходы")
st.dataframe(expenses)
