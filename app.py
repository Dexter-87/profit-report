import os
from pathlib import Path
from datetime import date

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Отчет по прибыли", layout="wide")

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

SALES_PATH = DATA_DIR / "sales.xlsx"
EXPENSES_PATH = DATA_DIR / "expenses.xlsx"


def save_uploaded_file(uploaded_file, target_path: Path) -> None:
    target_path.write_bytes(uploaded_file.getbuffer())


def load_sales_dataframe(path: Path) -> pd.DataFrame:
    df = pd.read_excel(path)
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


def load_expenses_dataframe(path: Path) -> pd.DataFrame:
    exp = pd.read_excel(path)
    exp.columns = exp.columns.astype(str).str.strip()

    if "Дата" in exp.columns:
        exp["Дата"] = pd.to_datetime(exp["Дата"], errors="coerce")
        exp["Дата_рус"] = exp["Дата"].dt.strftime("%d.%m.%Y")

    if "Сумма" in exp.columns:
        exp["Сумма"] = pd.to_numeric(exp["Сумма"], errors="coerce").fillna(0)
    else:
        exp["Сумма"] = 0.0

    return exp


def format_money(value: float) -> str:
    return f"{value:,.0f}".replace(",", " ")


st.title("Отчет по прибыли")

with st.sidebar:
    st.header("Файлы")

    sales_upload = st.file_uploader("Продажи", type=["xlsx"], key="sales_uploader")
    if sales_upload is not None:
        save_uploaded_file(sales_upload, SALES_PATH)
        st.success("Продажи сохранены")

    expenses_upload = st.file_uploader("Расходы", type=["xlsx"], key="expenses_uploader")
    if expenses_upload is not None:
        save_uploaded_file(expenses_upload, EXPENSES_PATH)
        st.success("Расходы сохранены")

    if SALES_PATH.exists():
        st.caption(f"Продажи: {SALES_PATH.name}")
    else:
        st.warning("Файл продаж ещё не загружен")

    if EXPENSES_PATH.exists():
        st.caption(f"Расходы: {EXPENSES_PATH.name}")
    else:
        st.info("Файл расходов пока не загружен")

    if st.button("Очистить сохраненные файлы"):
        if SALES_PATH.exists():
            SALES_PATH.unlink()
        if EXPENSES_PATH.exists():
            EXPENSES_PATH.unlink()
        st.rerun()

if not SALES_PATH.exists():
    st.info("Сначала загрузи файл продаж в левом меню.")
    st.stop()

df = load_sales_dataframe(SALES_PATH)
exp = load_expenses_dataframe(EXPENSES_PATH) if EXPENSES_PATH.exists() else None

st.sidebar.header("Фильтры")

valid_dates = df["Дата"].dropna()
if valid_dates.empty:
    st.error("В файле продаж не удалось распознать даты.")
    st.stop()

min_date = valid_dates.min().date()
max_date = valid_dates.max().date()

date_from = st.sidebar.date_input("С", min_date, format="DD.MM.YYYY")
date_to = st.sidebar.date_input("По", max_date, format="DD.MM.YYYY")

channel_options = ["Все"] + sorted(df["Канал"].dropna().astype(str).unique().tolist())
selected_channel = st.sidebar.selectbox("Канал", channel_options)

mode = st.radio("Режим", ["Сводка", "Аналитика"], horizontal=True)

# Фильтр по каналу
df["Канал"] = df["Канал"].fillna("").astype(str).str.strip()

if selected_channel != "Все":
    df = df[df["Канал"] == selected_channel].copy()

# Фильтрация продаж
df = df[
    (df["Дата"].dt.date >= date_from) &
    (df["Дата"].dt.date <= date_to)
].copy()

# Фильтрация расходов по тем же датам
if exp is not None and "Дата" in exp.columns:
    exp = exp[
        (exp["Дата"].dt.date >= date_from) &
        (exp["Дата"].dt.date <= date_to)
    ].copy()

# Расчеты
df["Мой"] = 0.0
df.loc[df["Это Ariston"], "Мой"] = df.loc[df["Это Ariston"], "Прибыль"] / 2
df.loc[~df["Это Ariston"] & df["Плюс"], "Мой"] = df.loc[
    ~df["Это Ariston"] & df["Плюс"], "Прибыль"
] / 2

df["Алексей"] = 0.0
df.loc[df["Это Ariston"], "Алексей"] = df.loc[df["Это Ariston"], "Прибыль"] / 2
df.loc[~df["Это Ariston"] & df["Плюс"], "Алексей"] = df.loc[
    ~df["Это Ariston"] & df["Плюс"], "Прибыль"
] / 2
df.loc[~df["Это Ariston"] & ~df["Плюс"], "Алексей"] = df.loc[
    ~df["Это Ariston"] & ~df["Плюс"], "Прибыль"
]

total_profit = df["Прибыль"].sum()
my_income = df["Мой"].sum()
alex_income = df["Алексей"].sum()

if len(df) == 0:
    expenses = 0.0
else:
    expenses = 0.0
    if exp is not None and "Сумма" in exp.columns:
        expenses = exp["Сумма"].sum()

half_expenses = expenses / 2

my_net = my_income - half_expenses
alex_net = alex_income - half_expenses
total_net = my_net + alex_net


avg_check = df["РРЦ"].mean() if len(df) > 0 else 0.0
sales_count = len(df)
revenue_sum = df["РРЦ"].sum()
margin_percent = (total_profit / revenue_sum * 100) if revenue_sum > 0 else 0.0

if mode == "Сводка":
    st.metric("Общая прибыль", format_money(total_profit))
    st.metric("Мой заработок", format_money(my_income))
    st.metric("Заработок Алексея", format_money(alex_income))
    st.metric("Расходы", format_money(expenses))
    st.metric("Половина расходов", format_money(half_expenses))
    st.metric("Мой чистый заработок", format_money(my_net))
    st.metric("Чистый заработок Алексея", format_money(alex_net))
    st.metric("Чистая прибыль", format_money(total_net))

    st.subheader("Коротко для отправки")
    st.code(
        "\n".join(
            [
                f"Период: {date_from.strftime('%d.%m.%Y')} - {date_to.strftime('%d.%m.%Y')}",
                f"Мой: {format_money(my_net)}",
                f"Алексей: {format_money(alex_net)}",
                f"Итого: {format_money(total_net)}",
            ]
        )
    )

else:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Общая прибыль", format_money(total_profit))
    c2.metric("Мой заработок", format_money(my_income))
    c3.metric("Алексей", format_money(alex_income))
    c4.metric("Расходы", format_money(expenses))

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Половина расходов", format_money(half_expenses))
    c6.metric("Мой чистый", format_money(my_net))
    c7.metric("Алексей чистый", format_money(alex_net))
    c8.metric("Итог", format_money(total_net))

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

    with st.expander("Проверка расчетов"):
        st.write(
            f"{format_money(my_income)} + {format_money(alex_income)} = {format_money(my_income + alex_income)}"
        )
        st.write(
            f"{format_money(my_income + alex_income)} - {format_money(expenses)} = {format_money(total_net)}"
        )

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

    if exp is not None:
        with st.expander("Расходы"):
            exp_cols = [col for col in ["Дата_рус", "Тип расхода", "Сумма"] if col in exp.columns]
            st.dataframe(exp[exp_cols], use_container_width=True)
