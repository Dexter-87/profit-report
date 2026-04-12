import os
from datetime import datetime, date

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st


# =========================
# НАСТРОЙКИ СТРАНИЦЫ
# =========================
st.set_page_config(
    page_title="Финансовая сводка",
    page_icon="📊",
    layout="wide"
)


# =========================
# ПУТИ К ФАЙЛАМ
# =========================
DATA_DIR = "data"
SALES_FILE = os.path.join(DATA_DIR, "sales.xlsx")
EXPENSES_FILE = os.path.join(DATA_DIR, "expenses.xlsx")
ORDERS_FILE = os.path.join(DATA_DIR, "orders.xlsx")


# =========================
# СОЗДАНИЕ ПАПКИ И ФАЙЛОВ
# =========================
def ensure_data_files():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(SALES_FILE):
        sales_df = pd.DataFrame(columns=[
            "Дата",
            "Канал",
            "Бренд",
            "Модель",
            "Количество",
            "Выручка",
            "Прибыль",
            "Стас доход",
            "Алексей доход"
        ])
        sales_df.to_excel(SALES_FILE, index=False)

    if not os.path.exists(EXPENSES_FILE):
        expenses_df = pd.DataFrame(columns=[
            "Дата",
            "Категория",
            "Сумма",
            "Комментарий"
        ])
        expenses_df.to_excel(EXPENSES_FILE, index=False)

    if not os.path.exists(ORDERS_FILE):
        orders_df = pd.DataFrame(columns=[
            "Дата",
            "Канал",
            "Бренд",
            "Модель",
            "Тип цены",
            "Количество",
            "Цена за шт",
            "Общая сумма",
            "Комментарий"
        ])
        orders_df.to_excel(ORDERS_FILE, index=False)


ensure_data_files()


# =========================
# CSS / СТИЛИ
# =========================
st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

.stApp {
    background: linear-gradient(180deg, #08111f 0%, #0b1324 100%);
    color: white;
}

.block-container {
    padding-top: 1.2rem;
    padding-bottom: 2rem;
    max-width: 1250px;
}

h1, h2, h3, h4, h5, h6, label, p, div, span {
    color: #f3f4f6;
}

div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div,
div[data-baseweb="textarea"] > div {
    background-color: #121c2f !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 16px !important;
    color: white !important;
}

input, textarea {
    color: white !important;
}

.stDateInput > div > div,
.stSelectbox > div > div,
.stTextInput > div > div,
.stNumberInput > div > div {
    background-color: #121c2f !important;
    border-radius: 16px !important;
}

section[data-testid="stSidebar"] {
    background: #0a1324;
}

div.stButton > button {
    background: linear-gradient(135deg, #ff4d5a 0%, #ff6a4d 100%);
    color: white;
    border: none;
    border-radius: 14px;
    padding: 0.7rem 1rem;
    font-weight: 700;
}

div.stButton > button:hover {
    filter: brightness(1.05);
}

[data-testid="stDataFrame"] {
    background-color: transparent !important;
}

.card {
    background: linear-gradient(180deg, rgba(24,35,58,0.98) 0%, rgba(19,28,47,0.98) 100%);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 26px;
    padding: 24px 24px 20px 24px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.35);
    margin-bottom: 18px;
}

.card-title {
    color: #cbd5e1;
    font-size: 16px;
    margin-bottom: 14px;
}

.card-value {
    font-size: 34px;
    font-weight: 800;
    line-height: 1.1;
}

.section-title {
    font-size: 28px;
    font-weight: 800;
    margin-top: 10px;
    margin-bottom: 18px;
}

.small-muted {
    color: #94a3b8;
    font-size: 14px;
}

.chart-box {
    background: linear-gradient(180deg, rgba(24,35,58,0.98) 0%, rgba(19,28,47,0.98) 100%);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 26px;
    padding: 18px 18px 8px 18px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.28);
    margin-top: 10px;
    margin-bottom: 18px;
}

.order-box {
    background: linear-gradient(180deg, rgba(24,35,58,0.98) 0%, rgba(19,28,47,0.98) 100%);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 26px;
    padding: 22px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.28);
    margin-top: 6px;
}
</style>
""", unsafe_allow_html=True)


# =========================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# =========================
def safe_read_excel(path: str) -> pd.DataFrame:
    try:
        return pd.read_excel(path)
    except Exception:
        return pd.DataFrame()


def parse_date_column(df: pd.DataFrame, col: str = "Дата") -> pd.DataFrame:
    if df.empty or col not in df.columns:
        return df

    df = df.copy()
    df[col] = pd.to_datetime(df[col], dayfirst=True, errors="coerce")
    return df


def format_money(value) -> str:
    try:
        value = float(value)
    except Exception:
        value = 0
    return f"{value:,.0f} ₸".replace(",", " ")


def to_numeric_safe(df: pd.DataFrame, cols: list) -> pd.DataFrame:
    df = df.copy()
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    return df


def show_card(title: str, value: str, color: str):
    st.markdown(
        f"""
        <div class="card">
            <div class="card-title">{title}</div>
            <div class="card-value" style="color:{color};">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def append_to_excel(path: str, row_df: pd.DataFrame):
    if os.path.exists(path):
        old_df = pd.read_excel(path)
        new_df = pd.concat([old_df, row_df], ignore_index=True)
    else:
        new_df = row_df.copy()

    new_df.to_excel(path, index=False)


def build_empty_fig_message(title_text: str):
    st.markdown(f"""
        <div class="chart-box">
            <div class="small-muted">{title_text}</div>
            <div style="padding:20px 4px 10px 4px; color:#94a3b8;">Нет данных для отображения</div>
        </div>
    """, unsafe_allow_html=True)


# =========================
# ЗАГРУЗКА ДАННЫХ
# =========================
sales_df = safe_read_excel(SALES_FILE)
expenses_df = safe_read_excel(EXPENSES_FILE)
orders_df = safe_read_excel(ORDERS_FILE)

sales_df = parse_date_column(sales_df, "Дата")
expenses_df = parse_date_column(expenses_df, "Дата")
orders_df = parse_date_column(orders_df, "Дата")

sales_df = to_numeric_safe(sales_df, ["Количество", "Выручка", "Прибыль", "Стас доход", "Алексей доход"])
expenses_df = to_numeric_safe(expenses_df, ["Сумма"])
orders_df = to_numeric_safe(orders_df, ["Количество", "Цена за шт", "Общая сумма"])


# =========================
# ШАПКА
# =========================
tab1, tab2 = st.tabs(["Финансовая сводка", "Создать заказ"])


# =========================================================
# TAB 1 — ФИНАНСОВАЯ СВОДКА
# =========================================================
with tab1:
    st.markdown('<div class="section-title">Финансовая сводка</div>', unsafe_allow_html=True)

    # ДАТЫ
    sales_min = sales_df["Дата"].min().date() if (not sales_df.empty and "Дата" in sales_df.columns and sales_df["Дата"].notna().any()) else date.today()
    sales_max = sales_df["Дата"].max().date() if (not sales_df.empty and "Дата" in sales_df.columns and sales_df["Дата"].notna().any()) else date.today()

    if sales_min > sales_max:
        sales_min = date.today()
        sales_max = date.today()

    col_filter1, col_filter2, col_filter3 = st.columns([1.2, 1.2, 1])

    with col_filter1:
        date_from = st.date_input("С", value=sales_min, format="DD.MM.YYYY")

    with col_filter2:
        date_to = st.date_input("По", value=sales_max if sales_max <= date.today() else date.today(), format="DD.MM.YYYY")

    with col_filter3:
        channel_options = ["Все"]
        if not sales_df.empty and "Канал" in sales_df.columns:
            existing_channels = sales_df["Канал"].dropna().astype(str).unique().tolist()
            existing_channels = sorted(existing_channels)
            channel_options += existing_channels

        selected_channel = st.selectbox("Канал", channel_options, index=0)

    # ФИЛЬТРЫ
    filtered_sales = sales_df.copy()
    filtered_expenses = expenses_df.copy()

    if not filtered_sales.empty and "Дата" in filtered_sales.columns:
        filtered_sales = filtered_sales[
            (filtered_sales["Дата"].dt.date >= date_from) &
            (filtered_sales["Дата"].dt.date <= date_to)
        ]

    if not filtered_expenses.empty and "Дата" in filtered_expenses.columns:
        filtered_expenses = filtered_expenses[
            (filtered_expenses["Дата"].dt.date >= date_from) &
            (filtered_expenses["Дата"].dt.date <= date_to)
        ]

    if selected_channel != "Все" and not filtered_sales.empty and "Канал" in filtered_sales.columns:
        filtered_sales = filtered_sales[filtered_sales["Канал"].astype(str) == selected_channel]

    # РАСЧЁТЫ
    stas_income = filtered_sales["Стас доход"].sum() if "Стас доход" in filtered_sales.columns else 0
    alexey_income = filtered_sales["Алексей доход"].sum() if "Алексей доход" in filtered_sales.columns else 0
    total_expenses = filtered_expenses["Сумма"].sum() if "Сумма" in filtered_expenses.columns else 0
    total_clean_profit = stas_income + alexey_income

    # КАРТОЧКИ
    c1, c2 = st.columns(2)
    with c1:
        show_card("Чистая прибыль", format_money(total_clean_profit), "#35e6a5")
        show_card("Стас чистый доход", format_money(stas_income), "#ffffff")
    with c2:
        show_card("Алексей чистый доход", format_money(alexey_income), "#62a8ff")
        show_card("Расходы", format_money(total_expenses), "#ff6978")

    # ГРАФИК 1 — ПРИБЫЛЬ ПО ДНЯМ
    st.markdown('<div class="section-title" style="font-size:24px;">Прибыль по дням</div>', unsafe_allow_html=True)

    if not filtered_sales.empty and "Дата" in filtered_sales.columns:
        by_day = filtered_sales.copy()
        by_day["День"] = by_day["Дата"].dt.strftime("%d.%m.%Y")

        daily = by_day.groupby("День", as_index=False)[["Стас доход", "Алексей доход"]].sum()
        daily["Итого"] = daily["Стас доход"] + daily["Алексей доход"]

        daily["ДатаСорт"] = pd.to_datetime(daily["День"], format="%d.%m.%Y", errors="coerce")
        daily = daily.sort_values("ДатаСорт")

        fig_daily = px.bar(
            daily,
            x="День",
            y="Итого",
            text="Итого",
            title=""
        )
        fig_daily.update_traces(
            texttemplate="%{text:,.0f}".replace(",", " "),
            textposition="outside",
            hovertemplate="Дата: %{x}<br>Сумма: %{y:,.0f} ₸<extra></extra>"
        )
        fig_daily.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            xaxis_title="",
            yaxis_title="",
            xaxis=dict(showgrid=False, tickangle=-25),
            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)"),
            margin=dict(l=20, r=20, t=10, b=20),
            height=420
        )

        st.markdown('<div class="chart-box">', unsafe_allow_html=True)
        st.plotly_chart(fig_daily, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        build_empty_fig_message("Прибыль по дням")

    # ГРАФИК 2 — ТОП 5 МОДЕЛЕЙ ПО ВЫРУЧКЕ
    st.markdown('<div class="section-title" style="font-size:24px;">Топ 5 моделей</div>', unsafe_allow_html=True)

    if not filtered_sales.empty and {"Модель", "Выручка"}.issubset(filtered_sales.columns):
        top_models = (
            filtered_sales.groupby("Модель", as_index=False)["Выручка"]
            .sum()
            .sort_values("Выручка", ascending=False)
            .head(5)
        )

        if not top_models.empty:
            fig_models = px.bar(
                top_models,
                x="Выручка",
                y="Модель",
                orientation="h",
                text="Выручка",
                title=""
            )
            fig_models.update_traces(
                texttemplate="%{text:,.0f}".replace(",", " "),
                textposition="outside",
                hovertemplate="Модель: %{y}<br>Выручка: %{x:,.0f} ₸<extra></extra>"
            )
            fig_models.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white"),
                xaxis_title="",
                yaxis_title="",
                yaxis=dict(categoryorder="total ascending"),
                xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)"),
                margin=dict(l=20, r=20, t=10, b=20),
                height=420
            )

            st.markdown('<div class="chart-box">', unsafe_allow_html=True)
            st.plotly_chart(fig_models, use_container_width=True, config={"displayModeBar": False})
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            build_empty_fig_message("Топ 5 моделей")
    else:
        build_empty_fig_message("Топ 5 моделей")

    # ДОП. ТАБЛИЦЫ
    with st.expander("Показать последние продажи"):
        if not filtered_sales.empty:
            show_cols = [c for c in ["Дата", "Канал", "Бренд", "Модель", "Количество", "Выручка", "Стас доход", "Алексей доход"] if c in filtered_sales.columns]
            temp_sales = filtered_sales[show_cols].copy()
            if "Дата" in temp_sales.columns:
                temp_sales["Дата"] = temp_sales["Дата"].dt.strftime("%d.%m.%Y")
            st.dataframe(temp_sales.sort_index(ascending=False), use_container_width=True, hide_index=True)
        else:
            st.info("Продаж за выбранный период нет.")

    with st.expander("Показать расходы"):
        if not filtered_expenses.empty:
            temp_exp = filtered_expenses.copy()
            if "Дата" in temp_exp.columns:
                temp_exp["Дата"] = temp_exp["Дата"].dt.strftime("%d.%m.%Y")
            st.dataframe(temp_exp, use_container_width=True, hide_index=True)
        else:
            st.info("Расходов за выбранный период нет.")


# =========================================================
# TAB 2 — СОЗДАТЬ ЗАКАЗ
# =========================================================
with tab2:
    st.markdown('<div class="section-title">Создать заказ</div>', unsafe_allow_html=True)
    st.markdown('<div class="order-box">', unsafe_allow_html=True)

    brand_options = ["Ariston", "Termex", "Edison", "Etalon", "Garanterm"]
    channel_options_order = ["ОПТ", "Kaspi", "Розница"]

    col1, col2 = st.columns(2)

    with col1:
        order_date = st.date_input("Дата заказа", value=date.today(), format="DD.MM.YYYY")
        order_channel = st.selectbox("Канал продажи", channel_options_order)
        order_brand = st.selectbox("Бренд", brand_options)
        order_model = st.text_input("Модель", placeholder="Например: ABS PRO R 80 V")

    with col2:
        order_price_type = st.selectbox("Тип цены", ["РРЦ", "Опт", "Акция", "Спеццена", "Другая"])
        order_qty = st.number_input("Количество", min_value=1, step=1, value=1)
        order_price = st.number_input("Цена за шт", min_value=0.0, step=100.0, value=0.0)
        order_comment = st.text_input("Комментарий", placeholder="Необязательно")

    total_sum = float(order_qty) * float(order_price)

    st.markdown(
        f"""
        <div class="card" style="margin-top:18px;">
            <div class="card-title">Общая сумма заказа</div>
            <div class="card-value" style="color:#35e6a5;">{format_money(total_sum)}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    save_order = st.button("Сохранить заказ", use_container_width=True)

    if save_order:
        if not order_model.strip():
            st.error("Заполни поле «Модель».")
        else:
            new_order = pd.DataFrame([{
                "Дата": pd.to_datetime(order_date),
                "Канал": order_channel,
                "Бренд": order_brand,
                "Модель": order_model.strip(),
                "Тип цены": order_price_type,
                "Количество": int(order_qty),
                "Цена за шт": float(order_price),
                "Общая сумма": float(total_sum),
                "Комментарий": order_comment.strip()
            }])

            try:
                append_to_excel(ORDERS_FILE, new_order)
                st.success("Заказ сохранён в Excel.")
            except Exception as e:
                st.error(f"Ошибка при сохранении заказа: {e}")

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title" style="font-size:24px;">Последние заказы</div>', unsafe_allow_html=True)

    latest_orders = safe_read_excel(ORDERS_FILE)
    latest_orders = parse_date_column(latest_orders, "Дата")
    latest_orders = to_numeric_safe(latest_orders, ["Количество", "Цена за шт", "Общая сумма"])

    if not latest_orders.empty:
        latest_orders_show = latest_orders.copy()
        latest_orders_show = latest_orders_show.sort_values("Дата", ascending=False)

        if "Дата" in latest_orders_show.columns:
            latest_orders_show["Дата"] = latest_orders_show["Дата"].dt.strftime("%d.%m.%Y")

        st.dataframe(latest_orders_show, use_container_width=True, hide_index=True)
    else:
        st.info("Заказов пока нет.")
