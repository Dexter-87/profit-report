import os
from datetime import date, timedelta

import pandas as pd
import streamlit as st
from matplotlib import pyplot as plt
import gspread
from google.oauth2.service_account import Credentials
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
@st.cache_data(ttl=60)
def load_price():
    teeg_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTs6jLT1iBie0Fcm28dPQ_x98Pm61yDGxBnHt85bPjyAUw_144eS0HaIEuejDQwYQ/pub?gid=115078867&single=true&output=csv"
    ariston_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQIpFNDSvIXvCQ4-uSvrHyM0QqXpMO83hn2K7b2tCVGJ8hOR9R199Sd2pKwTCRvVQ/pub?gid=1662607201&single=true&output=csv"

    frames = []

    df1 = pd.read_csv(teeg_url)
    df1.columns = df1.columns.str.strip()
    frames.append(df1)

    try:
        df2 = pd.read_csv(ariston_url)
        df2.columns = df2.columns.str.strip()
        frames.append(df2)
    except Exception:
        st.warning("Прайс Ariston пока не загрузился. Проверь ссылку CSV.")

    df_all = pd.concat(frames, ignore_index=True)
    df_all.columns = df_all.columns.str.strip()
    return df_all
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

@st.cache_resource
def get_gsheet_client():
    creds_dict = dict(st.secrets["gcp_service_account"])
    credentials = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    return gspread.authorize(credentials)

def append_opt_sales_to_gsheet(df: pd.DataFrame):
    gc = get_gsheet_client()

    spreadsheet_name = st.secrets["google_sheets"]["spreadsheet_name"]
    worksheet_name = st.secrets["google_sheets"]["worksheet_name"]

    sh = gc.open(spreadsheet_name)
    ws = sh.worksheet(worksheet_name)

    rows = df.fillna("").values.tolist()
    ws.append_rows(rows, value_input_option="USER_ENTERED")

st.set_page_config(page_title="Финансовая сводка", layout="wide")

# =========================
# СТИЛИ
# =========================
st.markdown("""
<style>

/* ОСНОВА */
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

/* ЗАГОЛОВКИ */
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

/* КАРТОЧКИ */
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

/* ЦВЕТА */
.value-green { color: #34d399; }
.value-red { color: #f87171; }
.value-blue { color: #60a5fa; }

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

/* ОБЫЧНЫЕ КНОПКИ */
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

/* 🔥 КНОПКИ СКАЧИВАНИЯ (ИСПРАВЛЕНО) */
.stDownloadButton > button {
    background: #1d2330 !important;
    color: #f3f4f6 !important;
    border: 1px solid #2f3747 !important;
    border-radius: 14px !important;
    font-weight: 600 !important;
    padding: 10px 18px !important;
}

.stDownloadButton > button:hover {
    border-color: #4b5568 !important;
    color: #ffffff !important;
}

.stDownloadButton > button p {
    color: #f3f4f6 !important;
}

/* ПОЛЯ */
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

/* ВЫПАДАЮЩИЕ СПИСКИ */
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
    padding: 14px 18px !important;
}

div[data-testid="stExpander"] details[open] summary {
    border-bottom: 1px solid #2f3747 !important;
}

/* TABS */
div[data-testid="stTabs"] button {
    color: #cbd5e1 !important;
    font-weight: 700 !important;
}

div[data-testid="stTabs"] button[aria-selected="true"] {
    color: #ffffff !important;
}

/* MOBILE */
@media (max-width: 768px) {
    .block-container {
        padding-top: calc(4.2rem + env(safe-area-inset-top));
    }

    .main-title {
        font-size: 28px;
    }

    .sub-title {
        font-size: 14px;
    }

    .card-value {
        font-size: 26px;
    }
}

/* Убираем курсор в дате */


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
def build_invoice_pdf(invoice_df: pd.DataFrame) -> bytes:
    from io import BytesIO
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    buffer = BytesIO()

    base_dir = os.path.dirname(os.path.abspath(__file__))

    regular_candidates = [
        os.path.join(base_dir, "DejaVuSans.ttf"),
        os.path.join(base_dir, "fonts", "DejaVuSans.ttf"),
    ]
    bold_candidates = [
        os.path.join(base_dir, "DejaVuSans-Bold.ttf"),
        os.path.join(base_dir, "fonts", "DejaVuSans-Bold.ttf"),
    ]

    regular_font_path = next((p for p in regular_candidates if os.path.exists(p)), None)
    bold_font_path = next((p for p in bold_candidates if os.path.exists(p)), None)

    regular_font_name = "Helvetica"
    bold_font_name = "Helvetica-Bold"

    if regular_font_path:
        pdfmetrics.registerFont(TTFont("CustomFont", regular_font_path))
        regular_font_name = "CustomFont"

    if bold_font_path:
        pdfmetrics.registerFont(TTFont("CustomFont-Bold", bold_font_path))
        bold_font_name = "CustomFont-Bold"
    elif regular_font_path:
        bold_font_name = "CustomFont"

    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=10 * mm,
        rightMargin=10 * mm,
        topMargin=10 * mm,
        bottomMargin=10 * mm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        fontName=bold_font_name,
        fontSize=22,
        leading=26,
        alignment=1,
        textColor=colors.black,
        spaceAfter=8,
    )

    sub_style = ParagraphStyle(
        "SubStyle",
        parent=styles["Normal"],
        fontName=regular_font_name,
        fontSize=12,
        leading=14,
        alignment=0,
        textColor=colors.black,
        spaceAfter=10,
    )

    cell_style = ParagraphStyle(
        "CellStyle",
        parent=styles["Normal"],
        fontName=regular_font_name,
        fontSize=10,
        leading=12,
        textColor=colors.black,
    )

    cell_center = ParagraphStyle(
        "CellCenter",
        parent=cell_style,
        alignment=1,
    )

    cell_right = ParagraphStyle(
        "CellRight",
        parent=cell_style,
        alignment=2,
    )

    df = invoice_df.copy()

    needed_cols = ["Дата", "Бренд", "Модель", "Количество", "Цена", "Сумма", "Комментарий"]
    for col in needed_cols:
        if col not in df.columns:
            df[col] = ""

    df = df[needed_cols].copy()
    df["Дата"] = df["Дата"].astype(str)
    df["Бренд"] = df["Бренд"].astype(str)
    df["Модель"] = df["Модель"].astype(str)
    df["Комментарий"] = df["Комментарий"].astype(str)
    df["Количество"] = pd.to_numeric(df["Количество"], errors="coerce").fillna(0).astype(int)
    df["Цена"] = pd.to_numeric(df["Цена"], errors="coerce").fillna(0)
    df["Сумма"] = pd.to_numeric(df["Сумма"], errors="coerce").fillna(0)

    total_sum = df["Сумма"].sum()

    data = [[
        Paragraph("<b>Дата</b>", cell_style),
        Paragraph("<b>Бренд</b>", cell_style),
        Paragraph("<b>Модель</b>", cell_style),
        Paragraph("<b>Кол-во</b>", cell_center),
        Paragraph("<b>Цена</b>", cell_right),
        Paragraph("<b>Сумма</b>", cell_right),
        Paragraph("<b>Комментарий</b>", cell_style),
    ]]

    for _, row in df.iterrows():
        data.append([
            Paragraph(str(row["Дата"]), cell_style),
            Paragraph(str(row["Бренд"]), cell_style),
            Paragraph(str(row["Модель"]), cell_style),
            Paragraph(str(row["Количество"]), cell_center),
            Paragraph(f"{int(row['Цена']):,}".replace(",", " "), cell_right),
            Paragraph(f"{int(row['Сумма']):,}".replace(",", " "), cell_right),
            Paragraph(str(row["Комментарий"]), cell_style),
        ])

    data.append([
        Paragraph("<b>ИТОГО</b>", cell_style),
        "",
        "",
        "",
        "",
        Paragraph(f"<b>{int(total_sum):,}</b>".replace(",", " "), cell_right),
        "",
    ])

    col_widths = [32 * mm, 28 * mm, 78 * mm, 20 * mm, 28 * mm, 30 * mm, 42 * mm]

    table = Table(data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4F79C7")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), bold_font_name),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("LEADING", (0, 0), (-1, -1), 12),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#8A8A8A")),
        ("BACKGROUND", (0, 1), (-1, -2), colors.whitesmoke),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#DCEAF7")),
        ("SPAN", (0, -1), (4, -1)),
        ("ALIGN", (3, 1), (3, -2), "CENTER"),
        ("ALIGN", (4, 1), (5, -1), "RIGHT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))

    elements = [
        Paragraph("Королевство бойлеров", title_style),
        Paragraph(f"Накладная от {pd.Timestamp.today().strftime('%d.%m.%Y')}", sub_style),
        Spacer(1, 4),
        table,
    ]

    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf



    # =========================
# ЗАГРУЗКА
# =========================
sales_raw, expenses_raw = load_data()

base_df = load_sales_dataframe(sales_raw)
base_exp = load_expenses_dataframe(expenses_raw)

if base_df is None or base_df.empty:
    st.error("Не удалось загрузить продажи.")
    st.stop()

if "Дата" not in base_df.columns:
    st.error("В таблице продаж нет колонки 'Дата'.")
    st.write(base_df.columns.tolist())
    st.stop()

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

    st.caption("Кэш обновляется примерно раз в 60 секунд")
    st.markdown('<div class="small-label">Фильтры</div>', unsafe_allow_html=True)

    min_date = valid_dates.min().date()
    max_date = valid_dates.max().date()
    safe_today = date.today()

    channel_values = sorted([
        str(x).strip()
        for x in df["Канал"].dropna().unique().tolist()
        if str(x).strip() != ""
    ])
    channel_options = ["Все"] + channel_values

    f1, f2 = st.columns(2)

    with f1:
        selected_channel = st.selectbox(
            "Канал",
            channel_options,
            index=0,
            key="report_channel"
        )

    with f2:
        if st.button("Обновить данные", use_container_width=True, key="refresh_report"):
            st.cache_data.clear()
            st.rerun()

    if "date_from_filter" not in st.session_state:
        st.session_state["date_from_filter"] = min_date

    if "date_to_filter" not in st.session_state:
        st.session_state["date_to_filter"] = safe_today

    st.markdown("### Фильтр периода")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        if st.button("Сегодня", use_container_width=True, key="period_today"):
            st.session_state["date_from_filter"] = safe_today
            st.session_state["date_to_filter"] = safe_today
            st.rerun()

    with c2:
        if st.button("7 дней", use_container_width=True, key="period_7"):
            end_date = safe_today
            start_date = max(min_date, end_date - timedelta(days=6))
            st.session_state["date_from_filter"] = start_date
            st.session_state["date_to_filter"] = end_date
            st.rerun()

    with c3:
        if st.button("30 дней", use_container_width=True, key="period_30"):
            end_date = safe_today
            start_date = max(min_date, end_date - timedelta(days=29))
            st.session_state["date_from_filter"] = start_date
            st.session_state["date_to_filter"] = end_date
            st.rerun()

    with c4:
        if st.button("Всё", use_container_width=True, key="period_all"):
            st.session_state["date_from_filter"] = min_date
            st.session_state["date_to_filter"] = safe_today
            st.rerun()

    date_from = st.date_input(
        "С",
        key="date_from_filter",
        min_value=min_date,
        max_value=safe_today,
        format="YYYY/MM/DD"
    )

    date_to = st.date_input(
        "По",
        key="date_to_filter",
        min_value=min_date,
        max_value=safe_today,
        format="YYYY/MM/DD"
    )

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

            ax.plot(
                daily_df["Дата"],
                daily_df["Прибыль"],
                marker="o",
                color="#34d399",
                linewidth=2
            )

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
        st.markdown(
            f"""
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

            <hr style="border:0; border-top:1px solid #2f3747; margin:12px 0;">

            <div style="display:flex; justify-content:space-between; font-size:18px; font-weight:700;">
                <span style="color:#f3f4f6;">Итого</span>
                <span style="color:#34d399;">{format_money(total_net)} ₸</span>
            </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


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
# СОЗДАНИЕ ЗАКАЗА
# =========================
with tab2:

    # ===== STATE =====
    if "invoice_items" not in st.session_state:
        st.session_state.invoice_items = []

    st.markdown('<div class="main-title">Создать заказ</div>', unsafe_allow_html=True)

    price_df = load_price().fillna("")

    # чистка
    for col in ["Бренд", "Модель", "ТипЦены"]:
        if col in price_df.columns:
            price_df[col] = price_df[col].astype(str).str.strip()

    price_df["Цена"] = pd.to_numeric(price_df.get("Цена", 0), errors="coerce").fillna(0)
    price_df["Себестоимость"] = pd.to_numeric(price_df.get("Себестоимость", 0), errors="coerce").fillna(0)

    # ===== ВЫБОР =====
    brands = sorted(price_df["Бренд"].dropna().unique())
    brand = st.selectbox("Бренд", brands)

    models = price_df[price_df["Бренд"] == brand]["Модель"].dropna().unique()
    model = st.selectbox("Модель", sorted(models))

    price_types = price_df[
        (price_df["Бренд"] == brand) &
        (price_df["Модель"] == model)
    ]["ТипЦены"].dropna().unique()

    price_type = st.selectbox("Тип цены", sorted(price_types))

    selected = price_df[
        (price_df["Бренд"] == brand) &
        (price_df["Модель"] == model) &
        (price_df["ТипЦены"] == price_type)
    ]

    price = float(selected["Цена"].iloc[0]) if not selected.empty else 0
    cost = float(selected["Себестоимость"].iloc[0]) if not selected.empty else 0

    qty = st.number_input("Количество", 1, 1000, 1)

    total = price * qty

    st.write(f"💰 Цена: {format_money(price)} ₸")
    st.write(f"📦 Сумма: {format_money(total)} ₸")

    comment = st.text_input("Комментарий")

    # ===== ДОБАВИТЬ =====
    if st.button("Добавить позицию"):

        if price <= 0:
            st.warning("Нет цены")
        else:
            st.session_state.invoice_items.append({
                "Бренд": brand,
                "Модель": model,
                "Количество": qty,
                "Цена": price,
                "Сумма": total,
                "Комментарий": comment
            })
            st.rerun()

    # ===== СПИСОК =====
    st.markdown("### Позиции")

    if not st.session_state.invoice_items:
        st.info("Пусто")
    else:

        total_sum = 0

        for i, item in enumerate(st.session_state.invoice_items):

            c1, c2, c3 = st.columns([5, 2, 1])

            with c1:
                st.write(f"**{item['Модель']}**")
                st.caption(f"{format_money(item['Цена'])} ₸")

            with c2:
                new_qty = st.number_input(
                    "шт",
                    value=int(item["Количество"]),
                    key=f"qty_{i}"
                )
                item["Количество"] = new_qty
                item["Сумма"] = new_qty * item["Цена"]

            with c3:
                if st.button("🗑️", key=f"del_{i}"):
                    st.session_state.invoice_items.pop(i)
                    st.rerun()

            st.write(f"Сумма: {format_money(item['Сумма'])} ₸")
            st.markdown("---")

            total_sum += item["Сумма"]

        st.markdown(f"## Итого: {format_money(total_sum)} ₸")

    # ===== КНОПКИ =====
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Очистить"):
            st.session_state.invoice_items = []
            st.rerun()

    with col2:
        if st.button("+ Добавить в продажи (ОПТ)", use_container_width=True, key="add_invoice_to_sales"):
        if not st.session_state.invoice_items:
        st.warning("Накладная пустая")
    else:
        df_to_save = pd.DataFrame(st.session_state.invoice_items).copy()

        df_to_save["Количество"] = pd.to_numeric(
            df_to_save["Количество"], errors="coerce"
        ).fillna(1).astype(int)

        df_to_save["Цена"] = pd.to_numeric(df_to_save["Цена"], errors="coerce").fillna(0)
        df_to_save["Себестоимость"] = pd.to_numeric(df_to_save["Себестоимость"], errors="coerce").fillna(0)

        df_to_save["Дата"] = pd.Timestamp.today().strftime("%d.%m.%Y")
        df_to_save["Канал"] = "ОПТ"

        df_to_save = df_to_save.rename(columns={
            "Модель": "Наименование",
            "Цена": "РРЦ",
        })

        if "Номер заказа" not in df_to_save.columns:
            df_to_save["Номер заказа"] = ""

        if "Комментарий" not in df_to_save.columns:
            df_to_save["Комментарий"] = ""

        df_to_save["Комиссия Kaspi"] = 0

        # РРЦ и себестоимость считаем с учетом количества
        df_to_save["РРЦ"] = df_to_save["РРЦ"] * df_to_save["Количество"]
        df_to_save["Себестоимость"] = df_to_save["Себестоимость"] * df_to_save["Количество"]

        df_to_save["Чистая прибыль"] = (
            df_to_save["РРЦ"] - df_to_save["Себестоимость"] - df_to_save["Комиссия Kaspi"]
        )

        # ВАЖНО: порядок колонок должен совпадать с Google Sheets
        save_columns = [
            "Дата",
            "Канал",
            "Наименование",
            "Номер заказа",
            "РРЦ",
            "Себестоимость",
            "Комиссия Kaspi",
            "Комментарий",
            "Чистая прибыль",
        ]

        df_to_save = df_to_save[save_columns].copy()
        df_to_save["Комментарий"] = df_to_save["Комментарий"].fillna("").astype(str)

        append_opt_sales_to_gsheet(df_to_save)

        st.success("Продажи добавлены")
        st.session_state.invoice_items = []
        st.session_state.saved_invoice_ready = False
        st.session_state.invoice_pdf_bytes = None
        st.rerun()



