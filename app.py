import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Финансовая сводка", layout="wide")

# =========================
# URL ТАБЛИЦ
# =========================
PRICE_URL = "https://docs.google.com/spreadsheets/d/1a4rIkdUUNjdO21CmKNb71FctyTdr2JMq/export?format=csv&gid=115078867"

SALES_URL = "https://docs.google.com/spreadsheets/d/1D26s-VjLPvg43z-Hk38fU7Y4tPFZ9h-UfFjJzQnvtB0/gviz/tq?tqx=out:csv&gid=1240951053"

EXPENSES_URL = "https://docs.google.com/spreadsheets/d/1AuxP3Qgk-zzOVOZChdwZ1udx4A8o01k3-w8_8TfJxK0/gviz/tq?tqx=out:csv&gid=1622934317"

# =========================
# СТИЛИ (РАЗНЫЕ ДЛЯ СТРАНИЦ)
# =========================
page = st.sidebar.selectbox("Раздел", ["Финансовая сводка", "Создать заказ"])

if page == "Финансовая сводка":
    st.markdown("""
    <style>
    .stApp { background: #151922; color: #f3f4f6; }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
    .stApp { background: white; color: black; }
    </style>
    """, unsafe_allow_html=True)

# =========================
# ФУНКЦИИ
# =========================
@st.cache_data(ttl=60)
def load_csv(url):
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    return df

def format_money(x):
    return f"{int(x):,}".replace(",", " ")

def detect_brand(name):
    text = str(name).lower()
    if "ariston" in text: return "Ariston"
    if "thermex" in text: return "Thermex"
    if "edisson" in text: return "Edisson"
    if "etalon" in text: return "Etalon"
    if "garanterm" in text: return "Garanterm"
    return "Прочее"

# =========================
# СОЗДАТЬ ЗАКАЗ
# =========================
if page == "Создать заказ":

    st.title("Создать заказ")

    price_df = load_csv(PRICE_URL)

    brands = sorted(price_df["Бренд"].dropna().unique())
    brand = st.selectbox("Бренд", brands)

    df_brand = price_df[price_df["Бренд"] == brand]

    models = sorted(df_brand["Модель"].dropna().unique())
    model = st.selectbox("Модель", models)

    df_model = df_brand[df_brand["Модель"] == model]

    types = sorted(df_model["ТипЦены"].dropna().unique())
    price_type = st.selectbox("Тип цены", types)

    price = df_model[df_model["ТипЦены"] == price_type]["Цена"].values[0]

    qty = st.number_input("Количество", 1, 1000, 1)
    total = price * qty

    st.write("Цена:", format_money(price))
    st.write("Сумма:", format_money(total))

    if "cart" not in st.session_state:
        st.session_state.cart = []

    if st.button("Добавить"):
        st.session_state.cart.append({
            "Модель": model,
            "Тип": price_type,
            "Кол-во": qty,
            "Сумма": total
        })

    if st.session_state.cart:
        df_cart = pd.DataFrame(st.session_state.cart)
        st.dataframe(df_cart)

        st.write("ИТОГО:", format_money(df_cart["Сумма"].sum()))

# =========================
# ФИНАНСОВАЯ СВОДКА
# =========================
else:

    st.title("Финансовая сводка")

    sales = load_csv(SALES_URL)
    expenses = load_csv(EXPENSES_URL)

    sales["Дата"] = pd.to_datetime(sales["Дата"], errors="coerce", dayfirst=True)
    expenses["Дата"] = pd.to_datetime(expenses["Дата"], errors="coerce", dayfirst=True)

    sales = sales.dropna(subset=["Дата"])
    expenses = expenses.dropna(subset=["Дата"])

    sales["Бренд"] = sales["Наименование"].apply(detect_brand)

    min_date = sales["Дата"].min().date()
    max_date = sales["Дата"].max().date()

    col1, col2 = st.columns(2)

    with col1:
        date_from = st.date_input("С", min_date, format="DD.MM.YYYY")

    with col2:
        date_to = st.date_input("По", max_date, format="DD.MM.YYYY")

    df = sales[
        (sales["Дата"].dt.date >= date_from) &
        (sales["Дата"].dt.date <= date_to)
    ]

    exp = expenses[
        (expenses["Дата"].dt.date >= date_from) &
        (expenses["Дата"].dt.date <= date_to)
    ]

    revenue = df["РРЦ"].sum()
    profit = df["Чистая прибыль"].sum()
    cost = exp["Сумма"].sum()
    net = profit - cost

    st.write("Выручка:", format_money(revenue))
    st.write("Прибыль:", format_money(profit))
    st.write("Чистая:", format_money(net))

    # ===== ГРАФИК =====
    st.subheader("Прибыль по дням")

    chart = df.copy()
    chart["Дата"] = chart["Дата"].dt.date

    daily = chart.groupby("Дата")["Чистая прибыль"].sum().reset_index()

    fig = px.bar(daily, x="Дата", y="Чистая прибыль")

    st.plotly_chart(fig, use_container_width=True)

    # ===== ТАБЛИЦЫ =====
    st.subheader("Последние продажи")
    st.dataframe(df.tail(10))

    st.subheader("Последние расходы")
    st.dataframe(exp.tail(10))
