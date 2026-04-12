import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Финансовая сводка",
    layout="wide"
)

# =========================
# НАСТРОЙКИ
# =========================
TEEG_SHEET_CSV = (
    "https://docs.google.com/spreadsheets/d/"
    "1a4rIkdUUNjdO21CmKNb71FctyTdr2JMq/"
    "export?format=csv&gid=115078867"
)

# =========================
# СТИЛИ
# =========================
st.markdown(
    """
    <style>
    .stApp {
        background: #151922;
        color: #f3f4f6;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    .main-title {
        font-size: 54px;
        font-weight: 800;
        line-height: 1.05;
        margin-bottom: 10px;
        color: #f3f4f6;
    }

    .sub-title {
        font-size: 16px;
        color: #aab2bf;
        margin-bottom: 28px;
    }

    .section-box {
        background: #1b2130;
        border: 1px solid #2a3347;
        border-radius: 18px;
        padding: 18px 20px;
        margin-bottom: 16px;
    }

    .metric-card {
        background: #1b2130;
        border: 1px solid #2a3347;
        border-radius: 18px;
        padding: 18px 20px;
    }

    .metric-label {
        font-size: 14px;
        color: #aab2bf;
        margin-bottom: 8px;
    }

    .metric-value {
        font-size: 34px;
        font-weight: 800;
        color: #f3f4f6;
    }

    .small-label {
        font-size: 14px;
        color: #aab2bf;
        margin-bottom: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# САЙДБАР
# =========================
page = st.sidebar.selectbox(
    "Раздел",
    ["Финансовая сводка", "Создать заказ"]
)

# =========================
# ЗАГРУЗКА ПРАЙСА
# =========================
@st.cache_data(ttl=60)
def load_price_csv(url: str) -> pd.DataFrame:
    df = pd.read_csv(url)
    df.columns = df.columns.astype(str).str.strip()

    required_cols = {"Бренд", "Модель", "ТипЦены", "Цена"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Нет нужных колонок: {', '.join(sorted(missing))}")

    df = df[list(required_cols)].copy()
    df["Бренд"] = df["Бренд"].astype(str).str.strip()
    df["Модель"] = df["Модель"].astype(str).str.strip()
    df["ТипЦены"] = df["ТипЦены"].astype(str).str.strip()
    df["Цена"] = pd.to_numeric(df["Цена"], errors="coerce")
    df = df.dropna(subset=["Бренд", "Модель", "ТипЦены", "Цена"])

    return df


def format_money(value: float | int) -> str:
    return f"{int(round(value)):,}".replace(",", " ")


# =========================
# СОЗДАТЬ ЗАКАЗ
# =========================
if page == "Создать заказ":
    st.markdown('<div class="main-title">Создать заказ</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-title">Выбор прайса, модели, количества и расчёт суммы</div>',
        unsafe_allow_html=True
    )

    try:
        df = load_price_csv(TEEG_SHEET_CSV)
    except Exception as e:
        st.error(f"Ошибка загрузки прайса: {e}")
        st.stop()

    brands = sorted(df["Бренд"].unique().tolist())
    brand = st.selectbox("Выбери бренд", brands)

    df_brand = df[df["Бренд"] == brand].copy()

    models = sorted(df_brand["Модель"].unique().tolist())
    model = st.selectbox("Выбери модель", models)

    df_model = df_brand[df_brand["Модель"] == model].copy()

    price_types = sorted(df_model["ТипЦены"].unique().tolist())
    price_type = st.selectbox("Тип цены", price_types)

    selected_row = df_model[df_model["ТипЦены"] == price_type].iloc[0]
    price = float(selected_row["Цена"])

    qty = st.number_input("Количество", min_value=1, value=1, step=1)
    total = price * qty

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Цена</div>
                <div class="metric-value">{format_money(price)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Сумма</div>
                <div class="metric-value">{format_money(total)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if "order_items" not in st.session_state:
        st.session_state.order_items = []

    if st.button("Добавить в заказ", use_container_width=True):
        st.session_state.order_items.append(
            {
                "Бренд": brand,
                "Модель": model,
                "ТипЦены": price_type,
                "Количество": int(qty),
                "Цена": int(round(price)),
                "Сумма": int(round(total)),
            }
        )
        st.success("Позиция добавлена в заказ")

    if st.session_state.order_items:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="small-label">Текущий заказ</div>', unsafe_allow_html=True)

        order_df = pd.DataFrame(st.session_state.order_items)

        st.dataframe(
            order_df,
            use_container_width=True,
            hide_index=True
        )

        grand_total = order_df["Сумма"].sum()

        st.markdown(
            f"""
            <div class="metric-card" style="margin-top:12px;">
                <div class="metric-label">Итого по заказу</div>
                <div class="metric-value">{format_money(grand_total)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Очистить заказ", use_container_width=True):
                st.session_state.order_items = []
                st.rerun()

        with col_b:
            csv_data = order_df.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                "Скачать заказ CSV",
                data=csv_data,
                file_name="zakaz.csv",
                mime="text/csv",
                use_container_width=True,
            )

# =========================
# ФИНАНСОВАЯ СВОДКА
# =========================
elif page == "Финансовая сводка":

    st.title("Финансовая сводка")
    st.caption("Продажи • Прибыль • Рентабельность")

    # --- ЗАГРУЗКА ДАННЫХ ---
    sales = load_price_csv("https://docs.google.com/spreadsheets/d/1D26s-VjLPvg43z-Hk38fU7Y4tPFZ9h-UfFjJzQnvtB0/export?format=csv")
    expenses = load_price_csv("https://docs.google.com/spreadsheets/d/1AuxP3Qgk-zzOVOZChdwZ1udx4A8o01k3-w8_8TfJxK0/export?format=csv")

    sales.columns = sales.columns.str.strip()
    expenses.columns = expenses.columns.str.strip()


    # --- ПРИВОДИМ ДАТЫ ---
    sales["Дата"] = pd.to_datetime(sales["Дата"], errors="coerce")
    expenses["Дата"] = pd.to_datetime(expenses["Дата"], errors="coerce")

    # удаляем пустые даты
    sales = sales.dropna(subset=["Дата"])
    expenses = expenses.dropna(subset=["Дата"])

    # --- ФИЛЬТРЫ ---
    st.subheader("Фильтры")

    min_date = sales["Дата"].min().date()
    max_date = sales["Дата"].max().date()

    col1, col2 = st.columns(2)

    with col1:
        date_from = st.date_input("С", min_date)

    with col2:
        date_to = st.date_input("По", max_date)

    channel_options = ["Все"] + sorted(sales["Каспий"].dropna().unique().tolist())
    channel = st.selectbox("Канал", channel_options)

    # --- ПРИМЕНЕНИЕ ФИЛЬТРОВ ---
    df = sales[
        (sales["Дата"].dt.date >= date_from) &
        (sales["Дата"].dt.date <= date_to)
    ]

    if channel != "Все":
        df = df[df["Каспий"] == channel]

    # --- РАСЧЕТЫ ---
    revenue = df["РРЦ"].sum()
    profit = df["Чистая прибыль"].sum()

    expenses_filtered = expenses[
        (expenses["Дата"].dt.date >= date_from) &
        (expenses["Дата"].dt.date <= date_to)
    ]

    total_expenses = expenses_filtered["Сумма"].sum()

    net_profit = profit - total_expenses

    # --- КАРТОЧКИ ---
    st.subheader("Итоги")

    col1, col2, col3 = st.columns(3)

    col1.metric("Выручка", f"{int(revenue):,}".replace(",", " "))
    col2.metric("Прибыль", f"{int(profit):,}".replace(",", " "))
    col3.metric("Чистая прибыль", f"{int(net_profit):,}".replace(",", " "))

    st.divider()

    # --- ДЕТАЛИ ---
    st.write("Расходы:", f"{int(total_expenses):,}".replace(",", " "))
    st.write("Сделок:", len(df))
