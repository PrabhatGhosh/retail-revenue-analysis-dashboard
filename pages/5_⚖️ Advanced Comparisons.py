# ============================================================
# pages/5_⚖️_Advanced_Comparisons.py
# ============================================================

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from utils import (
    inject_css, load_data, render_sidebar_filters,
    mpl_style, _DARK_AXES, PLOTLY_LAYOUT,
    section_header, insight,
)

st.set_page_config(
    page_title="⚖️ Advanced Comparisons · Retail Dashboard",
    page_icon="⚖️", layout="wide", initial_sidebar_state="expanded",
)
inject_css()

df_raw = load_data()
df     = render_sidebar_filters(df_raw)

if df.empty:
    st.warning("⚠️ No data matches your filters. Please widen your selection.")
    st.stop()

st.markdown("<h2>⚖️ Advanced Comparisons</h2>", unsafe_allow_html=True)
st.markdown("<p style='color:#6b7280;'>Heatmaps, dual-axis charts and best-seller-per-month deep dives.</p>", unsafe_allow_html=True)

# ── Chart 13: Revenue Heatmap ─────────────────────────────
section_header("13 · Revenue Heatmap — Month × Year")
heat = df.groupby(["Year","Month"])["Revenue"].sum().reset_index()
if not heat.empty:
    heat_pivot = heat.pivot(index="Year", columns="Month", values="Revenue").fillna(0)
    month_labels = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    heat_pivot.columns = [month_labels[m - 1] for m in heat_pivot.columns]
    mpl_style()
    fig, ax = plt.subplots(figsize=(13, max(3, len(heat_pivot) * 1.7)))
    sns.heatmap(
        heat_pivot, annot=True, fmt=".0f",
        cmap="YlOrRd", linewidths=0.4, linecolor="#0f1117",
        ax=ax, cbar_kws={"shrink": 0.7}, annot_kws={"size": 9},
    )
    ax.set_title("Monthly Revenue Heatmap (£)", color="#f9fafb", fontsize=13, pad=10)
    ax.set_xlabel("Month"); ax.set_ylabel("Year")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()
else:
    st.info("Not enough data to generate heatmap.")

insight(
    "November 2011 is the single hottest cell — the clearest visual proof of holiday-driven demand concentration.",
    "Heatmaps expose temporal patterns that line charts miss — they make seasonality risk undeniable to any stakeholder.",
    "Show this heatmap in your next board presentation. Pre-position stock and staff by September every year.",
)

# ── Chart 14: Orders vs Customers (dual axis) ─────────────
section_header("14 · Orders vs Unique Customers — Monthly")
oc = df.groupby("YearMonth").agg(
    Orders   =("InvoiceNo",   "nunique"),
    Customers=("CustomerID",  "nunique"),
).reset_index()

fig2 = make_subplots(specs=[[{"secondary_y": True}]])
fig2.add_trace(go.Bar(
    x=oc["YearMonth"], y=oc["Orders"],
    name="Orders", marker_color="#818cf8", opacity=0.8,
    hovertemplate="<b>%{x}</b><br>Orders: %{y:,}<extra></extra>",
), secondary_y=False)
fig2.add_trace(go.Scatter(
    x=oc["YearMonth"], y=oc["Customers"],
    name="Customers", mode="lines+markers",
    line=dict(color="#f59e0b", width=2.5),
    hovertemplate="<b>%{x}</b><br>Customers: %{y:,}<extra></extra>",
), secondary_y=True)
fig2.update_layout(**PLOTLY_LAYOUT, height=400, legend=dict(orientation="h", y=1.1))
fig2.update_xaxes(**_DARK_AXES)
fig2.update_yaxes(title_text="📦 Orders",    secondary_y=False, **_DARK_AXES)
fig2.update_yaxes(title_text="👥 Customers", secondary_y=True,  **_DARK_AXES)
st.plotly_chart(fig2, use_container_width=True)

insight(
    "Orders and customers track each other very closely — meaning most customers place roughly one order per period with minimal repeat purchasing within the same month.",
    "A low orders-per-customer ratio signals missed upselling and cross-selling opportunities.",
    "Introduce 'Frequently Bought Together' widgets. Send a follow-up email 14 days after purchase with related products.",
)

# ── Table 15: Best-seller per month ───────────────────────
section_header("15 · Best-Selling Product Each Month")
best_per_month = (
    df.groupby(["YearMonth","Description"])["Revenue"].sum().reset_index()
    .sort_values(["YearMonth","Revenue"], ascending=[True,False])
    .groupby("YearMonth").first().reset_index()
    .rename(columns={"Revenue": "Top Revenue (£)"})
)
best_per_month["Top Revenue (£)"] = best_per_month["Top Revenue (£)"].map("£{:,.0f}".format)
st.dataframe(best_per_month, use_container_width=True, height=400)

insight(
    "The best-selling product changes month to month — but holiday-themed items dominate in Q4 while storage and home items lead in the quieter months.",
    "Knowing the monthly champion SKU helps in marketing — a targeted campaign around the hero product of the month can amplify sales further.",
    "Build a 'Product of the Month' campaign. Feature the predicted monthly champion SKU on the homepage and in email headers.",
)
