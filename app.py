import os
from datetime import date

import pandas as pd
import streamlit as st
from matplotlib import pyplot as plt

st.set_page_config(page_title="Финансовая сводка", layout="wide")

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

/* Поля */
div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div,
div[data-testid="stDateInput"] > div,
div[data-testid="stSelectbox"] > div,
div[data-testid="stTextInput"] > div,
div[data-testid="stTextArea"] > div {
    background: #1d2330 !important;
    border: 1px solid #2f3747 !important;
    border-radius: 14px !important;
    color: #f3f4f6 !important;
}

div[data-baseweb="input"] input,
div[data-testid="stDateInput"] input,
div[data-testid="stTextInput"] input,
textarea {
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

div[data-testid="stTabs"] button {
    color: #cbd5e1 !important;
    font-weight: 700 !important;
}

div[data-testid="stTabs"] button[aria-selected="true"] {
    color: #ffffff !important;
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

ORDERS_FILE = "orders.xlsx"

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

def parse_float_text(value: str) -> float:
    if value is None:
        return 0.0
    text = str(value).strip().replace(" ", "").replace(",", ".")
    if text == "":
        return 0.0
    try:
        return float(text)
    except Exception:
        return 0.0

def parse_int_text(value: str, default: int = 1) -> int:
    if value is None:
        return default
    text = str(value).strip().replace(" ", "").replace(",", ".")
    if text == "":
        return default
    try:
        parsed = int(float(text))
        return max(1, parsed)
    except Exception:
        return default

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

def ensure_orders_file():
    if not os.path.exists(ORDERS_FILE):
        pd.DataFrame(columns=[
            "Дата заказа",
            "Канал продажи",
            "Бренд",
            "Модель",
            "Тип цены",
            "Количество",
            "Цена за шт",
            "Общая сумма",
            "Комментарий",
        ]).to_excel(ORDERS_FILE, index=False)

def load_orders_dataframe() -> pd.DataFrame:
    ensure_orders_file()
    try:
        orders = pd.read_excel(ORDERS_FILE)
        orders.columns = (
            orders.columns.astype(str)
            .str.replace("\ufeff", "", regex=False)
            .str.replace("\xa0", " ", regex=False)
            .str.strip()
        )
        if "Дата заказа" in orders.columns:
            orders["Дата заказа"] = pd.to_datetime(orders["Дата заказа"], errors="coerce")
        return orders
    except Exception:
        return pd.DataFrame(columns=[
            "Дата заказа",
            "Канал продажи",
            "Бренд",
            "Модель",
            "Тип цены",
            "Количество",
            "Цена за шт",
            "Общая сумма",
            "Комментарий",
        ])

def save_order_row(row: dict):
    ensure_orders_file()
    orders = load_orders_dataframe()
    updated = pd.concat([orders, pd.DataFrame([row])], ignore_index=True)
    updated.to_excel(ORDERS_FILE, index=False)

# =========================
# ЗАГРУЗКА
# =========================
sales_raw, expenses_raw = load_data()
base_df = load_sales_dataframe(sales_raw)
base_exp = load_expenses_dataframe(expenses_raw)

valid_dates = base_df["Дата"].dropna()
if valid_dates.empty:
    st.error("В продажах не распознаны даты.")
    st.stop()

# =========================
# ВКЛАДКИ
# =========================
tab1, tab2 = st.tabs(["Финансовая сводка", "Создать заказ"])

# =========================
# ФИНАНСОВАЯ СВОДКА
# =========================
with tab1:
    df = base_df.copy()
    exp = base_exp.copy()

    st.markdown('<div class="main-title">Финансовая сводка</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Продажи ∙ Прибыль ∙ Рентабельность</div>', unsafe_allow_html=True)

    if st.button("Обновить данные", key="refresh_main"):
        st.cache_data.clear()
        st.rerun()

    st.caption("Кэш обновляется примерно раз в 60 секунд")

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
            key="date_from_main_v2"
        )

    with f2:
        date_to = st.date_input(
            "По",
            value=max_date,
            min_value=min_date,
            max_value=max_date,
            format="DD.MM.YYYY",
            key="date_to_main_v2"
        )

    selected_channel = st.selectbox(
        "Канал",
        channel_options,
        key="channel_main_v2"
    )

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
            labels = daily_df["Дата"].dt.strftime("%d.%m")

            fig, ax = plt.subplots(figsize=(10, 4))
            fig.patch.set_facecolor("#151922")
            ax.set_facecolor("#151922")

            ax.plot(daily_df["Дата"], daily_df["Прибыль"], marker="o", color="#34d399", linewidth=2)

            ax.set_xlabel("Дата", color="#cbd5e1")
            ax.set_ylabel("Прибыль", color="#cbd5e1")
            ax.tick_params(colors="#cbd5e1")
            ax.grid(True, alpha=0.2, color="#2f3747")

            for spine in ax.spines.values():
                spine.set_color("#2f3747")

            ax.set_xticks(daily_df["Дата"])
            ax.set_xticklabels(labels, rotation=45, ha="right")

            plt.tight_layout()
            st.pyplot(fig, use_container_width=True)
        else:
            st.info("Нет данных для графика.")
    else:
        st.info("Нет данных для графика.")

    # =========================
    # ТОП-5
    # =========================
    st.subheader("Топ-5 товаров по прибыли")

    if not df.empty:
        top_df = (
            df.groupby("Наименование", as_index=False)["Прибыль"]
            .sum()
            .sort_values("Прибыль", ascending=False)
            .head(5)
        )

        if not top_df.empty:
            fig, ax = plt.subplots(figsize=(10, 5))
            fig.patch.set_facecolor("#151922")
            ax.set_facecolor("#151922")

            names = top_df["Наименование"].apply(
                lambda x: x[:28] + "..." if len(str(x)) > 28 else str(x)
            )
            ax.bar(names, top_df["Прибыль"], color="#60a5fa")

            ax.set_xlabel("Товар", color="#cbd5e1")
            ax.set_ylabel("Прибыль", color="#cbd5e1")
            ax.tick_params(colors="#cbd5e1")
            ax.grid(True, axis="y", alpha=0.2, color="#2f3747")

            for spine in ax.spines.values():
                spine.set_color("#2f3747")

            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()
            st.pyplot(fig, use_container_width=True)
        else:
            st.info("Нет данных по товарам.")
    else:
        st.info("Нет данных по товарам.")

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

# =========================
# СОЗДАНИЕ ЗАКАЗА (НОВАЯ ЛОГИКА)
# =========================
with tab2:
    if "invoice_items" not in st.session_state:
        st.session_state.invoice_items = []

    st.markdown('<div class="main-title">Создать заказ</div>', unsafe_allow_html=True)

    PRICE_URL_TEEG = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTs6jLT1iBie0Fcm28dPQ_x98Pm61yDGxBnHt85bPjyAUw_144eS0HaIEuejDQwYQ/pub?gid=115078867&single=true&output=csv"
    PRICE_URL_ARISTON = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQIpFNDSv1XvQC4-uSvrHyM0QqXpM83hn2K7b2tCVGj8h0R9R199Sd2PkwTCRVVQ/pub?gid=0&single=true&output=csv"

    @st.cache_data(ttl=60)
    def load_price():
        df1 = pd.read_csv("https://docs.google.com/spreadsheets/d/e/2PACX-1vTs6jLT1iBie0Fcm28dPQ_x98Pm61yDGxBnHt85bPjyAUw_144eS0HaIEuejDQwYQ/pub?gid=115078867&single=true&output=csv")
        df2 = pd.read_csv("https://docs.google.com/spreadsheets/d/e/2PACX-1vQIpFNDSvIXvCQ4-uSvrHyM0QqXpMO83hn2K7b2tCVGJ8hOR9R199Sd2pKwTCRvVQ/pub?gid=1662607201&single=true&output=csv")
    
        df1.columns = df1.columns.str.strip()
        df2.columns = df2.columns.str.strip()
    
        df = pd.concat([df1, df2], ignore_index=True)
        df.columns = df.columns.str.strip()
        return df

    price_df = load_price().fillna("")

    for col in ["Бренд", "Модель", "ТипЦены"]:
        price_df[col] = (
            price_df[col]
            .astype(str)
            .str.replace("\xa0", " ", regex=False)
            .str.replace("\ufeff", "", regex=False)
            .str.strip()
        )

    price_df["Цена"] = pd.to_numeric(price_df["Цена"], errors="coerce").fillna(0)
    price_df["Себестоимость"] = pd.to_numeric(price_df["Себестоимость"], errors="coerce").fillna(0)

    brands = sorted([
        x for x in price_df["Бренд"].dropna().unique()
        if str(x).strip() != ""
    ])
    brand = st.selectbox("Бренд", brands)

    models = sorted([
        x for x in price_df.loc[price_df["Бренд"] == brand, "Модель"].dropna().unique()
        if str(x).strip() != ""
    ])
    model = st.selectbox("Модель", models)

    price_types = sorted([
        x for x in price_df.loc[
            (price_df["Бренд"] == brand) &
            (price_df["Модель"] == model),
            "ТипЦены"
        ].dropna().unique()
        if str(x).strip() != ""
    ])
    price_type = st.selectbox("Тип цены", price_types)

    selected_row = price_df[
        (price_df["Бренд"] == brand) &
        (price_df["Модель"] == model) &
        (price_df["ТипЦены"] == price_type)
    ].copy()

    if not selected_row.empty:
        selected_row = selected_row[selected_row["Цена"] > 0]

    price = float(selected_row["Цена"].iloc[0]) if not selected_row.empty else 0
    cost = float(selected_row["Себестоимость"].iloc[0]) if not selected_row.empty else 0

    st.markdown(f"""
    <div class="card">
        <div class="card-title">Цена</div>
        <div class="card-value value-blue">{format_money(price)} ₸</div>
    </div>
    """, unsafe_allow_html=True)

    qty = st.number_input("Количество", min_value=1, value=1)

    total_sum = price * qty if price else 0

    st.markdown(f"""
    <div class="card">
        <div class="card-title">Сумма</div>
        <div class="card-value">{format_money(total_sum)} ₸</div>
    </div>
    """, unsafe_allow_html=True)

    comment = st.text_input("Комментарий", value="")

    current_row = {
        "Дата": pd.Timestamp.today().strftime("%d.%m.%Y"),
        "Бренд": brand,
        "Модель": model,
        "Количество": qty,
        "Цена": price,
        "Сумма": total_sum,
        "Комментарий": comment
    }


    b1, b2, b3 = st.columns(3)

    with b1:
        if st.button("Добавить позицию"):
            st.session_state.invoice_items.append(current_row.copy())
            st.success("Позиция добавлена")

    with b2:
        if st.button("Очистить накладную"):
            st.session_state.invoice_items = []
            st.success("Накладная очищена")

with b3:

    if "saved_invoice_ready" not in st.session_state:
        st.session_state.saved_invoice_ready = False

    if st.button("Сохранить накладную в Excel"):

        if st.session_state.invoice_items:

            file_path = "orders.xlsx"

            invoice_df = pd.DataFrame(st.session_state.invoice_items)

            final_columns = [
                "Дата",
                "Бренд",
                "Модель",
                "Количество",
                "Цена",
                "Сумма",
                "Комментарий"
            ]

            for col in final_columns:
                if col not in invoice_df.columns:
                    invoice_df[col] = ""

            invoice_df = invoice_df[final_columns].copy()

            total_invoice_sum = pd.to_numeric(invoice_df["Сумма"], errors="coerce").fillna(0).sum()

            from openpyxl import Workbook
            from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
            from openpyxl.utils import get_column_letter

            wb = Workbook()
            ws = wb.active
            ws.title = "Накладная"

            # Название компании
            ws.merge_cells("A1:G1")
            ws["A1"] = "Королевство бойлеров"
            ws["A1"].font = Font(size=16, bold=True, color="FFFFFF")
            ws["A1"].fill = PatternFill("solid", fgColor="1F4E78")
            ws["A1"].alignment = Alignment(horizontal="center", vertical="center")

            # Подзаголовок
            ws.merge_cells("A2:G2")
            ws["A2"] = f"Накладная от {pd.Timestamp.today().strftime('%d.%m.%Y')}"
            ws["A2"].font = Font(size=11, bold=True, color="FFFFFF")
            ws["A2"].fill = PatternFill("solid", fgColor="4F81BD")
            ws["A2"].alignment = Alignment(horizontal="center", vertical="center")

            # Заголовки таблицы
            headers = ["Дата", "Бренд", "Модель", "Количество", "Цена", "Сумма", "Комментарий"]
            header_row = 4

            thin = Side(style="thin", color="BFBFBF")
            border = Border(left=thin, right=thin, top=thin, bottom=thin)

            for col_num, header in enumerate(headers, 1):
                cell = ws.cell(row=header_row, column=col_num, value=header)
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill("solid", fgColor="4472C4")
                cell.alignment = Alignment(horizontal="center", vertical="center")
                cell.border = border

            # Данные
            start_row = 5
            for row_idx, row in enumerate(invoice_df.itertuples(index=False), start_row):
                values = list(row)
                for col_num, value in enumerate(values, 1):
                    cell = ws.cell(row=row_idx, column=col_num, value=value)
                    cell.border = border
                    if col_num in [4]:
                        cell.alignment = Alignment(horizontal="center")
                    elif col_num in [5, 6]:
                        cell.alignment = Alignment(horizontal="right")
                    else:
                        cell.alignment = Alignment(horizontal="left")

            # Итог
            total_row = start_row + len(invoice_df)

            ws.cell(row=total_row, column=1, value="ИТОГО")
            ws.cell(row=total_row, column=6, value=total_invoice_sum)

            for col_num in range(1, 8):
                cell = ws.cell(row=total_row, column=col_num)
                cell.font = Font(bold=True)
                cell.fill = PatternFill("solid", fgColor="D9EAF7")
                cell.border = border

            ws.cell(row=total_row, column=1).alignment = Alignment(horizontal="center")
            ws.cell(row=total_row, column=6).alignment = Alignment(horizontal="right")

            # Ширина колонок
            widths = {
                "A": 14,   # Дата
                "B": 16,   # Бренд
                "C": 38,   # Модель
                "D": 14,   # Количество
                "E": 14,   # Цена
                "F": 16,   # Сумма
                "G": 22    # Комментарий
            }

            for col_letter, width in widths.items():
                ws.column_dimensions[col_letter].width = width

            # Высота строк
            ws.row_dimensions[1].height = 24
            ws.row_dimensions[2].height = 20

            wb.save(file_path)

            st.success("Накладная сохранена")
            st.session_state.saved_invoice_ready = True
            st.session_state.invoice_items = []

        else:
            st.warning("Накладная пустая")

    if st.session_state.saved_invoice_ready:
        with open("orders.xlsx", "rb") as f:
            st.download_button(
                "Скачать накладную",
                data=f,
                file_name="orders.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            with col2:
    if st.button("➕ Добавить в продажи (ОПТ)"):

        df_to_save = df_order.copy()

        # Добавляем нужные колонки
        df_to_save["Канал"] = "ОПТ"
        df_to_save["Дата"] = pd.to_datetime("today").strftime("%d.%m.%Y")

        # Переименуем под структуру продаж
        df_to_save = df_to_save.rename(columns={
            "Бренд": "Бренд",
            "Модель": "Наименование",
            "Количество": "Количество",
            "Цена": "РРЦ",
            "Сумма": "РРЦ"  # если у тебя сумма отдельно — уберем ниже
        })

        # Если сумма есть — лучше не трогать РРЦ
        df_to_save["РРЦ"] = df_order["Цена"]
        df_to_save["Себестоимость"] = 0
        df_to_save["Комиссия Kaspi"] = 0
        df_to_save["Комментарий"] = ""

        # Оставляем нужные колонки
        df_to_save = df_to_save[[
            "Дата",
            "Канал",
            "Наименование",
            "Количество",
            "РРЦ",
            "Себестоимость",
            "Комиссия Kaspi",
            "Комментарий"
        ]]

        # === ВАЖНО: ТВОЯ ФУНКЦИЯ ДОБАВЛЕНИЯ ===
        append_to_google_sheet(df_to_save)

        st.success("✅ Добавлено в продажи (ОПТ)")



