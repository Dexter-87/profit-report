import pandas as pd
import streamlit as st
from matplotlib import pyplot as plt

st.set_page_config(page_title="Финансы", layout="wide")

# -------- ДАННЫЕ --------

sales_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTVCDzAu1DphzNCs2AzlpsjgJyRfzYWEAicdYbqMEFCcjjcxo4WyjVkcKa2-6G2BDyhM2GaBRx23DvO/pub?gid=1240951053&single=true&output=csv"
expenses_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSYEdrQn9FbW5xYzz_UuvUvOUYxbENvC1JnSE4z00YUTvtCxtnP4sU54J-Vs_40kEcuyQLRm-Ae6B_0/pub?gid=1622934317&single=true&output=csv"

@st.cache_data(ttl=60)
def load():
    return pd.read_csv(sales_url), pd.read_csv(expenses_url)

sales_raw, exp_raw = load()

df = sales_raw.copy()
exp = exp_raw.copy()

# -------- ОБРАБОТКА --------

df.columns = df.columns.str.strip()
exp.columns = exp.columns.str.strip()

df["Дата"] = pd.to_datetime(df["Дата"], dayfirst=True, errors="coerce")
exp["Дата"] = pd.to_datetime(exp["Дата"], dayfirst=True, errors="coerce")

df["РРЦ"] = pd.to_numeric(df["РРЦ"], errors="coerce").fillna(0)
df["Себестоимость"] = pd.to_numeric(df["Себестоимость"], errors="coerce").fillna(0)
df["Комиссия Kaspi"] = pd.to_numeric(df["Комиссия Kaspi"], errors="coerce").fillna(0)

df["Прибыль"] = df["РРЦ"] - df["Себестоимость"] - df["Комиссия Kaspi"]

# FIX маржи
df["Маржа %"] = (df["Прибыль"] / df["РРЦ"] * 100).fillna(0)

df["Комментарий"] = df["Комментарий"].fillna("").astype(str).str.strip()
df["Это Ariston"] = df["Наименование"].str.lower().str.contains("ariston", na=False)
df["Плюс"] = df["Комментарий"] == "+"

# -------- UI --------

st.title("Финансовая сводка")

# -------- ФИЛЬТРЫ --------

col1, col2, col3 = st.columns(3)

min_date = df["Дата"].min().date()
max_date = df["Дата"].max().date()

with col1:
    date_from = st.date_input("С", min_date)

with col2:
    date_to = st.date_input("По", max_date)

channel_values = sorted([x for x in df["Канал"].dropna().unique()])
channel_options = ["Все"] + channel_values

with col3:
    selected_channel = st.selectbox("Канал", channel_options)

# -------- ФИЛЬТР --------

df = df[(df["Дата"].dt.date >= date_from) & (df["Дата"].dt.date <= date_to)]

if selected_channel != "Все":
    df = df[df["Канал"] == selected_channel]

exp = exp[(exp["Дата"].dt.date >= date_from) & (exp["Дата"].dt.date <= date_to)]

# -------- РАСЧЕТ --------

df["Мой"] = 0.0
df.loc[df["Это Ariston"], "Мой"] = df["Прибыль"] / 2
df.loc[~df["Это Ariston"] & df["Плюс"], "Мой"] = df["Прибыль"] / 2

df["Алексей"] = 0.0
df.loc[df["Это Ariston"], "Алексей"] = df["Прибыль"] / 2
df.loc[~df["Это Ariston"] & df["Плюс"], "Алексей"] = df["Прибыль"] / 2
df.loc[~df["Это Ariston"] & ~df["Плюс"], "Алексей"] = df["Прибыль"]

my = df["Мой"].sum()
alex = df["Алексей"].sum()
expenses = exp["Сумма"].sum()

my -= expenses / 2
alex -= expenses / 2

total = my + alex

# -------- ВЫВОД --------

c1, c2, c3 = st.columns(3)

c1.metric("Мой", int(my))
c2.metric("Алексей", int(alex))
c3.metric("Итого", int(total))

st.divider()

c1, c2, c3 = st.columns(3)

c1.metric("Количество", len(df))
c2.metric("Средний чек", int(df["РРЦ"].mean()) if len(df) else 0)
c3.metric("Маржа %", round(df["Маржа %"].mean(), 1))

st.divider()

# -------- ГРАФИК --------

daily = df.groupby(df["Дата"].dt.date)["Прибыль"].sum()

st.line_chart(daily)

# -------- ТОП --------

top = df.groupby("Наименование")["Прибыль"].sum().sort_values(ascending=False).head(5)

st.bar_chart(top)

# -------- РАСХОДЫ --------

st.subheader("Расходы")
st.metric("Общие расходы", int(expenses))

