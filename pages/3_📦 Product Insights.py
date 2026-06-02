# ============================================================
# pages/3_📦_Product_Insights.py
# ============================================================

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import plotly.express as px
import streamlit as st

from utils import (
    inject_css, load_data, render_sidebar_filters,
    apply_layout, h_bar_layout,
    section_header, insight,
)

st.set_page_config(
    page_title="📦 Product Insights · Retail Dashboard",
    page_icon="📦", layout="wide", initial_sidebar_state="expanded",
)
inject_css()

df_raw = load_data()
df     = render_sidebar_filters(df_raw)

if df.empty:
    st.warning("⚠️ No data matches your filters. Please widen your selection.")
    st.stop()

product_rev = (
    df.groupby("Description")["Revenue"].sum()
    .reset_index().sort_values("Revenue", ascending=False)
)

st.markdown("<h2>📦 Product Insights</h2>", unsafe_allow_html=True)
st.markdown("<p style='color:#6b7280;'>Category performance, hero SKUs, laggards, demand trends and quantity vs revenue scatter.</p>", unsafe_allow_html=True)

# ── Category Revenue Overview ─────────────────────────────
section_header("📊 Revenue by Product Category")
cat_rev = (
    df.groupby("Category")["Revenue"].sum()
    .reset_index().sort_values("Revenue", ascending=False)
)
fig0 = px.bar(
    cat_rev, x="Revenue", y="Category", orientation="h",
    color="Revenue", color_continuous_scale="Purpor",
    text=cat_rev["Revenue"].map(lambda v: f"£{v/1e3:.0f}K"),
)
fig0.update_traces(textposition="outside")
h_bar_layout(fig0, height=460, coloraxis_showscale=False)
st.plotly_chart(fig0, use_container_width=True)

insight(
    "Home Décor, Kitchen & Dining, and Gift & Wrap categories lead revenue — all gift-adjacent categories peak in Q4.",
    "Category-level analysis helps allocate buying budgets, warehouse space, and marketing spend more precisely.",
    "Increase buying budget for the top 3 categories ahead of Q4. Build category-specific landing pages for SEO.",
)

# ── Top 10 ────────────────────────────────────────────────
section_header("7 · Top 10 Products by Revenue")
top10 = product_rev.head(10).copy()
fig = px.bar(
    top10, x="Revenue", y="Description", orientation="h",
    color="Revenue", color_continuous_scale="Teal",
    text=top10["Revenue"].map(lambda v: f"£{v/1e3:.1f}K"),
)
fig.update_traces(textposition="outside")
h_bar_layout(fig, height=420, coloraxis_showscale=False)
st.plotly_chart(fig, use_container_width=True)

# ── Bottom 10 ──────────────────────────────────────────────
section_header("8 · Bottom 10 Products by Revenue")
bot10 = product_rev.tail(10).copy()
fig2 = px.bar(
    bot10, x="Revenue", y="Description", orientation="h",
    color="Revenue", color_continuous_scale="Reds",
    text=bot10["Revenue"].map(lambda v: f"£{v:.2f}"),
)
fig2.update_traces(textposition="outside")
h_bar_layout(fig2, height=420, coloraxis_showscale=False)
st.plotly_chart(fig2, use_container_width=True)

insight(
    "A handful of hero SKUs drive the majority of revenue. Hundreds of long-tail products generate almost nothing.",
    "Long-tail SKUs tie up working capital, warehouse space, and demand forecasting resources without meaningful return.",
    "Discontinue or bundle the bottom-50 SKUs. Ensure top-10 hero SKUs are permanently in stock with safety buffer.",
)

# ── Top 5 Monthly Trend ────────────────────────────────────
section_header("9 · Top 5 Products — Monthly Revenue Trend")
top5_names = product_rev.head(5)["Description"].tolist()
prod_month = (
    df[df["Description"].isin(top5_names)]
    .groupby(["YearMonth","Description"])["Revenue"].sum().reset_index()
)
fig3 = px.line(
    prod_month, x="YearMonth", y="Revenue", color="Description",
    markers=True, color_discrete_sequence=px.colors.qualitative.Bold,
)
fig3.update_traces(hovertemplate="<b>%{fullData.name}</b><br>%{x}<br>£%{y:,.0f}<extra></extra>")
apply_layout(fig3, height=400, legend=dict(orientation="h", y=1.1))
st.plotly_chart(fig3, use_container_width=True)

insight(
    "Hero products peak sharply in Q4 (Nov–Dec), confirming the gifting hypothesis. Some evergreen products maintain steady year-round sales.",
    "Knowing which SKUs are seasonal vs evergreen allows more efficient inventory planning — no overstocking in off-peak months.",
    "Tag SKUs as 'Seasonal' or 'Evergreen' in your ERP. Plan separate stock replenishment cycles for each category type.",
)

# ── Quantity vs Revenue Scatter ────────────────────────────
section_header("10 · Quantity Sold vs Revenue per Product")
prod_scatter = (
    df.groupby("Description")
    .agg(Revenue=("Revenue","sum"), Quantity=("Quantity","sum"))
    .reset_index()
)
prod_scatter = prod_scatter[(prod_scatter["Revenue"] > 0) & (prod_scatter["Quantity"] > 0)]
fig4 = px.scatter(
    prod_scatter, x="Quantity", y="Revenue",
    hover_name="Description",
    color="Revenue", size="Quantity",
    color_continuous_scale="Viridis",
    opacity=0.7, log_x=True, log_y=True,
)
fig4.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>Qty: %{x:,.0f}<br>Revenue: £%{y:,.0f}<extra></extra>"
)
apply_layout(fig4, height=440, coloraxis_showscale=False)
st.plotly_chart(fig4, use_container_width=True)

insight(
    "Most products cluster in the low-quantity, low-revenue zone. True hero products have both high volume AND high revenue — rare but critical.",
    "High-volume, low-revenue products are candidates for price increases. High-revenue, low-volume products need priority stocking.",
    "Use this scatter to identify pricing opportunities: a 5% price rise on high-volume cheap SKUs can significantly boost margin.",
)
