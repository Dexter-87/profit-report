import pandas as pd
import streamlit as st

st.set_page_config(page_title="Отчет по прибыли", layout="wide")

# ===== ССЫЛКИ НА GOOGLE TABLES =====
sales_url = "https://docs.google.com/spreadsheets/d/1D26s-VjLPvg43z-Hk38fU7Y4tPF/edit?output=csv"
expenses_url = "https://docs.google.com/spreadsheets/d/1AuxP3Qgk-zZ0V0ZChdwZ1/edit?output=csv"

st.title("Отчет по прибыли")


def format_money(value):
    try:
        return f"{float(value):,.0f}".replace(",", " ")
    except Exception:
        return "0"


@st.cache_data(ttl=60)
def load_data():
    sales_csv = sales_url.replace("/edit?output=csv", "/export?format=csv")
    expenses_csv = expenses_url.replace("/edit?output=csv", "/export?format=csv")

    sales = pd.read_csv(sales_csv)
    expenses = pd.read_csv(expenses_csv)
    return sales, expenses


def load_sales_dataframe(data: pd.DataFrame) -> pd.DataFrame:
    df = data.copy()
    df.columns = df.columns.astype(str).str.strip()

    if "Комментарий" not in df.columns:
        df["Комментарий"] = ""

    if "Канал" not in df.columns:
        df["Канал"] = ""

    if "Наименование" not in df.columns:
        df["Наименование"] = ""

    if "РРЦ" not in df.columns:
        df["РРЦ"] = 0

    if "Себестоимость" not in df.columns:
        df["Себестоимость"] = 0

    if "Комиссия Kaspi" not in df.columns:
        df["Комиссия Kaspi"] = 0

    df["Дата"] = pd.to_datetime(df["Дата"], errors="coerce", dayfirst=False)
    df["РРЦ"] = pd.to_numeric(df["РРЦ"], errors="coerce").fillna(0)
    df["Себестоимость"] = pd.to_numeric(df["Себестоимость"], errors="coerce").fillna(0)
    df["Комиссия Kaspi"] = pd.to_numeric(df["Комиссия Kaspi"], errors="coerce").fillna(0)

    if "Чистая прибыль" in df.columns:
        df["Прибыль"] = pd.to_numeric(df["Чистая прибыль"], errors="coerce").fillna(0)
    else:
        df["Прибыль"] = df["РРЦ"] - df["Себестоимость"] - df["Комиссия Kaspi"]

    df["Наименование"] = df["Наименование"].fillna("").astype(str).str.strip()
    df["Канал"] = df["Канал"].fillna("").astype(str).str.strip()
    df["Комментарий"] = df["Комментарий"].fillna("").astype(str).str.strip()

    df["Это Ariston"] = df["Наименование"].str.lower().str.contains("ariston", na=False)
    df["Плюс"] = df["Комментарий"] == "+"
    df["Дата_рус"] = df["Дата"].dt.strftime("%d.%m.%Y")

    return df


def load_expenses_dataframe(data: pd.DataFrame) -> pd.DataFrame:
    exp = data.copy()
    exp.columns = exp.columns.astype(str).str.strip()

    if "Дата" not in exp.columns:
        exp["Дата"] = pd.NaT
    if "Сумма" not in exp.columns:
        exp["Сумма"] = 0
    if "Тип расхода" not in exp.columns:
        exp["Тип расхода"] = ""

    exp["Дата"] = pd.to_datetime(exp["Дата"], errors="coerce", dayfirst=False)
    exp["Сумма"] = pd.to_numeric(exp["Сумма"], errors="coerce").fillna(0)
    exp["Дата_рус"] = exp["Дата"].dt.strftime("%d.%m.%Y")

    return exp


left, right = st.columns([1, 1])

with left:
    if st.button("Обновить данные"):
        st.cache_data.clear()
        st.rerun()

with right:
    st.caption("Кэш обновляется примерно раз в 60 секунд")

sales_df, expenses_df = load_data()
df = load_sales_dataframe(sales_df)
exp = load_expenses_dataframe(expenses_df)

valid_dates = df["Дата"].dropna()
if valid_dates.empty:
    st.error("В таблице продаж не распознаны даты.")
    st.stop()

st.sidebar.header("Фильтры")

min_date = valid_dates.min().date()
max_date = valid_dates.max().date()

date_from = st.sidebar.date_input("С", min_date, format="DD.MM.YYYY")
date_to = st.sidebar.date_input("По", max_date, format="DD.MM.YYYY")

channel_options = ["Все"] + sorted(
    [x for x in df["Канал"].dropna().unique().tolist() if str(x).strip() != ""]
)
selected_channel = st.sidebar.selectbox("Канал", channel_options)

mode = st.radio("Режим", ["Сводка", "Аналитика"], horizontal=True)

if selected_channel != "Все":
    df = df[df["Канал"] == selected_channel].copy()

df = df[
    (df["Дата"].dt.date >= date_from) &
    (df["Дата"].dt.date <= date_to)
].copy()

exp = exp[
    (exp["Дата"].dt.date >= date_from) &
    (exp["Дата"].dt.date <= date_to)
].copy()

df["Мой"] = 0.0
df.loc[df["Это Ariston"], "Мой"] = df.loc[df["Это Ariston"], "Прибыль"] / 2
df.loc[~df["Это Ariston"] & df["Плюс"], "Мой"] = (
    df.loc[~df["Это Ariston"] & df["Плюс"], "Прибыль"] / 2
)

df["Алексей"] = 0.0
df.loc[df["Это Ariston"], "Алексей"] = df.loc[df["Это Ariston"], "Прибыль"] / 2
df.loc[~df["Это Ariston"] & df["Плюс"], "Алексей"] = (
    df.loc[~df["Это Ariston"] & df["Плюс"], "Прибыль"] / 2
)
df.loc[~df["Это Ariston"] & ~df["Плюс"], "Алексей"] = (
    df.loc[~df["Это Ariston"] & ~df["Плюс"], "Прибыль"]
)

total_profit = df["Прибыль"].sum()
my_income = df["Мой"].sum()
alex_income = df["Алексей"].sum()

expenses = exp["Сумма"].sum() if "Сумма" in exp.columns else 0
half_expenses = expenses / 2

my_net = my_income - half_expenses
alex_net = alex_income - half_expenses
total_net = my_net + alex_net

avg_check = df["РРЦ"].mean() if len(df) > 0 else 0
sales_count = len(df)
revenue_sum = df["РРЦ"].sum()
margin_percent = (total_profit / revenue_sum * 100) if revenue_sum > 0 else 0

quick_report = "\n".join([
    f"Период: {date_from.strftime('%d.%m.%Y')} - {date_to.strftime('%d.%m.%Y')}",
    f"Канал: {selected_channel}",
    f"Мой чистый: {format_money(my_net)}",
    f"Алексей чистый: {format_money(alex_net)}",
    f"Итого: {format_money(total_net)}",
])

if mode == "Сводка":
    st.metric("Общая прибыль", format_money(total_profit))
    st.metric("Мой заработок", format_money(my_income))
    st.metric("Алексей", format_money(alex_income))
    st.metric("Расходы", format_money(expenses))
    st.metric("Мой чистый", format_money(my_net))
    st.metric("Алексей чистый", format_money(alex_net))
    st.metric("Итого", format_money(total_net))

    st.subheader("Быстрый отчет")
    st.code(quick_report)

else:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Прибыль", format_money(total_profit))
    c2.metric("Мой", format_money(my_income))
    c3.metric("Алексей", format_money(alex_income))
    c4.metric("Расходы", format_money(expenses))

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Половина расходов", format_money(half_expenses))
    c6.metric("Мой чистый", format_money(my_net))
    c7.metric("Алексей чистый", format_money(alex_net))
    c8.metric("Итого", format_money(total_net))

    c9, c10, c11, c12 = st.columns(4)
    c9.metric("Средний чек", format_money(avg_check))
    c10.metric("Количество продаж", format_money(sales_count))
    c11.metric("Выручка", format_money(revenue_sum))
    c12.metric("Маржа %", f"{margin_percent:.2f}%")

    st.subheader("Прибыль по дням")
    if not df.empty:
        daily = df.groupby("Дата_рус")["Прибыль"].sum()
        st.line_chart(daily)

    st.subheader("Топ-5 товаров по прибыли")
    if not df.empty:
        top_products = (
            df.groupby("Наименование")["Прибыль"]
            .sum()
            .sort_values(ascending=False)
            .head(5)
        )
        st.bar_chart(top_products)

    with st.expander("Быстрый отчет"):
        st.code(quick_report)

    with st.expander("Продажи"):
        show_cols = [
            "Дата_рус",
            "Канал",
            "Наименование",
            "Комментарий",
            "Прибыль",
            "Это Ariston",
            "Плюс",
            "Мой",
            "Алексей",
        ]
        show_cols = [col for col in show_cols if col in df.columns]
        st.dataframe(df[show_cols], use_container_width=True)

    with st.expander("Расходы"):
        exp_cols = [col for col in ["Дата_рус", "Тип расхода", "Сумма"] if col in exp.columns]
        st.dataframe(exp[exp_cols], use_container_width=True)
