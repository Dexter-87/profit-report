import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Финансовая сводка",
    layout="wide"
)

# =========================
# ССЫЛКИ НА GOOGLE SHEETS
# =========================
PRICE_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1a4rIkdUUNjdO21CmKNb71FctyTdr2JMq/"
    "export?format=csv&gid=115078867"
)

SALES_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1D26s-VjLPvg43z-Hk38fU7Y4tPFZ9h-UffjJzQnvtB0/"
    "export?format=csv"
)

EXPENSES_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1AuxP3Qgk-zzOVOZChdwZ1udx4A8o01k3-w8_8TfjxK07/"
    "export?format=csv"
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

    .metric-card {
        background: #1b2130;
        border: 1px solid #2a3347;
        border-radius: 18px;
        padding: 18px 20px;
        margin-bottom: 16px;
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

    .section-box {
        background: #1b2130;
        border: 1px solid #2a3347;
        border-radius: 18px;
        padding: 18px 20px;
        margin-bottom: 16px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# =========================
def format_money(value: float | int) -> str:
    return f"{int(round(value)):,}".replace(",", " ")


@st.cache_data(ttl=60)
def load_sheet_csv(url: str) -> pd.DataFrame:
    return pd.read_csv(url)



@st.cache_data(ttl=60)
def load_sheet_csv(url: str) -> pd.DataFrame:
    df = pd.read_csv(url)
    df.columns = df.columns.astype(str).str.strip()
    return df


    required_cols = {"Бренд", "Модель", "ТипЦены", "Цена"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Нет нужных колонок в прайсе: {', '.join(sorted(missing))}")

    df = df[["Бренд", "Модель", "ТипЦены", "Цена"]].copy()
    df["Бренд"] = df["Бренд"].astype(str).str.strip()
    df["Модель"] = df["Модель"].astype(str).str.strip()
    df["ТипЦены"] = df["ТипЦены"].astype(str).str.strip()
    df["Цена"] = pd.to_numeric(df["Цена"], errors="coerce")
    df = df.dropna(subset=["Бренд", "Модель", "ТипЦены", "Цена"])

    return df


def detect_brand(name: str) -> str:
    text = str(name).lower()
    if "ariston" in text:
        return "Ariston"
    if "thermex" in text:
        return "Thermex"
    if "edisson" in text:
        return "Edisson"
    if "etalon" in text:
        return "Etalon"
    if "garanterm" in text:
        return "Garanterm"
    if "termax" in text:
        return "Termax"
    return "Прочее"


# =========================
# САЙДБАР
# =========================
page = st.sidebar.selectbox(
    "Раздел",
    ["Финансовая сводка", "Создать заказ"]
)

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
        price_df = load_price_csv(PRICE_URL)
    except Exception as e:
        st.error(f"Ошибка загрузки прайса: {e}")
        st.stop()

    brands = sorted(price_df["Бренд"].unique().tolist())
    brand = st.selectbox("Выбери бренд", brands)

    df_brand = price_df[price_df["Бренд"] == brand].copy()

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
        order_df = pd.DataFrame(st.session_state.order_items)

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("Текущий заказ")

        st.dataframe(
            order_df,
            use_container_width=True,
            hide_index=True
        )

        grand_total = order_df["Сумма"].sum()

        st.markdown(
            f"""
            <div class="metric-card">
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
    st.markdown('<div class="main-title">Финансовая сводка</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-title">Продажи • Прибыль • Рентабельность</div>',
        unsafe_allow_html=True
    )

    try:
        sales = load_sheet_csv(
    "https://docs.google.com/spreadsheets/d/1D26s-VjLPvg43z-Hk38fU7Y4tPFZ9h-UfFjJzQnvtB0/gviz/tq?tqx=out:csv&gid=1240951053"
)

        expenses = load_sheet_csv(
    "https://docs.google.com/spreadsheets/d/1AuxP3Qgk-zzOVOZChdwZ1udx4A8o01k3-w8_8TfJxK0/gviz/tq?tqx=out:csv&gid=1622934317"
)

    except Exception as e:
        st.error(f"Ошибка загрузки таблиц: {e}")
        st.stop()

    # --- НОРМАЛИЗАЦИЯ КОЛОНОК ---
    sales.columns = sales.columns.str.strip()
    expenses.columns = expenses.columns.str.strip()

    # --- ПРОВЕРКА КОЛОНОК ---
    sales_required = {
        "Дата", "Каспий", "Наименование", "Себестоимость", "РРЦ", "Комиссия Kaspi", "Чистая прибыль"
    }
    expenses_required = {"Дата", "Тип расхода", "Сумма"}

    missing_sales = sales_required - set(sales.columns)
    missing_expenses = expenses_required - set(expenses.columns)

    if missing_sales:
        st.error(f"В таблице продаж не хватает колонок: {', '.join(sorted(missing_sales))}")
        st.stop()

    if missing_expenses:
        st.error(f"В таблице расходов не хватает колонок: {', '.join(sorted(missing_expenses))}")
        st.stop()

    # --- ПРИВОДИМ ТИПЫ ---
    sales["Дата"] = pd.to_datetime(sales["Дата"], errors="coerce", dayfirst=True)
    expenses["Дата"] = pd.to_datetime(expenses["Дата"], errors="coerce", dayfirst=True)

    numeric_sales_cols = ["Себестоимость", "РРЦ", "Комиссия Kaspi", "Чистая прибыль"]
    for col in numeric_sales_cols:
        sales[col] = pd.to_numeric(sales[col], errors="coerce").fillna(0)

    expenses["Сумма"] = pd.to_numeric(expenses["Сумма"], errors="coerce").fillna(0)

    sales["Каспий"] = sales["Каспий"].astype(str).str.strip()
    sales["Наименование"] = sales["Наименование"].astype(str).str.strip()
    sales["Комментарий"] = sales["Комментарий"].astype(str).str.strip() if "Комментарий" in sales.columns else ""
    sales["Бренд"] = sales["Наименование"].apply(detect_brand)

    sales = sales.dropna(subset=["Дата"])
    expenses = expenses.dropna(subset=["Дата"])

    if sales.empty:
        st.warning("В таблице продаж нет корректных дат.")
        st.stop()

    # --- ФИЛЬТРЫ ---
    st.subheader("Фильтры")

    min_date = sales["Дата"].min().date()
    max_date = sales["Дата"].max().date()

    f1, f2, f3 = st.columns(3)

    with f1:
        date_from = st.date_input("С", value=min_date, min_value=min_date, max_value=max_date)

    with f2:
        date_to = st.date_input("По", value=max_date, min_value=min_date, max_value=max_date)

    with f3:
        channel_options = ["Все"] + sorted(sales["Каспий"].dropna().unique().tolist())
        selected_channel = st.selectbox("Канал", channel_options)

    brand_options = ["Все"] + sorted(sales["Бренд"].dropna().unique().tolist())
    selected_brand = st.selectbox("Бренд", brand_options)

    if date_from > date_to:
        st.error("Дата 'С' не может быть позже даты 'По'")
        st.stop()

    # --- ПРИМЕНЕНИЕ ФИЛЬТРОВ К ПРОДАЖАМ ---
    filtered_sales = sales[
        (sales["Дата"].dt.date >= date_from) &
        (sales["Дата"].dt.date <= date_to)
    ].copy()

    if selected_channel != "Все":
        filtered_sales = filtered_sales[filtered_sales["Каспий"] == selected_channel]

    if selected_brand != "Все":
        filtered_sales = filtered_sales[filtered_sales["Бренд"] == selected_brand]

    # --- ПРИМЕНЕНИЕ ФИЛЬТРОВ К РАСХОДАМ ---
    filtered_expenses = expenses[
        (expenses["Дата"].dt.date >= date_from) &
        (expenses["Дата"].dt.date <= date_to)
    ].copy()

    # --- ОСНОВНЫЕ МЕТРИКИ ---
    revenue = filtered_sales["РРЦ"].sum()
    gross_profit = filtered_sales["Чистая прибыль"].sum()
    total_expenses = filtered_expenses["Сумма"].sum()
    net_profit = gross_profit - total_expenses

    # --- ЛОГИКА ДЕЛЕНИЯ ---
    comment_series = filtered_sales["Комментарий"].astype(str) if "Комментарий" in filtered_sales.columns else pd.Series("", index=filtered_sales.index)

    shared_mask = (
        filtered_sales["Бренд"].eq("Ariston") |
        comment_series.str.contains(r"\+", na=False)
    )

    stas_profit = (filtered_sales.loc[shared_mask, "Чистая прибыль"].sum() * 0.5)
    alexey_profit = (
        filtered_sales.loc[shared_mask, "Чистая прибыль"].sum() * 0.5
        + filtered_sales.loc[~shared_mask, "Чистая прибыль"].sum()
    )

    # расходы пока вычитаем общим итогом только в чистой прибыли
    # персональное деление расходов можно добавить следующим шагом

    # --- КАРТОЧКИ ---
    c1, c2, c3 = st.columns(3)
    c4, c5 = st.columns(2)

    with c1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Выручка</div>
                <div class="metric-value">{format_money(revenue)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Прибыль</div>
                <div class="metric-value">{format_money(gross_profit)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Чистая прибыль</div>
                <div class="metric-value">{format_money(net_profit)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Стас доход</div>
                <div class="metric-value">{format_money(stas_profit)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c5:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Алексей доход</div>
                <div class="metric-value">{format_money(alexey_profit)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --- ДОП. ИНФО ---
    col_x, col_y, col_z = st.columns(3)
    col_x.metric("Расходы", format_money(total_expenses))
    col_y.metric("Сделок", len(filtered_sales))
    avg_margin = (gross_profit / revenue * 100) if revenue > 0 else 0
    col_z.metric("Средняя маржа %", f"{avg_margin:.1f}")

    # --- ПОСЛЕДНИЕ ПРОДАЖИ ---
    st.subheader("Последние продажи")

    preview_cols = [
        "Дата", "Каспий", "Бренд", "Наименование", "РРЦ", "Чистая прибыль"
    ]
    sales_preview = filtered_sales[preview_cols].sort_values("Дата", ascending=False).head(10).copy()
    sales_preview["Дата"] = sales_preview["Дата"].dt.strftime("%d.%m.%Y")

    st.dataframe(
        sales_preview,
        use_container_width=True,
        hide_index=True
    )

    # --- ПОСЛЕДНИЕ РАСХОДЫ ---
    st.subheader("Последние расходы")

    expenses_preview = filtered_expenses[["Дата", "Тип расхода", "Сумма"]].sort_values("Дата", ascending=False).head(10).copy()
    expenses_preview["Дата"] = expenses_preview["Дата"].dt.strftime("%d.%m.%Y")

    st.dataframe(
        expenses_preview,
        use_container_width=True,
        hide_index=True
    )
