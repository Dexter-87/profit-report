import os
from datetime import date

import pandas as pd
import plotly.express as px
import streamlit as st


# =========================
# НАСТРОЙКИ
# =========================
st.set_page_config(
    page_title="Финансовая сводка",
    page_icon="📊",
    layout="wide"
)

DATA_DIR = "data"
SALES_FILE = os.path.join(DATA_DIR, "sales.xlsx")
EXPENSES_FILE = os.path.join(DATA_DIR, "expenses.xlsx")
ORDERS_FILE = os.path.join(DATA_DIR, "orders.xlsx")


# =========================
# СОЗДАНИЕ ФАЙЛОВ
# =========================
def ensure_files():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(SALES_FILE):
        pd.DataFrame(columns=[
            "Дата",
            "Канал",
            "Бренд",
            "Модель",
            "Количество",
            "Выручка",
            "Прибыль",
            "Стас доход",
            "Алексей доход",
        ]).to_excel(SALES_FILE, index=False)

    if not os.path.exists(EXPENSES_FILE):
        pd.DataFrame(columns=[
            "Дата",
            "Категория",
            "Сумма",
            "Комментарий",
        ]).to_excel(EXPENSES_FILE, index=False)

    if not os.path.exists(ORDERS_FILE):
        pd.DataFrame(columns=[
            "Дата",
            "Канал",
            "Бренд",
            "Модель",
            "Тип цены",
            "Количество",
            "Цена за шт",
            "Общая сумма",
            "Комментарий",
        ]).to_excel(ORDERS_FILE, index=False)


ensure_files()


# =========================
# СТИЛИ
# =========================
st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

.stApp {
    background: linear-gradient(180deg, #020817 0%, #03122b 100%);
    color: white;
}

.block-container {
    max-width: 1100px;
    padding-top: 1rem;
    padding-bottom: 2rem;
}

h1, h2, h3, h4, h5, h6, p, label, span, div {
    color: #f8fafc;
}

[data-testid="stTabs"] button {
    font-size: 16px;
    font-weight: 700;
}

[data-testid="stDateInput"] input,
[data-testid="stTextInput"] input,
[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
[data-testid="stTextArea"] textarea {
    background-color: #0f1b35 !important;
    color: white !important;
    border-radius: 18px !important;
}

[data-testid="stDateInput"] > div,
[data-testid="stTextInput"] > div,
[data-testid="stSelectbox"] > div,
[data-testid="stTextArea"] > div {
    border-radius: 18px !important;
}

div[data-baseweb="select"] > div {
    border: 1px solid rgba(255,255,255,0.08) !important;
    min-height: 56px !important;
}

[data-testid="stTextInput"] input,
[data-testid="stDateInput"] input {
    min-height: 56px !important;
}

[data-testid="stTextArea"] textarea {
    border: 1px solid rgba(255,255,255,0.08) !important;
    min-height: 120px !important;
}

div.stButton > button,
div[data-testid="stFormSubmitButton"] > button {
    width: 100%;
    background: linear-gradient(135deg, #ff4d5a 0%, #ff6b57 100%);
    color: white;
    border: none;
    border-radius: 18px;
    font-weight: 800;
    padding: 0.9rem 1rem;
    box-shadow: 0 10px 24px rgba(255, 90, 90, 0.25);
}

div.stButton > button:hover,
div[data-testid="stFormSubmitButton"] > button:hover {
    filter: brightness(1.05);
}

.section-title {
    font-size: 2.25rem;
    font-weight: 900;
    margin-bottom: 1rem;
    letter-spacing: -0.02em;
}

.card {
    background: linear-gradient(180deg, rgba(21,33,61,0.98) 0%, rgba(15,27,53,0.98) 100%);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 28px;
    padding: 26px 24px;
    margin-bottom: 18px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.28);
}

.card-title {
    color: #cbd5e1;
    font-size: 15px;
    margin-bottom: 14px;
}

.card-value {
    font-size: 32px;
    font-weight: 900;
    line-height: 1.1;
}

.box {
    background: linear-gradient(180deg, rgba(21,33,61,0.98) 0%, rgba(15,27,53,0.98) 100%);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 28px;
    padding: 20px;
    margin-top: 8px;
    margin-bottom: 18px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.22);
}

.small-title {
    font-size: 15px;
    color: #cbd5e1;
    margin-bottom: 10px;
}

[data-testid="stDataFrame"] {
    border-radius: 16px;
    overflow: hidden;
}

.streamlit-expanderHeader {
    font-size: 18px !important;
    font-weight: 700 !important;
}
</style>
""", unsafe_allow_html=True)


# =========================
# ФУНКЦИИ
# =========================
def read_excel_safe(path: str) -> pd.DataFrame:
    try:
        df = pd.read_excel(path)
        return df
    except Exception:
        return pd.DataFrame()


def normalize_dates(df: pd.DataFrame, col: str = "Дата") -> pd.DataFrame:
    if df.empty or col not in df.columns:
        return df
    df = df.copy()
    df[col] = pd.to_datetime(df[col], dayfirst=True, errors="coerce")
    return df


def numericize(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    if df.empty:
        return df
    df = df.copy()
    for col in cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df


def format_money(value) -> str:
    try:
        value = float(value)
    except Exception:
        value = 0
    return f"{value:,.0f} ₸".replace(",", " ")


def show_card(title: str, value: str, color: str):
    st.markdown(f"""
    <div class="card">
        <div class="card-title">{title}</div>
        <div class="card-value" style="color:{color};">{value}</div>
    </div>
    """, unsafe_allow_html=True)


def append_row_to_excel(path: str, row: dict):
    old_df = read_excel_safe(path)
    new_df = pd.concat([old_df, pd.DataFrame([row])], ignore_index=True)
    new_df.to_excel(path, index=False)


def parse_float_text(text_value: str) -> float:
    if text_value is None:
        return 0.0
    text_value = str(text_value).strip().replace(" ", "").replace(",", ".")
    if text_value == "":
        return 0.0
    try:
        return float(text_value)
    except Exception:
        return 0.0


def parse_int_text(text_value: str, default: int = 1) -> int:
    if text_value is None:
        return default
    text_value = str(text_value).strip().replace(" ", "")
    if text_value == "":
        return default
    try:
        value = int(float(text_value.replace(",", ".")))
        return max(1, value)
    except Exception:
        return default


# =========================
# ЗАГРУЗКА
# =========================
sales_df = read_excel_safe(SALES_FILE)
expenses_df = read_excel_safe(EXPENSES_FILE)
orders_df = read_excel_safe(ORDERS_FILE)

sales_df = normalize_dates(sales_df, "Дата")
expenses_df = normalize_dates(expenses_df, "Дата")
orders_df = normalize_dates(orders_df, "Дата")

sales_df = numericize(sales_df, ["Количество", "Выручка", "Прибыль", "Стас доход", "Алексей доход"])
expenses_df = numericize(expenses_df, ["Сумма"])
orders_df = numericize(orders_df, ["Количество", "Цена за шт", "Общая сумма"])


# =========================
# ВКЛАДКИ
# =========================
tab1, tab2 = st.tabs(["Финансовая сводка", "Создать заказ"])


# =====================================================
# ФИНАНСОВАЯ СВОДКА
# =====================================================
with tab1:
    st.markdown('<div class="section-title">Финансовая сводка</div>', unsafe_allow_html=True)

    if not sales_df.empty and "Дата" in sales_df.columns and sales_df["Дата"].notna().any():
        min_date = sales_df["Дата"].min().date()
        max_date = sales_df["Дата"].max().date()
    else:
        min_date = date.today()
        max_date = date.today()

    fcol1, fcol2, fcol3 = st.columns(3)

    with fcol1:
        date_from = st.date_input("С", value=min_date, format="DD.MM.YYYY", key="summary_date_from")

    with fcol2:
        date_to = st.date_input("По", value=max_date, format="DD.MM.YYYY", key="summary_date_to")

    with fcol3:
        channel_list = ["Все"]
        if not sales_df.empty and "Канал" in sales_df.columns:
            channel_values = sorted(sales_df["Канал"].dropna().astype(str).unique().tolist())
            channel_list.extend(channel_values)

        selected_channel = st.selectbox("Канал", channel_list, key="summary_channel")

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

    stas_income = filtered_sales["Стас доход"].sum() if "Стас доход" in filtered_sales.columns else 0
    alexey_income = filtered_sales["Алексей доход"].sum() if "Алексей доход" in filtered_sales.columns else 0
    total_expenses = filtered_expenses["Сумма"].sum() if "Сумма" in filtered_expenses.columns else 0
    total_clean_profit = stas_income + alexey_income

    c1, c2 = st.columns(2)
    with c1:
        show_card("Чистая прибыль", format_money(total_clean_profit), "#31e7a9")
        show_card("Стас чистый доход", format_money(stas_income), "#f8fafc")
    with c2:
        show_card("Алексей чистый доход", format_money(alexey_income), "#60a5fa")
        show_card("Расходы", format_money(total_expenses), "#ff6b7d")

    st.markdown('<div class="section-title" style="font-size: 1.9rem; margin-top: 0.8rem;">Прибыль по дням</div>', unsafe_allow_html=True)

    if not filtered_sales.empty and {"Дата", "Стас доход", "Алексей доход"}.issubset(filtered_sales.columns):
        daily_df = filtered_sales.copy()
        daily_df["День"] = daily_df["Дата"].dt.strftime("%d.%m.%Y")
        daily_group = daily_df.groupby("День", as_index=False)[["Стас доход", "Алексей доход"]].sum()
        daily_group["Итого"] = daily_group["Стас доход"] + daily_group["Алексей доход"]
        daily_group["Сорт"] = pd.to_datetime(daily_group["День"], format="%d.%m.%Y", errors="coerce")
        daily_group = daily_group.sort_values("Сорт")

        fig_daily = px.bar(
            daily_group,
            x="День",
            y="Итого",
            text="Итого"
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
            xaxis=dict(showgrid=False, tickangle=-20),
            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)"),
            margin=dict(l=10, r=10, t=10, b=10),
            height=380
        )

        st.markdown('<div class="box">', unsafe_allow_html=True)
        st.plotly_chart(fig_daily, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="box">
            <div class="small-title">Прибыль по дням</div>
            <div style="font-size:18px; color:#cbd5e1;">Нет данных для отображения</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-title" style="font-size: 1.9rem;">Топ 5 моделей</div>', unsafe_allow_html=True)

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
                text="Выручка"
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
                xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)"),
                yaxis=dict(categoryorder="total ascending"),
                margin=dict(l=10, r=10, t=10, b=10),
                height=380
            )

            st.markdown('<div class="box">', unsafe_allow_html=True)
            st.plotly_chart(fig_models, use_container_width=True, config={"displayModeBar": False})
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="box">
                <div class="small-title">Топ 5 моделей</div>
                <div style="font-size:18px; color:#cbd5e1;">Нет данных для отображения</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="box">
            <div class="small-title">Топ 5 моделей</div>
            <div style="font-size:18px; color:#cbd5e1;">Нет данных для отображения</div>
        </div>
        """, unsafe_allow_html=True)

    with st.expander("Показать последние продажи"):
        if not filtered_sales.empty:
            show_cols = [c for c in ["Дата", "Канал", "Бренд", "Модель", "Количество", "Выручка", "Стас доход", "Алексей доход"] if c in filtered_sales.columns]
            temp = filtered_sales[show_cols].copy()
            if "Дата" in temp.columns:
                temp["Дата"] = temp["Дата"].dt.strftime("%d.%m.%Y")
            st.dataframe(temp.sort_index(ascending=False), use_container_width=True, hide_index=True)
        else:
            st.info("Продаж за выбранный период нет.")

    with st.expander("Показать расходы"):
        if not filtered_expenses.empty:
            temp = filtered_expenses.copy()
            if "Дата" in temp.columns:
                temp["Дата"] = temp["Дата"].dt.strftime("%d.%m.%Y")
            st.dataframe(temp, use_container_width=True, hide_index=True)
        else:
            st.info("Расходов за выбранный период нет.")


# =====================================================
# СОЗДАТЬ ЗАКАЗ
# =====================================================
with tab2:
    st.markdown('<div class="section-title">Создать заказ</div>', unsafe_allow_html=True)

    st.markdown('<div class="box">', unsafe_allow_html=True)

    brand_options = ["Ariston", "Termex", "Edison", "Etalon", "Garanterm"]
    channel_options = ["ОПТ", "Kaspi", "Розница"]
    price_type_options = ["РРЦ", "Опт", "Акция", "Спеццена", "Другая"]

    with st.form("create_order_form", clear_on_submit=False):
        order_date = st.date_input("Дата заказа", value=date.today(), format="DD.MM.YYYY", key="order_date")
        order_channel = st.selectbox("Канал продажи", channel_options, key="order_channel")
        order_brand = st.selectbox("Бренд", brand_options, key="order_brand")
        order_model = st.text_input("Модель", placeholder="Например: ABS PRO R 80 V", key="order_model")
        order_price_type = st.selectbox("Тип цены", price_type_options, key="order_price_type")

        qty_text = st.text_input("Количество", value="1", key="order_qty")
        price_text = st.text_input("Цена за шт", value="0", key="order_price")
        order_comment = st.text_area("Комментарий", placeholder="Необязательно", key="order_comment")

        qty = parse_int_text(qty_text, default=1)
        price = parse_float_text(price_text)
        total_sum = qty * price

        st.markdown(f"""
        <div class="card" style="margin-top:8px; margin-bottom:12px;">
            <div class="card-title">Общая сумма заказа</div>
            <div class="card-value" style="color:#31e7a9;">{format_money(total_sum)}</div>
        </div>
        """, unsafe_allow_html=True)

        submitted = st.form_submit_button("Сохранить заказ")

        if submitted:
            if not str(order_model).strip():
                st.error("Заполни поле «Модель».")
            else:
                row = {
                    "Дата": pd.to_datetime(order_date),
                    "Канал": order_channel,
                    "Бренд": order_brand,
                    "Модель": str(order_model).strip(),
                    "Тип цены": order_price_type,
                    "Количество": qty,
                    "Цена за шт": price,
                    "Общая сумма": total_sum,
                    "Комментарий": str(order_comment).strip(),
                }

                try:
                    append_row_to_excel(ORDERS_FILE, row)
                    st.success("Заказ сохранён в Excel.")
                except Exception as e:
                    st.error(f"Ошибка сохранения: {e}")

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title" style="font-size: 1.9rem;">Последние заказы</div>', unsafe_allow_html=True)

    latest_orders = read_excel_safe(ORDERS_FILE)
    latest_orders = normalize_dates(latest_orders, "Дата")
    latest_orders = numericize(latest_orders, ["Количество", "Цена за шт", "Общая сумма"])

    if not latest_orders.empty:
        latest_orders = latest_orders.sort_values("Дата", ascending=False).copy()
        latest_orders_show = latest_orders.copy()

        if "Дата" in latest_orders_show.columns:
            latest_orders_show["Дата"] = latest_orders_show["Дата"].dt.strftime("%d.%m.%Y")

        st.dataframe(latest_orders_show, use_container_width=True, hide_index=True)
    else:
        st.info("Заказов пока нет.")

