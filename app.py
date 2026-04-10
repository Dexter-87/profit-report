import pandas as pd
import streamlit as st

st.set_page_config(page_title="Отчет по прибыли", layout="wide")

st.title("Отчет по прибыли")

# ===== ССЫЛКИ НА GOOGLE TABLES =====
sales_url = "https://docs.google.com/spreadsheets/d/1G3uWX47NGYgEYWhV6yZkW-Aca_6wRz-e/export?format=csv"
expenses_url = "https://docs.google.com/spreadsheets/d/1N28HP0kI22xru71rBiHKpuo9M1HRo8YC/export?format=csv"


# ===== ЗАГРУЗКА ДАННЫХ =====
@st.cache_data
def load_data():
    sales = pd.read_csv(sales_url)
    expenses = pd.read_csv(expenses_url)
    return sales, expenses


sales_df, expenses_df = load_data()


# ===== ОБРАБОТКА ПРОДАЖ =====
def load_sales_dataframe(data):
    df = data.copy()
    df.columns = df.columns.astype(str).str.strip()

    if "Комментарий" not in df.columns:
        df["Комментарий"] = ""

    df["Дата"] = pd.to_datetime(df["Дата"], errors="coerce")
    df["РРЦ"] = pd.to_numeric(df["РРЦ"], errors="coerce").fillna(0)
    df["Себестоимость"] = pd.to_numeric(df["Себестоимость"], errors="coerce").fillna(0)
    df["Комиссия Kaspi"] = pd.to_numeric(df["Комиссия Kaspi"], errors="coerce").fillna(0)

    if "Чистая прибыль" in df.columns:
        df["Прибыль"] = pd.to_numeric(df["Чистая прибыль"], errors="coerce").fillna(0)
    else:
        df["Прибыль"] = df["РРЦ"] - df["Себестоимость"] - df["Комиссия Kaspi"]

    df["Наименование"] = df["Наименование"].fillna("").astype(str).str.strip()

    df["Комментарий"] = df["Комментарий"].fillna("").astype(str)
    df["Комментарий"] = df["Комментарий"].str.replace("\xa0", "", regex=False)
    df["Комментарий"] = df["Комментарий"].str.replace(" ", "", regex=False)
    df["Комментарий"] = df["Комментарий"].str.strip()

    df["Это Ariston"] = df["Наименование"].str.lower().str.contains("ariston", na=False)
    df["Плюс"] = df["Комментарий"] == "+"
    df["Дата_рус"] = df["Дата"].dt.strftime("%d.%m.%Y")

    return df


# ===== ОБРАБОТКА РАСХОДОВ =====
def load_expenses_dataframe(data):
    exp = data.copy()
    exp.columns = exp.columns.astype(str).str.strip()

    if "Дата" in exp.columns:
        exp["Дата"] = pd.to_datetime(exp["Дата"], errors="coerce")
        exp["Дата_рус"] = exp["Дата"].dt.strftime("%d.%m.%Y")

    if "Сумма" in exp.columns:
        exp["Сумма"] = pd.to_numeric(exp["Сумма"], errors="coerce").fillna(0)
    else:
        exp["Сумма"] = 0.0

    return exp


df = load_sales_dataframe(sales_df)
exp = load_expenses_dataframe(expenses_df)


# ===== ФИЛЬТРЫ =====
st.sidebar.header("Фильтры")

valid_dates = df["Дата"].dropna()

if valid_dates.empty:
    st.error("Не удалось распознать даты")
    st.stop()

min_date = valid_dates.min().date()
max_date = valid_dates.max().date()

date_from = st.sidebar.date_input("С", min_date, format="DD.MM.YYYY")
date_to = st.sidebar.date_input("По", max_date, format="DD.MM.YYYY")

df["Канал"] = df["Канал"].fillna("").astype(str).str.strip()
channel_options = ["Все"] + sorted(df["Канал"].unique().tolist())
selected_channel = st.sidebar.selectbox("Канал", channel_options)

mode = st.radio("Режим", ["Сводка", "Аналитика"], horizontal=True)


# ===== ПРИМЕНЕНИЕ ФИЛЬТРОВ =====
if selected_channel != "Все":
    df = df[df["Канал"] == selected_channel].copy()

df = df[
    (df["Дата"].dt.date >= date_from) &
    (df["Дата"].dt.date <= date_to)
].copy()

if "Дата" in exp.columns:
    exp = exp[
        (exp["Дата"].dt.date >= date_from) &
        (exp["Дата"].dt.date <= date_to)
    ].copy()


# ===== РАСЧЕТЫ =====
df["Мой"] = 0.0
df.loc[df["Это Ariston"], "Мой"] = df["Прибыль"] / 2
df.loc[~df["Это Ariston"] & df["Плюс"], "Мой"] = df["Прибыль"] / 2

df["Алексей"] = 0.0
df.loc[df["Это Ariston"], "Алексей"] = df["Прибыль"] / 2
df.loc[~df["Это Ariston"] & df["Плюс"], "Алексей"] = df["Прибыль"] / 2
df.loc[~df["Это Ariston"] & ~df["Плюс"], "Алексей"] = df["Прибыль"]

total_profit = df["Прибыль"].sum()
my_income = df["Мой"].sum()
alex_income = df["Алексей"].sum()

expenses = exp["Сумма"].sum() if "Сумма" in exp.columns else 0.0
half_expenses = expenses / 2

my_net = my_income - half_expenses
alex_net = alex_income - half_expenses
total_net = my_net + alex_net

avg_check = df["РРЦ"].mean() if len(df) > 0 else 0
sales_count = len(df)
revenue_sum = df["РРЦ"].sum()
margin_percent = (total_profit / revenue_sum * 100) if revenue_sum > 0 else 0


def format_money(value):
    return f"{value:,.0f}".replace(",", " ")


# ===== ВЫВОД =====
if mode == "Сводка":
    st.metric("Общая прибыль", format_money(total_profit))
    st.metric("Мой заработок", format_money(my_income))
    st.metric("Алексей", format_money(alex_income))
    st.metric("Расходы", format_money(expenses))
    st.metric("Мой чистый", format_money(my_net))
    st.metric("Алексей чистый", format_money(alex_net))
    st.metric("Итого", format_money(total_net))

else:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Прибыль", format_money(total_profit))
    c2.metric("Мой", format_money(my_income))
    c3.metric("Алексей", format_money(alex_income))
    c4.metric("Расходы", format_money(expenses))

    st.subheader("Прибыль по дням")
    if not df.empty:
        daily = df.groupby("Дата_рус")["Прибыль"].sum()
        st.line_chart(daily)

    st.subheader("Топ товаров")
    if not df.empty:
        top = df.groupby("Наименование")["Прибыль"].sum().sort_values(ascending=False).head(5)
        st.bar_chart(top)

    st.subheader("Продажи")
    st.dataframe(df, use_container_width=True)

    st.subheader("Расходы")
    st.dataframe(exp, use_container_width=True)
