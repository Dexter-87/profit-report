import pandas as pd
import streamlit as st
from matplotlib import pyplot as plt
import io
import plotly.express as px
st.set_page_config(page_title="Финансовая сводка", layout="wide")
page = st.sidebar.selectbox(
    "Раздел",
    ["Финансовая сводка", "Создать заказ"]
)
@st.cache_data(ttl=60)
def load_price_from_google(file_id: str) -> pd.DataFrame:
    url = f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=xlsx"
    df = pd.read_excel(url)
    df.columns = df.columns.astype(str).str.strip()
    return df

if page == "Создать заказ":
    st.title("Создать заказ")
    st.caption("Выбор прайса, модели, количества и расчёт суммы")

    Teeg_FILE_ID = "1a4rIkdUUNjdO21CmKNb71FctyTdr2JMq"
    ARISTON_FILE_ID = "1M2RAZDDdYwPDr92o2E27em3-PDqD4JnR"

    price_source = st.selectbox(
        "Прайс",
        ["Teeg", "Ariston"]
    )

    if price_source == "Teeg":
        price_df = load_price_from_google(Teeg_FILE_ID)
        

        required_columns = ["Модель", "Цена_0", "Цена_1", "Цена_2", "Цена_3", "Цена_4"]
        missing_columns = [col for col in required_columns if col not in price_df.columns]

        if missing_columns:
            st.error(f"В Teeg-прайсе не хватает колонок: {', '.join(missing_columns)}")
            st.stop()

        price_df["Модель"] = price_df["Модель"].fillna("").astype(str).str.strip()
        price_df = price_df[price_df["Модель"] != ""].copy()

        for col in ["Цена_0", "Цена_1", "Цена_2", "Цена_3", "Цена_4"]:
            price_df[col] = pd.to_numeric(price_df[col], errors="coerce").fillna(0)

        model = st.selectbox("Модель", price_df["Модель"].tolist())

        price_type = st.selectbox(
            "Тип цены",
            ["Цена_0", "Цена_1", "Цена_2", "Цена_3", "Цена_4"]
        )

        qty = st.number_input("Количество", min_value=1, value=1, step=1)

        selected_row = price_df[price_df["Модель"] == model].iloc[0]
        price = float(selected_row[price_type])
        total = price * qty

        c1, c2 = st.columns(2)
        c1.metric("Цена", f"{price:,.0f}".replace(",", " "))
        c2.metric("Сумма", f"{total:,.0f}".replace(",", " "))

        with st.expander("Показать все цены по модели"):
            st.write({
                "Цена_0": f"{selected_row['Цена_0']:,.0f}".replace(",", " "),
                "Цена_1": f"{selected_row['Цена_1']:,.0f}".replace(",", " "),
                "Цена_2": f"{selected_row['Цена_2']:,.0f}".replace(",", " "),
                "Цена_3": f"{selected_row['Цена_3']:,.0f}".replace(",", " "),
                "Цена_4": f"{selected_row['Цена_4']:,.0f}".replace(",", " "),
            })

    else:
        price_df = load_price_from_google(ARISTON_FILE_ID)

        required_columns = ["Модель", "Цена_1"]
        missing_columns = [col for col in required_columns if col not in price_df.columns]

        if missing_columns:
            st.error(f"В Ariston-прайсе не хватает колонок: {', '.join(missing_columns)}")
            st.stop()

        price_df["Модель"] = price_df["Модель"].fillna("").astype(str).str.strip()
        price_df = price_df[price_df["Модель"] != ""].copy()
        price_df["Цена_1"] = pd.to_numeric(price_df["Цена_1"], errors="coerce").fillna(0)

        model = st.selectbox("Модель", price_df["Модель"].tolist())
        qty = st.number_input("Количество", min_value=1, value=1, step=1)

        selected_row = price_df[price_df["Модель"] == model].iloc[0]
        price = float(selected_row["Цена_1"])
        total = price * qty

        c1, c2 = st.columns(2)
        c1.metric("Цена", f"{price:,.0f}".replace(",", " "))
        c2.metric("Сумма", f"{total:,.0f}".replace(",", " "))

    st.stop()


# =========================
# СТИЛИ
# =========================
st.markdown("""
<style>
.stApp {
    background: #151922;
    color: #f3f4f6;
}

.block-container {
    padding-top: calc(2.8rem + env(safe-area-inset-top));
    padding-bottom: 2rem;
    max-width: 1400px;
}


a.anchor-link {
    display: none !important;
}

h1, h2, h3 {
    color: #f9fafb;
    letter-spacing: 0.2px;
}

.main-title {
    font-size: 40px;
    font-weight: 800;
    color: #f9fafb;
    margin-top: 0;
    margin-bottom: 6px;
    line-height: 1.05;
}


.sub-title {
    font-size: 16px;
    color: #aab2bf;
    margin-bottom: 18px;
}

.section-box {
    background: #1d2330;
    border: 1px solid #2f3747;
    border-radius: 18px;
    padding: 14px 16px;
    margin-bottom: 14px;
    box-shadow: 0 6px 20px rgba(0,0,0,0.18);
}

.card {
    background: #1d2330;
    border: 1px solid #2f3747;
    border-radius: 20px;
    padding: 18px 18px;
    margin-bottom: 14px;
    box-shadow: 0 6px 20px rgba(0,0,0,0.18);
}

.card-title {
    font-size: 13px;
    color: #aab2bf;
    margin-bottom: 10px;
}

.card-value {
    font-size: 30px;
    font-weight: 800;
    color: #f8fafc;
    line-height: 1.1;
}

.value-green {
    color: #34d399;
}

.value-red {
    color: #f87171;
}

.value-blue {
    color: #60a5fa;
}

.small-label {
    font-size: 20px;
    font-weight: 700;
    margin-bottom: 8px;
    color: #f9fafb;
}

hr {
    border: none;
    height: 1px;
    background: #2f3747;
    margin: 14px 0;
}

/* Кнопка */
.stButton > button {
    background: #1d2330 !important;
    color: #f3f4f6 !important;
    border: 1px solid #2f3747 !important;
    border-radius: 14px !important;
    font-weight: 600 !important;
    padding: 10px 18px !important;
}

.stButton > button:hover {
    border-color: #4b5568 !important;
    color: #ffffff !important;
}

/* Поля date_input/selectbox */
div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div,
div[data-testid="stDateInput"] > div,
div[data-testid="stSelectbox"] > div {
    background: #1d2330 !important;
    border: 1px solid #2f3747 !important;
    border-radius: 14px !important;
    color: #f3f4f6 !important;
}

div[data-baseweb="input"] input,
div[data-testid="stDateInput"] input {
    color: #f3f4f6 !important;
    -webkit-text-fill-color: #f3f4f6 !important;
}

div[data-baseweb="select"] span {
    color: #f3f4f6 !important;
}

/* Выпадающий список */
div[data-baseweb="popover"] {
    background: #1d2330 !important;
    border-radius: 12px !important;
}

ul[role="listbox"] {
    background: #1d2330 !important;
    color: #f3f4f6 !important;
    border: 1px solid #2f3747 !important;
}

ul[role="listbox"] li {
    color: #f3f4f6 !important;
    background: #1d2330 !important;
}

ul[role="listbox"] li:hover {
    background: #263042 !important;
}

/* EXPANDER */
div[data-testid="stExpander"] details {
    background: #1d2330 !important;
    border: 1px solid #2f3747 !important;
    border-radius: 18px !important;
    overflow: hidden !important;
}

div[data-testid="stExpander"] details summary {
    background: #1d2330 !important;
    color: #f3f4f6 !important;
    border: none !important;
    box-shadow: none !important;
    padding: 14px 18px !important;
}

div[data-testid="stExpander"] details[open] summary {
    background: #1d2330 !important;
    color: #f3f4f6 !important;
    border-bottom: 1px solid #2f3747 !important;
}

div[data-testid="stExpander"] details summary:hover {
    background: #1d2330 !important;
    color: #ffffff !important;
}

div[data-testid="stExpander"] details summary span {
    color: #f3f4f6 !important;
}

div[data-testid="stExpander"] > div {
    background: transparent !important;
}

div[data-testid="stExpander"] details summary svg {
    fill: #9ca3af !important;
    color: #9ca3af !important;
}

@media (max-width: 768px) {
    .block-container {
        padding-top: calc(4.2rem + env(safe-area-inset-top));
    }

    .main-title {
        font-size: 28px;
        margin-top: 0;
    }

    .sub-title {
        font-size: 14px;
        margin-bottom: 14px;
    }

    .card-value {
        font-size: 26px;
    }
}

div[data-testid="stDateInput"] input {
    caret-color: transparent !important;
}


</style>
""", unsafe_allow_html=True)

# =========================
# URL
# =========================
SALES_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTVCDzAu1DphzNCs2AzlpsjgJyRfzYWEAicdYbqMEFCcjjcxo4WyjVkcKa2-6G2BDyhM2GaBRx23DvO/pub?gid=1240951053&single=true&output=csv"
EXPENSES_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSYEdrQn9FbW5xYzz_UuvUvOUYxbENvC1JnSE4z00YUTvtCxtnP4sU54J-Vs_40kEcuyQLRm-Ae6B_0/pub?gid=1622934317&single=true&output=csv"

# =========================
# ВСПОМОГАТЕЛЬНОЕ
# =========================
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

    parsed_dayfirst = pd.to_datetime(s, errors="coerce", dayfirst=True)

    missing = parsed_dayfirst.isna()
    if missing.any():
        parsed_monthfirst = pd.to_datetime(s[missing], errors="coerce", dayfirst=False)
        parsed_dayfirst.loc[missing] = parsed_monthfirst

    parsed_dayfirst = parsed_dayfirst.where(
        (parsed_dayfirst >= pd.Timestamp("2020-01-01")) &
        (parsed_dayfirst <= pd.Timestamp("2030-12-31"))
    )
    return parsed_dayfirst

@st.cache_data(ttl=60)
def load_data():
    sales_df = pd.read_csv(SALES_URL)
    expenses_df = pd.read_csv(EXPENSES_URL)
    return normalize_columns(sales_df), normalize_columns(expenses_df)

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
    comment_col = find_column(df, ["Комментарий", "комментарий", "Комментарии", "комментарии"])
    kaspiy_marker_col = find_column(df, ["Каспий", "каспий"])

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

    if kaspiy_marker_col is None:
        df["Каспий"] = 0
        kaspiy_marker_col = "Каспий"

    df["Дата"] = parse_mixed_dates(df[date_col])
    df["Канал"] = df[channel_col].fillna("").astype(str).str.strip()
    df["Наименование"] = df[name_col].fillna("").astype(str).str.strip()
    df["Номер заказа"] = df[order_col].fillna("").astype(str).str.strip()
    df["Себестоимость"] = pd.to_numeric(df[cost_col], errors="coerce").fillna(0)
    df["РРЦ"] = pd.to_numeric(df[rrc_col], errors="coerce").fillna(0)
    df["Комиссия Kaspi"] = pd.to_numeric(df[kaspi_col], errors="coerce").fillna(0)

    df["Комментарий"] = df[comment_col].fillna("").astype(str)
    df["Комментарий"] = df["Комментарий"].str.replace("\xa0", "", regex=False)
    df["Комментарий"] = df["Комментарий"].str.strip()

    df["Каспий_маркер"] = pd.to_numeric(df[kaspiy_marker_col], errors="coerce").fillna(0)

    # Автоопределение канала, если колонка пустая
    if df["Канал"].eq("").all():
        kaspi_mask = pd.Series(False, index=df.index)

        if "Комиссия Kaspi" in df.columns:
            kaspi_mask = kaspi_mask | (
                pd.to_numeric(df["Комиссия Kaspi"], errors="coerce").fillna(0) > 0
            )

        if "Номер заказа" in df.columns:
            kaspi_mask = kaspi_mask | (
                df["Номер заказа"].fillna("").astype(str).str.strip() != ""
            )

        if "Каспий_маркер" in df.columns:
            kaspi_mask = kaspi_mask | (
                pd.to_numeric(df["Каспий_маркер"], errors="coerce").fillna(0) > 0
            )

        df.loc[kaspi_mask, "Канал"] = "Каспий"
        df.loc[~kaspi_mask, "Канал"] = "ОПТ"

    if profit_col is not None:
        df["Прибыль"] = pd.to_numeric(df[profit_col], errors="coerce").fillna(0)
    else:
        df["Прибыль"] = df["РРЦ"] - df["Себестоимость"] - df["Комиссия Kaspi"]

    df["Маржа %"] = (
        (df["Прибыль"] / df["РРЦ"] * 100)
        .replace([float("inf"), -float("inf")], 0)
        .fillna(0)
    )

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

# =========================
# ЗАГРУЗКА
# =========================
sales_raw, expenses_raw = load_data()
df = load_sales_dataframe(sales_raw)
exp = load_expenses_dataframe(expenses_raw)

valid_dates = df["Дата"].dropna()
if valid_dates.empty:
    st.error("В продажах не распознаны даты.")
    st.stop()

# =========================
# ШАПКА
# =========================
st.markdown('<div class="main-title">Финансовая сводка</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Продажи • Прибыль • Рентабельность</div>', unsafe_allow_html=True)

if st.button("Обновить данные"):
    st.cache_data.clear()
    st.rerun()

st.caption("Кэш обновляется примерно раз в 60 секунд")

# =========================
# ФИЛЬТРЫ
# =========================
st.markdown('<div class="small-label">Фильтры</div>', unsafe_allow_html=True)

min_date = valid_dates.min().date()
max_date = valid_dates.max().date()

channel_values = sorted([
    str(x).strip()
    for x in df["Канал"].dropna().unique().tolist()
    if str(x).strip() != ""
])
channel_options = ["Все"] + channel_values

f1, f2 = st.columns(2)

with f1:
    date_from = st.date_input(
        "С",
        value=min_date,
        min_value=min_date,
        max_value=max_date,
        format="DD.MM.YYYY",
        key="date_from_main"
    )

with f2:
    date_to = st.date_input(
        "По",
        value=max_date,
        min_value=min_date,
        max_value=max_date,
        format="DD.MM.YYYY",
        key="date_to_main"
    )

selected_channel = st.selectbox(
    "Канал",
    channel_options,
    key="channel_main"
)

st.markdown('</div>', unsafe_allow_html=True)

if date_from > date_to:
    st.error("Дата 'С' не может быть позже даты 'По'")
    st.stop()

# =========================
# ПРИМЕНЕНИЕ ФИЛЬТРОВ
# =========================
df = df[
    (df["Дата"].dt.date >= date_from) &
    (df["Дата"].dt.date <= date_to)
].copy()

if selected_channel != "Все":
    df = df[df["Канал"].astype(str).str.strip() == selected_channel].copy()

exp = exp[
    (exp["Дата"].dt.date >= date_from) &
    (exp["Дата"].dt.date <= date_to)
].copy()

# =========================
# РАСЧЕТЫ
# =========================
df["Мой"] = 0.0
df.loc[df["Это Ariston"], "Мой"] = df.loc[df["Это Ariston"], "Прибыль"] / 2
df.loc[~df["Это Ariston"] & df["Плюс"], "Мой"] = df.loc[~df["Это Ariston"] & df["Плюс"], "Прибыль"] / 2

df["Алексей"] = 0.0
df.loc[df["Это Ariston"], "Алексей"] = df.loc[df["Это Ariston"], "Прибыль"] / 2
df.loc[~df["Это Ariston"] & df["Плюс"], "Алексей"] = df.loc[~df["Это Ariston"] & df["Плюс"], "Прибыль"] / 2
df.loc[~df["Это Ariston"] & ~df["Плюс"], "Алексей"] = df.loc[~df["Это Ariston"] & ~df["Плюс"], "Прибыль"]

gross_profit = df["Прибыль"].sum()
my_income = df["Мой"].sum()
alex_income = df["Алексей"].sum()

expenses = exp["Сумма"].sum() if "Сумма" in exp.columns else 0
half_expenses = expenses / 2

my_net = my_income - half_expenses
alex_net = alex_income - half_expenses
total_net = my_net + alex_net

sales_count = len(df)
avg_check = df["РРЦ"].mean() if sales_count > 0 else 0
revenue_sum = df["РРЦ"].sum() if "РРЦ" in df.columns else 0
margin_percent = (gross_profit / revenue_sum * 100) if revenue_sum > 0 else 0

# =========================
# ВЕРХНИЕ КАРТОЧКИ
# =========================
k1, k2 = st.columns(2)
k3, k4 = st.columns(2)

with k1:
    st.markdown(f"""
    <div class="card">
        <div class="card-title">Чистая прибыль</div>
        <div class="card-value value-green">{format_money(total_net)} ₸</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="card">
        <div class="card-title">Стас чистый доход</div>
        <div class="card-value">{format_money(my_net)} ₸</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="card">
        <div class="card-title">Алексей чистый доход</div>
        <div class="card-value value-blue">{format_money(alex_net)} ₸</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="card">
        <div class="card-title">Расходы</div>
        <div class="card-value value-red">{format_money(expenses)} ₸</div>
    </div>
    """, unsafe_allow_html=True)

# =========================
# ПРИБЫЛЬ ПО ДНЯМ
# =========================
st.subheader("Прибыль по дням")

if not df.empty:
    daily_df = (
        df.groupby("Дата", as_index=False)["Прибыль"]
        .sum()
        .sort_values("Дата")
    )

    if not daily_df.empty:
        daily_df["Дата_подпись"] = daily_df["Дата"].dt.strftime("%d.%m")

        fig = px.line(
            daily_df,
            x="Дата_подпись",
            y="Прибыль",
            markers=True,
            height=320
        )

        fig.update_layout(
            paper_bgcolor="#151922",
            plot_bgcolor="#151922",
            font=dict(color="#cbd5e1"),
            margin=dict(l=10, r=10, t=20, b=10),
            xaxis_title="Дата",
            yaxis_title="Прибыль, ₸"
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displayModeBar": False,
                "staticPlot": True
            }
        )


# =========================
# ТОП-5
# =========================
st.subheader("Топ-5 товаров по прибыли")

if not df.empty:
    top_products = (
        df.groupby("Наименование", as_index=False)["Прибыль"]
        .sum()
        .sort_values("Прибыль", ascending=False)
        .head(5)
    )

    if not top_products.empty:
        top_products = top_products.sort_values("Прибыль", ascending=True)

        fig = px.bar(
            top_products,
            x="Прибыль",
            y="Наименование",
            orientation="h",
            height=360
        )

        fig.update_layout(
            paper_bgcolor="#151922",
            plot_bgcolor="#151922",
            font=dict(color="#cbd5e1"),
            margin=dict(l=10, r=10, t=20, b=10),
            xaxis_title="Прибыль",
            yaxis_title=""
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displayModeBar": False,
                "staticPlot": True
            }
        )



# =========================
# БЫСТРЫЙ ОТЧЕТ
# =========================
start_date_text = date_from.strftime("%d.%m.%Y")
end_date_text = date_to.strftime("%d.%m.%Y")

with st.expander("Быстрый отчет"):
    st.markdown(f"""
    <div class="section-box">
    <div style="font-size:14px; color:#aab2bf; margin-bottom:10px;">
        Период: <span style="color:#34d399;">{start_date_text} — {end_date_text}</span>
    </div>

    <div style="font-size:14px; color:#aab2bf; margin-bottom:12px;">
        Канал: <span style="color:#f3f4f6;">{selected_channel}</span>
    </div>

    <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
        <span style="color:#aab2bf;">Стас чистый доход</span>
        <span style="color:#34d399; font-weight:600;">{format_money(my_net)} ₸</span>
    </div>

    <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
        <span style="color:#aab2bf;">Алексей чистый доход</span>
        <span style="color:#60a5fa; font-weight:600;">{format_money(alex_net)} ₸</span>
    </div>

    <hr>

    <div style="display:flex; justify-content:space-between; font-size:18px; font-weight:700;">
        <span style="color:#f3f4f6;">Итого</span>
        <span style="color:#34d399;">{format_money(total_net)} ₸</span>
    </div>
    </div>
    """, unsafe_allow_html=True)

# =========================
# ПРОДАЖИ
# =========================
with st.expander("Продажи"):
    st.markdown(f"""
    <div class="section-box">
        <div style="display:flex; justify-content:space-between; margin-bottom:12px;">
            <span style="color:#aab2bf;">Количество продаж</span>
            <span style="font-weight:700;">{sales_count}</span>
        </div>
        <div style="display:flex; justify-content:space-between; margin-bottom:12px;">
            <span style="color:#aab2bf;">Средний чек</span>
            <span style="font-weight:700; color:#34d399;">{format_money(avg_check)} ₸</span>
        </div>
        <div style="display:flex; justify-content:space-between;">
            <span style="color:#aab2bf;">Средняя маржа</span>
            <span style="font-weight:700; color:#60a5fa;">{margin_percent:.1f}%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =========================
# РАСХОДЫ
# =========================
with st.expander("Расходы"):
    st.markdown(f"""
    <div class="section-box">
        <div style="font-size:14px; color:#aab2bf;">Общие расходы</div>
        <div style="font-size:28px; font-weight:700; color:#f87171;">{format_money(expenses)} ₸</div>
    </div>
    """, unsafe_allow_html=True)

    if not exp.empty and {"Дата_рус", "Тип расхода", "Сумма"}.issubset(exp.columns):
        recent_exp = exp[["Дата_рус", "Тип расхода", "Сумма"]].tail(3).copy()

        st.markdown("**Последние расходы**")

        for _, row in recent_exp.iterrows():
            st.markdown(f"""
            <div class="section-box">
                <div style="font-size:13px; color:#aab2bf;">{row["Дата_рус"]}</div>
                <div style="font-size:15px; color:#f3f4f6;">{row["Тип расхода"]}</div>
                <div style="font-size:16px; font-weight:700; color:#f87171;">{format_money(row["Сумма"])} ₸</div>
            </div>
            """, unsafe_allow_html=True)

