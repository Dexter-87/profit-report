import pandas as pd
import streamlit as st

st.set_page_config(page_title="Отчет по прибыли", layout="wide")

sales_url = "https://docs.google.com/spreadsheets/d/1D26s-VjLPvg43z-Hk38fU7Y4tPF79h-UlFjlzQnvtB0/gviz/tq?tqx=out:csv&gid=1240951053"
expenses_url = "https://docs.google.com/spreadsheets/d/ID_РАСХОДОВ/gviz/tq?tqx=out:csv&gid=GID_ЛИСТА"

st.title("Отчет по прибыли")


def format_money(value):
    try:
        return f"{float(value):,.0f}".replace(",", " ")
    except Exception:
        return "0"


@st.cache_data(ttl=60)
def load_data():
    sales = pd.read_csv(sales_url)
    expenses = pd.read_csv(expenses_url)
    return sales, expenses


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = (
        df.columns.astype(str)
        .str.replace("\ufeff", "", regex=False)
        .str.replace("\xa0", " ", regex=False)
        .str.strip()
    )
    return df


def find_column(df: pd.DataFrame, variants: list[str]) -> str | None:
    lower_map = {str(col).strip().lower(): col for col in df.columns}
    for variant in variants:
        found = lower_map.get(variant.lower())
        if found is not None:
            return found
    return None


def load_sales_dataframe(data: pd.DataFrame) -> pd.DataFrame:
    df = normalize_columns(data)

    date_col = find_column(df, ["Дата", "дата"])
    channel_col = find_column(df, ["Канал", "канал"])
    name_col = find_column(df, ["Наименование", "наименование"])
    comment_col = find_column(df, ["Комментарий", "комментарий"])
    rrc_col = find_column(df, ["РРЦ", "ррц"])
    cost_col = find_column(df, ["Себестоимость", "себестоимость"])
    kaspi_col = find_column(df, ["Комиссия Kaspi", "комиссия kaspi", "Kaspi", "kaspi"])
    profit_col = find_column(df, ["Чистая прибыль", "чистая прибыль"])

    if date_col is None:
        st.error("В таблице продаж не найден столбец 'Дата'.")
        st.write("Найденные столбцы:", list(df.columns))
        st.stop()

    if channel_col is None:
        df["Канал"] = ""
        channel_col = "Канал"

    if name_col is None:
        df["Наименование"] = ""
        name_col = "Наименование"

    if comment_col is None:
        df["Комментарий"] = ""
        comment_col = "Комментарий"

    if rrc_col is None:
        df["РРЦ"] = 0
        rrc_col = "РРЦ"

    if cost_col is None:
        df["Себестоимость"] = 0
        cost_col = "Себестоимость"

    if kaspi_col is None:
        df["Комиссия Kaspi"] = 0
        kaspi_col = "Комиссия Kaspi"

    df["Дата"] = pd.to_datetime(df[date_col], errors="coerce", dayfirst=False)
    df["Канал"] = df[channel_col].fillna("").astype(str).str.strip()
    df["Наименование"] = df[name_col].fillna("").astype(str).str.strip()
    df["Комментарий"] = df[comment_col].fillna("").astype(str).str.strip()

    df["РРЦ"] = pd.to_numeric(df[rrc_col], errors="coerce").fillna(0)
    df["Себестоимость"] = pd.to_numeric(df[cost_col], errors="coerce").fillna(0)
    df["Комиссия Kaspi"] = pd.to_numeric(df[kaspi_col], errors="coerce").fillna(0)

    if profit_col is not None:
        df["Прибыль"] = pd.to_numeric(df[profit_col], errors="coerce").fillna(0)
    else:
        df["Прибыль"] = df["РРЦ"] - df["Себестоимость"] - df["Комиссия Kaspi"]

    df["Это Ariston"] = df["Наименование"].str.lower().str.contains("ariston", na=False)
    if "Комментарий" in df.colums:
        df["Плюс"] = df["Комментарий"] == "+"
    else:
        df["Плюс"] = False
    df["Дата_рус"] = df["Дата"].dt.strftime("%d.%m.%Y")

    return df


def load_expenses_dataframe(data: pd.DataFrame) -> pd.DataFrame:
    exp = normalize_columns(data)

    date_col = find_column(exp, ["Дата", "дата"])
    sum_col = find_column(exp, ["Сумма", "сумма"])
    type_col = find_column(exp, ["Тип расхода", "тип расхода"])

    if date_col is None:
        exp["Дата"] = pd.NaT
    else:
        exp["Дата"] = pd.to_datetime(exp[date_col], errors="coerce", dayfirst=False)

    if sum_col is None:
        exp["Сумма"] = 0
    else:
        exp["Сумма"] = pd.to_numeric(exp[sum_col], errors="coerce").fillna(0)

    if type_col is None:
        exp["Тип расхода"] = ""
    else:
        exp["Тип расхода"] = exp[type_col].fillna("").astype(str)

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
    st.error("В продажах не распознаны даты.")
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

    with st.expander("Продажи"):
        show_cols = [c for c in ["Дата_рус", "Канал", "Наименование", "Комментарий", "Прибыль", "Мой", "Алексей"] if c in df.columns]
        st.dataframe(df[show_cols], use_container_width=True)

    with st.expander("Расходы"):
        exp_cols = [c for c in ["Дата_рус", "Тип расхода", "Сумма"] if c in exp.columns]
        st.dataframe(exp[exp_cols], use_container_width=True)
