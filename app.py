import pandas as pd
import streamlit as st
from matplotlib import pyplot as plt

st.set_page_config(page_title="Финансы", layout="wide")

# ---------------- СТИЛИ ----------------
st.markdown("""
<style>

.stApp {
    background: #12151c;
    color: #f3f4f6;
}

.block-container {
    padding-top: 1.5rem;
}

.section {
    background: #1a1f2b;
    border: 1px solid #2d3445;
    border-radius: 18px;
    padding: 16px;
    margin-bottom: 16px;
}

.title {
    font-size: 36px;
    font-weight: 800;
}

.subtitle {
    color: #9ca3af;
    margin-bottom: 10px;
}

.metric {
    font-size: 26px;
    font-weight: 700;
}

.green { color: #22c55e; }
.red { color: #ef4444; }

input {
    color: #f3f4f6 !important;
}

</style>
""", unsafe_allow_html=True)

# ---------------- ДАННЫЕ ----------------

sales_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTVCDzAu1DphzNCs2AzlpsjgJyRfzYWEAicdYbqMEFCcjjcxo4WyjVkcKa2-6G2BDyhM2GaBRx23DvO/pub?gid=1240951053&single=true&output=csv"
expenses_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSYEdrQn9FbW5xYzz_UuvUvOUYxbENvC1JnSE4z00YUTvtCxtnP4sU54J-Vs_40kEcuyQLRm-Ae6B_0/pub?gid=1622934317&single=true&output=csv"

@st.cache_data(ttl=60)
def load():
    return pd.read_csv(sales_url), pd.read_csv(expenses_url)

sales_raw, exp_raw = load()

df = sales_raw.copy()
exp = exp_raw.copy()

# ---------------- ОБРАБОТКА ----------------

df.columns = df.columns.str.strip()
exp.columns = exp.columns.str.strip()

df["Дата"] = pd.to_datetime(df["Дата"], dayfirst=True, errors="coerce")
exp["Дата"] = pd.to_datetime(exp["Дата"], dayfirst=True, errors="coerce")

df["РРЦ"] = pd.to_numeric(df["РРЦ"], errors="coerce").fillna(0)
df["Себестоимость"] = pd.to_numeric(df["Себестоимость"], errors="coerce").fillna(0)
df["Комиссия Kaspi"] = pd.to_numeric(df["Комиссия Kaspi"], errors="coerce").fillna(0)

df["Прибыль"] = df["РРЦ"] - df["Себестоимость"] - df["Комиссия Kaspi"]

# маржа FIX
df["Маржа %"] = (df["Прибыль"] / df["РРЦ"] * 100).fillna(0)

df["Комментарий"] = df["Комментарий"].fillna("").astype(str).str.strip()
df["Это Ariston"] = df["Наименование"].str.lower().str.contains("ariston", na=False)
df["Плюс"] = df["Комментарий"] == "+"

# ---------------- UI ----------------

st.markdown('<div class="title">Финансовая сводка</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Продажи • Прибыль • Контроль</div>', unsafe_allow_html=True)

# -------- ФИЛЬТРЫ --------

st.markdown('<div class="section">', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)

min_date = df["Дата"].min().date()
max_date = df["Дата"].max().date()

with c1:
    date_from = st.date_input("С", value=min_date)

with c2:
    date_to = st.date_input("По", value=max_date)

channel_values = sorted([x for x in df["Канал"].dropna().unique()])
channel_options = ["Все"] + channel_values

with c3:
    selected_channel = st.selectbox("Канал", channel_options)

st.markdown('</div>', unsafe_allow_html=True)

# -------- ФИЛЬТРЫ ПРИМЕНЕНИЕ --------

df = df[(df["Дата"].dt.date >= date_from) & (df["Дата"].dt.date <= date_to)]

if selected_channel != "Все":
    df = df[df["Канал"] == selected_channel]

exp = exp[(exp["Дата"].dt.date >= date_from) & (exp["Дата"].dt.date <= date_to)]

# -------- РАСЧЕТЫ --------

df["Мой"] = 0.0
df.loc[df["Это Ariston"], "Мой"] = df["Прибыль"] / 2
df.loc[~df["Это Ariston"] & df["Плюс"], "Мой"] = df["Прибыль"] / 2

df["Алексей"] = 0.0
df.loc[df["Это Ariston"], "Алексей"] = df["Прибыль"] / 2
df.loc[~df["Это Ariston"] & df["Плюс"], "Алексей"] = df["Прибыль"] / 2
df.loc[~df["Это Ariston"] & ~df["Плюс"], "Алексей"] = df["Прибыль"]

my = df["Мой"].sum()
alex = df["Алексей"].sum()
total = my + alex

expenses = exp["Сумма"].sum()
my -= expenses/2
alex -= expenses/2

# -------- КАРТОЧКИ --------

st.markdown('<div class="section">', unsafe_allow_html=True)

m1, m2, m3 = st.columns(3)

with m1:
    st.markdown(f'<div class="metric green">{int(my)} ₸</div>Мой', unsafe_allow_html=True)

with m2:
    st.markdown(f'<div class="metric green">{int(alex)} ₸</div>Алексей', unsafe_allow_html=True)

with m3:
    st.markdown(f'<div class="metric">{int(total)} ₸</div>Итого', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# -------- ПРОДАЖИ --------

st.markdown('<div class="section">', unsafe_allow_html=True)

st.subheader("Продажи")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Количество", len(df))

with col2:
    st.metric("Средний чек", int(df["РРЦ"].mean()) if len(df) else 0)

with col3:
    st.metric("Маржа %", round(df["Маржа %"].mean(), 1))

st.markdown('</div>', unsafe_allow_html=True)

# -------- ГРАФИК --------

st.subheader("Динамика прибыли")

daily = df.groupby(df["Дата"].dt.date)["Прибыль"].sum()

fig, ax = plt.subplots()
fig.patch.set_facecolor("#12151c")
ax.set_facecolor("#12151c")

ax.plot(daily.index, daily.values, color="#22c55e", marker="o")

st.pyplot(fig)

# -------- ТОП --------

st.subheader("Топ товаров")

top = df.groupby("Наименование")["Прибыль"].sum().sort_values(ascending=False).head(5)

st.bar_chart(top)

# -------- РАСХОДЫ --------

st.markdown('<div class="section">', unsafe_allow_html=True)

st.subheader("Расходы")

st.markdown(f'<div class="metric red">{int(expenses)} ₸</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
