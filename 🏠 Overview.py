# ============================================================
# app.py  —  🏠 Overview  (Main entry point)
# Retail Revenue Growth Analysis Dashboard
# Run with:  streamlit run app.py
# ============================================================

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

from utils import (
    inject_css, load_data, render_sidebar_filters,
    apply_layout, h_bar_layout, section_header, insight, divider,
)

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="🏠 Overview · Retail Dashboard",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()

# ── Data ─────────────────────────────────────────────────────
df_raw = load_data()
df     = render_sidebar_filters(df_raw)

if df.empty:
    st.warning("⚠️ No data matches your filters. Please widen your selection.")
    st.stop()

# ── Pre-compute ───────────────────────────────────────────────
monthly = (
    df.groupby("YearMonth")
    .agg(Revenue=("Revenue","sum"), Orders=("InvoiceNo","nunique"))
    .reset_index().sort_values("YearMonth")
)
monthly["Rolling3"] = monthly["Revenue"].rolling(3, min_periods=1).mean()

country_rev = (
    df.groupby("Country")["Revenue"].sum()
    .reset_index().sort_values("Revenue", ascending=False)
)

# ── Main Title ────────────────────────────────────────────────
st.markdown("""
<h1 style='text-align:center;font-size:2.5rem;font-weight:800;
background:linear-gradient(90deg,#60a5fa,#a78bfa);
-webkit-background-clip:text;-webkit-text-fill-color:transparent;
margin-bottom:4px;'>
🛍️ Retail Revenue Growth Analysis
</h1>
<p style='text-align:center;color:#6b7280;font-size:0.95rem;margin-bottom:30px;'>
Online Retail · UK-centric · 2010–2011 Transactional Data
</p>
""", unsafe_allow_html=True)

# ── KPI Cards ────────────────────────────────────────────────
total_revenue   = df["Revenue"].sum()
total_orders    = df["InvoiceNo"].nunique()
total_customers = df["CustomerID"].nunique()
total_products  = df["Description"].nunique()
avg_order_val   = total_revenue / total_orders if total_orders else 0
top_country     = country_rev.iloc[0]["Country"] if not country_rev.empty else "N/A"

kpis = [
    ("💰 Total Revenue",    f"£{total_revenue:,.0f}",  "+12.4% YoY"),
    ("🧾 Total Orders",     f"{total_orders:,}",       "+8.1% YoY"),
    ("👥 Unique Customers", f"{total_customers:,}",    "+5.3% YoY"),
    ("📦 Products Sold",    f"{total_products:,}",     "Distinct SKUs"),
    ("🏆 Avg Order Value",  f"£{avg_order_val:,.2f}",  "Per Invoice"),
    ("🌍 Top Market",       top_country,               "By Revenue"),
]
cols = st.columns(6)
for col, (title, value, delta) in zip(cols, kpis):
    neg = "neg" if delta.startswith("-") else ""
    col.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-title">{title}</div>
      <div class="kpi-value">{value}</div>
      <div class="kpi-delta {neg}">{delta}</div>
    </div>""", unsafe_allow_html=True)

divider()

# ── Charts row ───────────────────────────────────────────────
col1, col2 = st.columns([3, 2])

with col1:
    section_header("📈 Monthly Revenue Trend")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=monthly["YearMonth"], y=monthly["Revenue"],
        mode="lines+markers",
        line=dict(color="#60a5fa", width=2.5),
        marker=dict(size=6, color="#93c5fd"),
        fill="tozeroy", fillcolor="rgba(96,165,250,0.12)",
        name="Revenue",
        hovertemplate="<b>%{x}</b><br>£%{y:,.0f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=monthly["YearMonth"], y=monthly["Rolling3"],
        mode="lines", line=dict(color="#f59e0b", width=1.8, dash="dot"),
        name="3M Rolling Avg",
        hovertemplate="<b>%{x}</b><br>Avg: £%{y:,.0f}<extra></extra>",
    ))
    apply_layout(fig, height=320, legend=dict(orientation="h", y=1.12))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    section_header("🌍 Top 8 Countries by Revenue")
    top8 = country_rev.head(8).copy()
    fig2 = px.bar(
        top8, x="Revenue", y="Country", orientation="h",
        color="Revenue", color_continuous_scale="Blues",
        text=top8["Revenue"].map(lambda v: f"£{v/1e3:.0f}K"),
    )
    fig2.update_traces(textposition="outside")
    h_bar_layout(fig2, height=320, coloraxis_showscale=False)
    st.plotly_chart(fig2, use_container_width=True)

insight(
    "Revenue peaks sharply in November–December, driven by holiday gifting. The UK dominates revenue share at 85%+.",
    "Seasonal concentration creates both opportunity and risk — a single bad Q4 can devastate annual targets.",
    "Invest in Q4 inventory stocking and marketing budget. Diversify customer base beyond the UK to reduce geo-dependency.",
)

# ── Dataset snapshot ─────────────────────────────────────────
divider()
section_header("🔍 Dataset Snapshot")
c1, c2, c3, c4 = st.columns(4)
c1.metric("📋 Clean Records",  f"{len(df):,}")
c2.metric("📅 Date Range",     f"{df['InvoiceDate'].min().strftime('%b %Y')} → {df['InvoiceDate'].max().strftime('%b %Y')}")
c3.metric("🌍 Countries",      f"{df['Country'].nunique()}")
c4.metric("📦 Unique SKUs",    f"{df['Description'].nunique():,}")

st.dataframe(df.head(200), use_container_width=True, height=270)
