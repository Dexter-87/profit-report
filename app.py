import pandas as pd
import streamlit as st
import altair as st

st.set_page_config(page_title="Отчет по прибыли", layout="wide")

st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

.stApp {
    background-color: #0f1115;
    color: #f3f4f6;
}

.block-container {
    padding-top: 1.2rem;
    padding-bottom: 1rem;
    padding-left: 1.5rem;
    padding-right: 1.5rem;
    max-width: 1600px;
}

h1, h2, h3 {
    color: #f9fafb;
    letter-spacing: 0.2px;
}

.main-title {
    font-size: 42px;
    font-weight: 800;
    color: #f9fafb;
    margin-top: 8px;
    margin-bottom: 6px;
    line-height: 1.05;
}

@media (max-width: 768px) {
    .main-title {
        font-size: 28px;
        margin-top: 18px;
        line-height: 1.1;
    }

    .sub-title {
        font-size: 13px;
        margin-bottom: 14px;
    }

    .block-container {
        padding-top: 2.8rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
}


.sub-title {
    font-size: 14px;
    color: #9ca3af;
    margin-bottom: 20px;
}

.metric-card {
    background: #171a21;
    border: 1px solid #2a2f3a;
    border-radius: 18px;
    padding: 18px 20px;
    box-shadow: 0 6px 20px rgba(0,0,0,0.18);
    transition: 0.2s ease;
}

.metric-title {
    font-size: 13px;
    color: #9ca3af;
    margin-bottom: 10px;
}

.metric-value {
    font-size: 30px;
    font-weight: 800;
    color: #f9fafb;
    line-height: 1.1;
}

.metric-green {
    color: #22c55e;
}

.metric-red {
    color: #ef4444;
}

.section-card {
    background: #171a21;
    border: 1px solid #2a2f3a;
    border-radius: 18px;
    padding: 18px 18px 10px 18px;
    margin-top: 14px;
    box-shadow: 0 6px 20px rgba(0,0,0,0.18);
}

.section-title {
    font-size: 18px;
    font-weight: 700;
    color: #f9fafb;
    margin-bottom: 12px;
}

div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div,
div[data-testid="stDateInput"] > div,
div[data-testid="stNumberInput"] > div {
    background-color: #11151b !important;
    border: 1px solid #2a2f3a !important;
    border-radius: 12px !important;
    color: #f3f4f6 !important;
}

div[data-testid="stMetric"] {
    background-color: #171a21;
    border: 1px solid #2a2f3a;
    padding: 16px;
    border-radius: 16px;
}

hr {
    border: none;
    height: 1px;
    background: #2a2f3a;
    margin: 16px 0;
}

.stButton > button {
    background-color: #171a21;
    color: #f3f4f6;
    border: 1px solid #2a2f3a;
    border-radius: 12px;
    padding: 10px 18px;
    font-weight: 600;
}

.stButton > button:hover {
    border-color: #3b82f6;
    color: #ffffff;
}

.metric-big {
    font-size: 34px;
    font-weight: 800;
    color: #f9fafb;
}

.metric-profit {
    color: #22c55e;
}

.metric-expense {
    color: #ef4444;
}

.metric-muted {
    color: #9ca3af;
}

</style>
""", unsafe_allow_html=True)


sales_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTVCDzAu1DphzNCs2AzlpsjgJyRfzYWEAicdYbqMEFCcjjcxo4WyjVkcKa2-6G2BDyhM2GaBRx23DvO/pub?gid=1240951053&single=true&output=csv"
expenses_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSYEdrQn9FbW5xYzz_UuvUvOUYxbENvC1JnSE4z00YUTvtCxtnP4sU54J-Vs_40kEcuyQLRm-Ae6B_0/pub?gid=1622934317&single=true&output=csv"


def format_money(value: float) -> str:
    try:
        return f"{float(value):,.0f}".replace(",", " ")
    except Exception:
        return "0"


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


def parse_mixed_dates(series: pd.Series) -> pd.Series:
    s = series.astype(str).str.strip()

    # 1) сначала пробуем день.месяц.год
    parsed_dayfirst = pd.to_datetime(s, errors="coerce", dayfirst=True)

    # 2) всё, что не распарсилось — пробуем месяц/день/год
    missing = parsed_dayfirst.isna()
    if missing.any():
        parsed_monthfirst = pd.to_datetime(s[missing], errors="coerce", dayfirst=False)
        parsed_dayfirst.loc[missing] = parsed_monthfirst

    # 3) отбрасываем явно бредовые даты
    parsed_dayfirst = parsed_dayfirst.where(
        (parsed_dayfirst >= pd.Timestamp("2020-01-01")) &
        (parsed_dayfirst <= pd.Timestamp("2030-12-31"))
    )

    return parsed_dayfirst


@st.cache_data(ttl=60)
def load_data():
    sales_df = pd.read_csv(sales_url)
    expenses_df = pd.read_csv(expenses_url)

    sales_df = normalize_columns(sales_df)
    expenses_df = normalize_columns(expenses_df)

    return sales_df, expenses_df


def load_sales_dataframe(data: pd.DataFrame) -> pd.DataFrame:
    df = normalize_columns(data)

    date_col = find_column(df, ["Дата", "дата"])
    channel_col = find_column(df, ["Канал", "канал"])
    name_col = find_column(df, ["Наименование", "наименование"])
    order_col = find_column(df, ["Номер заказа", "номер заказа"])
    cost_col = find_column(df, ["Себестоимость", "себестоимость"])
    rrc_col = find_column(df, ["РРЦ", "ррц"])
    kaspi_col = find_column(df, ["Комиссия Kaspi", "комиссия kaspi"])
    profit_col = find_column(df, ["Чистая прибыль", "чистая прибыль"])
    comment_col = find_column(df, ["Комментарий", "комментарий", "Комментарии"])

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

    if order_col is None:
        df["Номер заказа"] = ""
        order_col = "Номер заказа"

    if cost_col is None:
        df["Себестоимость"] = 0
        cost_col = "Себестоимость"

    if rrc_col is None:
        df["РРЦ"] = 0
        rrc_col = "РРЦ"

    if kaspi_col is None:
        df["Комиссия Kaspi"] = 0
        kaspi_col = "Комиссия Kaspi"

    if comment_col is None:
        df["Комментарий"] = ""
        comment_col = "Комментарий"

    df["Дата"] = parse_mixed_dates(df[date_col])
    df["Канал"] = df[channel_col].fillna("").astype(str).str.strip()
    df["Наименование"] = df[name_col].fillna("").astype(str).str.strip()
    df["Номер заказа"] = df[order_col].fillna("").astype(str).str.strip()

    df["Себестоимость"] = pd.to_numeric(df[cost_col], errors="coerce").fillna(0)
    df["РРЦ"] = pd.to_numeric(df[rrc_col], errors="coerce").fillna(0)
    df["Комиссия Kaspi"] = pd.to_numeric(df[kaspi_col], errors="coerce").fillna(0)

    df["Комментарий"] = df[comment_col].fillna("").astype(str)
    df["Комментарий"] = df["Комментарий"].str.replace("\xa0", "", regex=False)
    df["Комментарий"] = df["Комментарий"].str.replace(" ", "", regex=False)
    df["Комментарий"] = df["Комментарий"].str.strip()

    if profit_col is not None:
        df["Прибыль"] = pd.to_numeric(df[profit_col], errors="coerce").fillna(0)
    else:
        df["Прибыль"] = df["РРЦ"] - df["Себестоимость"] - df["Комиссия Kaspi"]

    df["Это Ariston"] = df["Наименование"].str.lower().str.contains("ariston", na=False)
    df["Плюс"] = df["Комментарий"] == "+"
    df["Дата_рус"] = df["Дата"].dt.strftime("%d.%m.%Y")

    return df


def load_expenses_dataframe(data: pd.DataFrame) -> pd.DataFrame:
    exp = normalize_columns(data)

    date_col = find_column(exp, ["Дата", "дата"])
    type_col = find_column(exp, ["Тип расхода", "тип расхода"])
    sum_col = find_column(exp, ["Сумма", "сумма"])

    if date_col is None:
        exp["Дата"] = pd.NaT
    else:
        exp["Дата"] = parse_mixed_dates(exp[date_col])

    if type_col is None:
        exp["Тип расхода"] = ""
    else:
        exp["Тип расхода"] = exp[type_col].fillna("").astype(str).str.strip()

    if sum_col is None:
        exp["Сумма"] = 0
    else:
        exp["Сумма"] = pd.to_numeric(exp[sum_col], errors="coerce").fillna(0)

    exp["Дата_рус"] = exp["Дата"].dt.strftime("%d.%m.%Y")
    return exp


st.markdown('<div class="main-title">Финансовая сводка</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Продажи • Прибыль • Рентабельность</div>', unsafe_allow_html=True)


top_left, top_right = st.columns([1, 1])

with top_left:
    if st.button("Обновить данные"):
        st.cache_data.clear()
        st.rerun()

with top_right:
    st.caption("Кэш обновляется примерно раз в 60 секунд")

sales_raw, expenses_raw = load_data()
df = load_sales_dataframe(sales_raw)
exp = load_expenses_dataframe(expenses_raw)

valid_dates = df["Дата"].dropna()
if valid_dates.empty:
    st.error("В продажах не распознаны даты.")
    st.stop()

st.sidebar.header("Фильтры")

min_date = valid_dates.min().date()
max_date = valid_dates.max().date()

date_from = st.sidebar.date_input("С", value=min_date, min_value=min_date, max_value=max_date, format="DD.MM.YYYY")
date_to = st.sidebar.date_input("По", value=max_date, min_value=min_date, max_value=max_date, format="DD.MM.YYYY")

if date_from > date_to:
    st.sidebar.error("Дата 'С' не может быть позже даты 'По'")
    st.stop()

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

if "Дата" in exp.columns:
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
    st.markdown(f"""
<div class="metric-card">
    <div class="metric-title">Чистая прибыль</div>
    <div class="metric-value metric-profit">{format_money(total_net)} ₸</div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="metric-card">
    <div class="metric-title">Мой заработок</div>
    <div class="metric-value">{format_money(my_net)} ₸</div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="metric-card">
    <div class="metric-title">Алексей</div>
    <div class="metric-value">{format_money(alex_net)} ₸</div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="metric-card">
    <div class="metric-title">Расходы</div>
    <div class="metric-value metric-expense">{format_money(expenses)} ₸</div>
</div>
""", unsafe_allow_html=True)

st.subheader("Прибыль по дням")
if not df.empty:
        daily = df.groupby("Дата_рус")["Прибыль"].sum()
        chart = alt.Chart(daily.reset_index()).mark_line().encode(
    x="Дата_рус",
    y="Прибыль"
).configure_axis(
    labelColor="white",
    titleColor="white"
)

st.altair_chart(chart, use_container_width=True)



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
            "Номер заказа",
            "Себестоимость",
            "РРЦ",
            "Комиссия Kaspi",
            "Прибыль",
            "Комментарий",
            "Мой",
            "Алексей",
        ]
        show_cols = [col for col in show_cols if col in df.columns]
        st.dataframe(df[show_cols], use_container_width=True)

with st.expander("Расходы"):
        exp_cols = [col for col in ["Дата_рус", "Тип расхода", "Сумма"] if col in exp.columns]
        st.dataframe(exp[exp_cols], use_container_width=True)
