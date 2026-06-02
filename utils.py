# ============================================================
# utils.py  —  Shared helpers for Retail Revenue Dashboard
# Every page imports from here — single source of truth.
# ============================================================

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

# ─────────────────────────────────────────────────────────────
# GLOBAL CSS  (injected by every page via inject_css())
# ─────────────────────────────────────────────────────────────
CSS = """
<style>
[data-testid="stAppViewContainer"] { background:#0f1117; color:#e0e0e0; }
[data-testid="stSidebar"]          { background:#161b22; border-right:1px solid #30363d; }

.kpi-card {
    background:linear-gradient(135deg,#1f2937 0%,#111827 100%);
    border:1px solid #374151; border-radius:14px;
    padding:22px 20px 18px 20px; text-align:center;
    box-shadow:0 4px 20px rgba(0,0,0,0.4); transition:transform 0.2s;
}
.kpi-card:hover { transform:translateY(-3px); }
.kpi-title  { font-size:0.78rem; color:#9ca3af; letter-spacing:0.08em; text-transform:uppercase; }
.kpi-value  { font-size:2.0rem; font-weight:700; color:#f9fafb; margin:6px 0 2px 0; }
.kpi-delta  { font-size:0.82rem; color:#34d399; }
.kpi-delta.neg { color:#f87171; }

.section-header {
    font-size:1.35rem; font-weight:700; color:#60a5fa;
    border-left:4px solid #3b82f6; padding-left:12px; margin:28px 0 16px 0;
}
.insight-box {
    background:#1e293b; border-left:4px solid #38bdf8; border-radius:8px;
    padding:16px 20px; margin:14px 0 22px 0; font-size:0.9rem;
    line-height:1.7; color:#cbd5e1;
}
.insight-box b  { color:#f0f9ff; }
.custom-divider { border:none; border-top:1px solid #1f2937; margin:30px 0; }

h1,h2,h3 { color:#f9fafb !important; }
[data-testid="stMetricValue"] { font-size:1.6rem !important; }
.stDataFrame { border-radius:10px; }
</style>
"""

def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# PLOTLY DARK THEME HELPERS
# _DARK_AXES kept separate from PLOTLY_LAYOUT to avoid the
# "multiple values for keyword argument 'yaxis'" collision.
# ─────────────────────────────────────────────────────────────
_DARK_AXES = dict(gridcolor="#1f2937", linecolor="#374151")

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#d1d5db", family="Inter, sans-serif"),
    title_font=dict(size=15, color="#f9fafb"),
    margin=dict(t=55, b=40, l=40, r=20),
)

def apply_layout(fig, **extra):
    """Apply dark Plotly theme. xaxis/yaxis applied via update_* to avoid collision."""
    fig.update_layout(**PLOTLY_LAYOUT, **extra)
    try:
        fig.update_xaxes(**_DARK_AXES)
        fig.update_yaxes(**_DARK_AXES)
    except Exception:
        pass
    return fig

def h_bar_layout(fig, height=400, reverse_y=True, **extra):
    """Dark-theme layout for horizontal bar charts with safe y-axis reversal."""
    fig.update_layout(**PLOTLY_LAYOUT, height=height, **extra)
    fig.update_xaxes(**_DARK_AXES)
    fig.update_yaxes(autorange="reversed" if reverse_y else True, **_DARK_AXES)
    return fig


# ─────────────────────────────────────────────────────────────
# MATPLOTLIB DARK STYLE
# ─────────────────────────────────────────────────────────────
def mpl_style():
    plt.style.use("dark_background")
    plt.rcParams.update({
        "axes.facecolor":   "#111827",
        "figure.facecolor": "#0f1117",
        "axes.edgecolor":   "#374151",
        "grid.color":       "#1f2937",
        "text.color":       "#d1d5db",
        "xtick.color":      "#9ca3af",
        "ytick.color":      "#9ca3af",
    })


# ─────────────────────────────────────────────────────────────
# UI COMPONENT HELPERS
# ─────────────────────────────────────────────────────────────
def section_header(title: str):
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)

def insight(what: str, why: str, action: str):
    st.markdown(f"""
    <div class="insight-box">
    📌 <b>What is happening?</b><br>{what}<br><br>
    💡 <b>Why it matters?</b><br>{why}<br><br>
    🚀 <b>Business Action / Recommendation</b><br>{action}
    </div>""", unsafe_allow_html=True)

def divider():
    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# COUNTRY NAME NORMALISATION
# Maps dataset names → Plotly ISO-recognised country names
# ─────────────────────────────────────────────────────────────
COUNTRY_NAME_MAP = {
    "EIRE":               "Ireland",
    "Channel Islands":    "United Kingdom",
    "RSA":                "South Africa",
    "European Community": None,
    "Unspecified":        None,
    "USA":                "United States",
    "Czech Republic":     "Czechia",
}

def normalise_country(name: str):
    return COUNTRY_NAME_MAP.get(name, name)


# ─────────────────────────────────────────────────────────────
# KEYWORD-BASED PRODUCT CATEGORY MAP
# ─────────────────────────────────────────────────────────────
CATEGORY_KEYWORDS = {
    "🕯️ Candles & Lighting":   ["candle","lantern","t-light","tlight","light","lamp","fairy","bulb","holder"],
    "🌸 Floral & Garden":      ["flower","floral","garden","plant","pot","watering","daisy","rose","botanical"],
    "🎁 Gift & Wrap":          ["gift","wrap","ribbon","tag","card","package","voucher","tissue"],
    "🧸 Toys & Games":         ["toy","game","puzzle","doll","teddy","bear","play","ball","magic","kid","children"],
    "🍴 Kitchen & Dining":     ["kitchen","mug","cup","tea","coffee","plate","bowl","jar","tin","biscuit","cake","spoon","fork"],
    "🛁 Bath & Fragrance":     ["bath","soap","fragrance","scent","aroma","incense","perfume","diffuser","lotion"],
    "👜 Bags & Accessories":   ["tote","purse","pouch","wallet","satchel","handbag","shopper","rucksack","backpack"],
    "💍 Jewellery":            ["necklace","bracelet","earring","ring","bead","pendant","charm","crystal","jewel","locket"],
    "🏠 Home Décor":           ["frame","clock","mirror","cushion","doorstop","doormat","rug","curtain","hook","hanger","shelf"],
    "🎄 Seasonal & Christmas": ["christmas","xmas","advent","santa","snowman","reindeer","festive","holiday","easter","halloween"],
    "📦 Storage & Organising": ["cabinet","drawer","organis","storage","basket","tray","crate","rack"],
    "🖊️ Stationery & Books":   ["book","notebook","journal","diary","pen","pencil","stationery","pad","note"],
    "🎨 Art & Craft":          ["paint","canvas","craft","draw","sew","knit","stamp","kit","embroidery"],
    "🐾 Animal & Nature":      ["bird","cat","dog","animal","owl","fox","rabbit","elephant","butterfly","bee","hedgehog","horse"],
    "😄 Novelty & Retro":      ["retro","vintage","novelty","fun","cute","quirky","humour","funny","joke"],
}

@st.cache_data(show_spinner=False)
def build_category_map(descriptions: tuple) -> dict:
    """Assign each product description to a category via keyword matching."""
    cat_map = {}
    for desc in descriptions:
        d = desc.lower()
        found = "🗂️ Other"
        for cat, keywords in CATEGORY_KEYWORDS.items():
            if any(kw in d for kw in keywords):
                found = cat
                break
        cat_map[desc] = found
    return cat_map


# ─────────────────────────────────────────────────────────────
# DATA LOADING & CLEANING
# ─────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="🔄 Loading & cleaning data …")
def load_data() -> pd.DataFrame:
    df = pd.read_csv(
        "Online Retail Data Set.csv",
        encoding="latin-1",
        dtype={"CustomerID": str},
    )
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], dayfirst=True, errors="coerce")
    df.dropna(subset=["InvoiceDate", "CustomerID"], inplace=True)
    df = df[~df["InvoiceNo"].astype(str).str.startswith("C")]
    df = df[(df["Quantity"] > 0) & (df["UnitPrice"] > 0)]
    df["Revenue"]     = df["Quantity"] * df["UnitPrice"]
    df["Year"]        = df["InvoiceDate"].dt.year
    df["Month"]       = df["InvoiceDate"].dt.month
    df["MonthName"]   = df["InvoiceDate"].dt.strftime("%b")
    df["YearMonth"]   = df["InvoiceDate"].dt.to_period("M").astype(str)
    df["DayOfWeek"]   = df["InvoiceDate"].dt.day_name()
    df["Hour"]        = df["InvoiceDate"].dt.hour
    df["Quarter"]     = df["InvoiceDate"].dt.to_period("Q").astype(str)
    df["Description"] = df["Description"].str.strip().str.title()
    # Attach product categories
    all_desc         = tuple(sorted(df["Description"].dropna().unique()))
    cat_map          = build_category_map(all_desc)
    df["Category"]   = df["Description"].map(cat_map)
    return df


# ─────────────────────────────────────────────────────────────
# SIDEBAR FILTERS  (called from every page)
# Returns: (df_filtered, df_raw) so pages can use both
# ─────────────────────────────────────────────────────────────
def render_sidebar_filters(df_raw: pd.DataFrame):
    """
    Renders the shared sidebar logo, navigation hint, and all filters.
    Returns the filtered dataframe.
    """
    with st.sidebar:
        st.markdown("## 🛍️ Retail Dashboard")
        st.markdown("*Navigate using the Pages menu above ↑*")
        st.markdown("---")
        st.markdown("### 🎛️ Filters")

        # ── Date range ──
        min_date = df_raw["InvoiceDate"].min().date()
        max_date = df_raw["InvoiceDate"].max().date()
        date_range = st.date_input(
            "📅 Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )

        # ── Country ──
        all_countries = sorted(df_raw["Country"].dropna().unique())
        selected_countries = st.multiselect(
            "🌍 Country", all_countries,
            default=all_countries,
            placeholder="All countries",
        )

        # ── 2-step product filter ──
        st.markdown("**📦 Product Filter (2-step)**")
        all_cats = sorted(df_raw["Category"].dropna().unique())
        selected_cats = st.multiselect(
            "🗂️ Step 1 — Category",
            options=all_cats,
            placeholder="All categories (leave blank = all)",
            help="Pick a category to narrow Step 2",
        )

        if selected_cats:
            avail_prods = sorted(
                df_raw[df_raw["Category"].isin(selected_cats)]["Description"].dropna().unique()
            )
            step2_label = f"🔍 Step 2 — Product ({len(avail_prods)} available)"
        else:
            avail_prods = sorted(df_raw["Description"].dropna().unique())
            step2_label = "🔍 Step 2 — Product (pick category first)"

        selected_products = st.multiselect(
            step2_label,
            options=avail_prods,
            placeholder="All products (leave blank = all)",
        )

        # ── Revenue floor ──
        rev_range = st.slider(
            "💰 Min Order Revenue (£)",
            min_value=0.0, max_value=500.0, value=0.0, step=5.0,
        )

        st.markdown("---")
        st.caption("📊 TATA Online Retail Dataset")

    # ── Apply filters ──
    df = df_raw.copy()

    if len(date_range) == 2:
        s, e = date_range
        df = df[(df["InvoiceDate"].dt.date >= s) & (df["InvoiceDate"].dt.date <= e)]

    if selected_countries:
        df = df[df["Country"].isin(selected_countries)]

    if selected_cats and not selected_products:
        df = df[df["Category"].isin(selected_cats)]

    if selected_products:
        df = df[df["Description"].isin(selected_products)]

    if rev_range > 0:
        inv_rev = df.groupby("InvoiceNo")["Revenue"].sum()
        df = df[df["InvoiceNo"].isin(inv_rev[inv_rev >= rev_range].index)]

    return df


# ─────────────────────────────────────────────────────────────
# RFM SEGMENTATION  (shared by Customer & Final pages)
# ─────────────────────────────────────────────────────────────
def compute_rfm(df: pd.DataFrame) -> pd.DataFrame:
    snapshot = df["InvoiceDate"].max() + pd.Timedelta(days=1)
    rfm = (
        df.groupby("CustomerID").agg(
            Recency  =("InvoiceDate", lambda x: (snapshot - x.max()).days),
            Frequency=("InvoiceNo",   "nunique"),
            Monetary =("Revenue",     "sum"),
        ).reset_index()
    )
    def _seg(row):
        if row["Recency"] <= 30  and row["Frequency"] >= 5: return "Champions"
        if row["Recency"] <= 90  and row["Frequency"] >= 3: return "Loyal"
        if row["Recency"] <= 180:                           return "At Risk"
        return "Lost"
    rfm["Segment"] = rfm.apply(_seg, axis=1)
    return rfm


# ─────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────
DAY_ORDER = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

GEO_STYLE = dict(
    bgcolor="rgba(15,17,23,1)",
    showland=True,       landcolor="#1f2937",
    showocean=True,      oceancolor="#0d1b2a",
    showcoastlines=True, coastlinecolor="#4b5563",
    showframe=False,
    showlakes=True,      lakecolor="#0d1b2a",
    projection_type="natural earth",
)
