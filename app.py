import os
from datetime import date
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Финансы", layout="wide")

FILE = "sales.xlsx"

# =====================
# ЗАГРУЗКА
# =====================
@st.cache_data
def load_data():
    try:
        df = pd.read_excel(FILE)
        df["Дата"] = pd.to_datetime(df["Дата"], dayfirst=True, errors="coerce")
        return df
    except:
        return pd.DataFrame()

df = load_data()

# =====================
# РАСЧЕТЫ
# =====================
def calc_money(df):
    stas = 0
    alexey = 0

    for _, row in df.iterrows():
        profit = row.get("Чистая прибыль", 0)
        name = str(row.get("Наименование", "")).lower()
        comment = str(row.get("Комментарий", ""))

        # делим
        if "ariston" in name or "+" in comment:
            stas += profit / 2
            alexey += profit / 2
        else:
            alexey += profit

    return stas, alexey


# =====================
# UI
# =====================
st.title("Финансовая сводка")

col1, col2 = st.columns(2)

with col1:
    date_from = st.date_input("С", value=df["Дата"].min() if not df.empty else date.today())

with col2:
    date_to = st.date_input("По", value=df["Дата"].max() if not df.empty else date.today())

# фильтр
if not df.empty:
    filtered = df[
        (df["Дата"].dt.date >= date_from) &
        (df["Дата"].dt.date <= date_to)
    ]
else:
    filtered = df

# расчет
stas, alexey = calc_money(filtered)
total = stas + alexey

# =====================
# КАРТОЧКИ
# =====================
st.markdown(f"""
### Чистая прибыль  
# {int(total):,} ₸
""")

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"### Стас\n# {int(stas):,} ₸")

with col2:
    st.markdown(f"### Алексей\n# {int(alexey):,} ₸")


# =====================
# ГРАФИК
# =====================
if not filtered.empty:
    chart_df = filtered.copy()
    chart_df["День"] = chart_df["Дата"].dt.strftime("%d.%m")

    daily = chart_df.groupby("День")["Чистая прибыль"].sum().reset_index()

    fig = px.bar(daily, x="День", y="Чистая прибыль")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.write("Нет данных")





Отправлено из мобильной Почты Mail
