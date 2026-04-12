import pandas as pd
import streamlit as st
from matplotlib import pyplot as plt

st.set_page_config(page_title="Финансовая сводка", layout="wide")

# ---------- СТИЛИ ----------
st.markdown(f"""
<style>
.stApp {
    background: #151922;
    color: #f3f4f6;
}

.block-container {
    padding-top: 1.2rem;
    padding-bottom: 2rem;
    max-width: 1400px;
}

h1, h2, h3 {
    color: #f9fafb;
}

.main-title {
    font-size: 38px;
    font-weight: 800;
    margin-bottom: 4px;
}

.sub-title {
    color: #aab2bf;
    font-size: 16px;
    margin-bottom: 18px;
}

.card {
    background: #1d2330;
    border: 1px solid #2f3747;
    border-radius: 18px;
    padding: 16px 18px;
    margin-bottom: 12px;
}

.card-title {
    color: #aab2bf;
    font-size: 13px;
    margin-bottom: 8px;
}

.card-value {
    color: #f8fafc;
    font-size: 30px;
    font-weight: 800;
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

.section-box {
    background: #1d2330;
    border: 1px solid #2f3747;
    border-radius: 18px;
    padding: 14px 16px;
    margin-bottom: 14px;
}

div[data-baseweb="select"] > div,
div[data-testid="stDateInput"] > div {
    background: #1d2330 !important;
    border: 1px solid #2f3747 !important;
    border-radius: 14px !important;
}

input {
    color: #f3f4f6 !important;
}

@media (max-width: 768px) {
    .main-title {
        font-size: 28px;
    }

    .sub-title {
        font-size: 14px;
    }
}
</style>
""", unsafe_allow_html=True)

# ---------- URL ----------
SALES_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTVCDzAu1DphzNCs2AzlpsjgJyRfzYWEAicdYbqMEFCcjjcxo4WyjVkcKa2-6G2BDyhM2GaBRx23DvO/pub?gid=1240951053&single=true&output=csv"
EXPENSES_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSYEdrQn9FbW5xYzz_UuvUvOUYxbENvC1JnSE4z00YUTvtCxtnP4sU54J-Vs_40kEcuyQLRm-Ae6B_0/pub?gid=1622934317&single=true&output=csv"

# ---------- ВСПОМОГАТЕЛЬНОЕ ----------
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
    cost_col = find_column(df, ["Себестоимость", "себестоимость"])
    rrc_col = find_column(df, ["РРЦ", "ррц"])
    kaspi_col = find_column(df, ["Комиссия Kaspi", "комиссия kaspi"])
    profit_col = find_column(df, ["Чистая прибыль", "чистая прибыль"])
    comment_col = find_column(df, ["Комментарий", "комментарий", "Комментарии", "комментарии"])

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
    df["Себестоимость"] = pd.to_numeric(df[cost_col], errors="coerce").fillna(0)
    df["РРЦ"] = pd.to_numeric(df[rrc_col], errors="coerce").fillna(0)
    df["Комиссия Kaspi"] = pd.to_numeric(df[kaspi_col], errors="coerce").fillna(0)
    df["Комментарий"] = df[comment_col].fillna("").astype(str).str.replace("\xa0", "", regex=False).str.strip()

    if profit_col is not None:
        df["Прибыль"] = pd.to_numeric(df[profit_col], errors="coerce").fillna(0)
    else:
        df["Прибыль"] = df["РРЦ"] - df["Себестоимость"] - df["Комиссия Kaspi"]

    df["Маржа %"] = (df["Прибыль"] / df["РРЦ"] * 100).replace([float("inf"), -float("inf")], 0).fillna(0)
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

# ---------- ЗАГРУЗКА ----------
sales_raw, expenses_raw = load_data()
df = load_sales_dataframe(sales_raw)
exp = load_expenses_dataframe(expenses_raw)

valid_dates = df["Дата"].dropna()
if valid_dates.empty:
    st.error("В продажах не распознаны даты.")
    st.stop()

# ---------- ШАПКА ----------
st.markdown('<div class="main-title">Финансовая сводка</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Продажи • Прибыль • Рентабельность</div>', unsafe_allow_html=True)

top_left, top_right = st.columns([1, 1])

with top_left:
    if st.button("Обновить данные"):
        st.cache_data.clear()
        st.rerun()

with top_right:
    st.caption("Кэш обновляется примерно раз в 60 секунд")

# ---------- ФИЛЬТРЫ В ОСНОВНОМ ОКНЕ ----------
st.markdown('<div class="section-box">', unsafe_allow_html=True)
st.subheader("Фильтры")

min_date = valid_dates.min().date()
max_date = valid_dates.max().date()

channel_values = sorted(
    [
        str(x).strip()
        for x in df["Канал"].dropna().unique().tolist()
        if str(x).strip() != ""
    ]
)
channel_options = ["Все"] + channel_values

f1, f2, f3 = st.columns(3)

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

with f3:
    selected_channel = st.selectbox(
        "Канал",
        channel_options,
        key="channel_main"
    )

st.markdown('</div>', unsafe_allow_html=True)

if date_from > date_to:
    st.error("Дата 'С' не может быть позже даты 'По'")
    st.stop()

# ---------- ПРИМЕНЕНИЕ ФИЛЬТРОВ ----------
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

# ---------- РАСЧЕТЫ ----------
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

# ---------- ВЕРХНИЕ КАРТОЧКИ ----------
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
        <div class="card-title">Мой чистый</div>
        <div class="card-value">{format_money(my_net)} ₸</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="card">
        <div class="card-title">Алексей чистый</div>
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

# ---------- ПРОДАЖИ ----------
with st.expander("Продажи", expanded=True):
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

# ---------- ПРИБЫЛЬ ПО ДНЯМ ----------
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

# ---------- ТОП-5 ----------
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

        names = top_df["Наименование"].apply(lambda x: x[:28] + "..." if len(str(x)) > 28 else str(x))
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

# ---------- БЫСТРЫЙ ОТЧЕТ ----------
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
        <span style="color:#aab2bf;">Мой чистый</span>
        <span style="color:#34d399; font-weight:600;">{format_money(my_net)} ₸</span>
    </div>

    <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
        <span style="color:#aab2bf;">Алексей чистый</span>
        <span style="color:#60a5fa; font-weight:600;">{format_money(alex_net)} ₸</span>
    </div>

    <hr>

    <div style="display:flex; justify-content:space-between; font-size:18px; font-weight:700;">
        <span style="color:#f3f4f6;">Итого</span>
        <span style="color:#34d399;">{format_money(total_net)} ₸</span>
    </div>
    </div>
    """, unsafe_allow_html=True)

# ---------- РАСХОДЫ ----------
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
