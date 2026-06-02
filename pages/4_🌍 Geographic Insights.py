# ============================================================
# pages/4_🌍_Geographic_Insights.py
# ============================================================

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from utils import (
    inject_css, load_data, render_sidebar_filters,
    apply_layout, section_header, insight,
    normalise_country, GEO_STYLE,
)

st.set_page_config(
    page_title="🌍 Geographic Insights · Retail Dashboard",
    page_icon="🌍", layout="wide", initial_sidebar_state="expanded",
)
inject_css()

df_raw = load_data()
df     = render_sidebar_filters(df_raw)

if df.empty:
    st.warning("⚠️ No data matches your filters. Please widen your selection.")
    st.stop()

country_rev = (
    df.groupby("Country")["Revenue"].sum()
    .reset_index().sort_values("Revenue", ascending=False)
)

# Build normalised country dataframe for choropleth
country_plot = country_rev.copy()
country_plot["PlotName"] = country_plot["Country"].apply(normalise_country)
country_plot = country_plot.dropna(subset=["PlotName"])
country_plot = (
    country_plot.groupby("PlotName", as_index=False)["Revenue"].sum()
    .sort_values("Revenue", ascending=False)
)

st.markdown("<h2>🌍 Geographic Insights</h2>", unsafe_allow_html=True)
st.markdown("<p style='color:#6b7280;'>World revenue map, market concentration and country ranking comparisons.</p>", unsafe_allow_html=True)

# ── Chart 11: Choropleth maps ─────────────────────────────
section_header("11 · Country-wise Revenue — World Map")

map_tab1, map_tab2 = st.tabs(["🌐 All Countries (log scale)", "🇪🇺 Excluding UK (other markets)"])

with map_tab1:
    plot_all = country_plot.copy()
    plot_all["LogRevenue"] = np.log1p(plot_all["Revenue"])
    fig_map1 = px.choropleth(
        plot_all,
        locations="PlotName", locationmode="country names",
        color="LogRevenue",
        hover_name="PlotName",
        hover_data={"Revenue": ":,.0f", "LogRevenue": False},
        color_continuous_scale="Blues",
        labels={"LogRevenue": "Revenue (log scale)"},
    )
    fig_map1.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        geo=GEO_STYLE,
        coloraxis_colorbar=dict(title="Revenue (log £)", tickfont=dict(color="#9ca3af")),
        margin=dict(t=10, b=0, l=0, r=0),
        height=460,
        font=dict(color="#d1d5db"),
    )
    st.plotly_chart(fig_map1, use_container_width=True)
    st.caption("📌 Log scale used so smaller markets remain visible alongside the dominant UK.")

with map_tab2:
    plot_exuk = country_plot[country_plot["PlotName"] != "United Kingdom"].copy()
    fig_map2 = px.choropleth(
        plot_exuk,
        locations="PlotName", locationmode="country names",
        color="Revenue",
        hover_name="PlotName",
        hover_data={"Revenue": ":,.0f"},
        color_continuous_scale="Teal",
        labels={"Revenue": "Revenue (£)"},
    )
    fig_map2.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        geo=GEO_STYLE,
        coloraxis_colorbar=dict(title="Revenue (£)", tickfont=dict(color="#9ca3af")),
        margin=dict(t=10, b=0, l=0, r=0),
        height=460,
        font=dict(color="#d1d5db"),
    )
    st.plotly_chart(fig_map2, use_container_width=True)
    st.caption("📌 UK excluded so the colour scale reveals the relative strength of European and global markets.")

insight(
    "UK dominates with 85%+ of revenue. Germany, France, Ireland (EIRE → normalised), and Netherlands show the strongest international demand. RSA normalised to South Africa.",
    "Extreme geographic concentration is a single-point-of-failure: any UK economic shock, regulatory change or logistics disruption can devastate revenue.",
    "Launch EU-localised marketing in Germany and Netherlands first — they already have organic traction. Add local-currency checkout and domestic delivery partners.",
)

# ── Chart 12: Top 5 vs Bottom 5 ───────────────────────────
section_header("12 · Top 5 vs Bottom 5 Countries by Revenue")
top5c = country_rev.head(5)
bot5c = country_rev.tail(5)
compare = pd.concat([top5c.assign(Group="🟢 Top 5"), bot5c.assign(Group="🔴 Bottom 5")])
fig_cmp = px.bar(
    compare, x="Country", y="Revenue", color="Group",
    barmode="group",
    color_discrete_map={"🟢 Top 5":"#34d399","🔴 Bottom 5":"#f87171"},
    text=compare["Revenue"].map(lambda v: f"£{v/1e3:.1f}K"),
)
fig_cmp.update_traces(textposition="outside")
apply_layout(fig_cmp, height=400)
st.plotly_chart(fig_cmp, use_container_width=True)

insight(
    "The revenue gap between top and bottom countries is staggering — top 5 generate thousands of times more than the bottom 5.",
    "Maintaining market presence in micro-revenue countries may cost more in ops overhead than the revenue justifies.",
    "Introduce a minimum order threshold (e.g. £100) for international markets. Exit or automate the bottom-5 to free up resource.",
)

# ── Full country table ─────────────────────────────────────
section_header("🗺️ Country Revenue Breakdown (Full Table)")
cr_display = country_rev.copy()
cr_display["Revenue Share %"] = (cr_display["Revenue"] / cr_display["Revenue"].sum() * 100).round(2)
cr_display["Revenue (£)"] = cr_display["Revenue"].map("£{:,.2f}".format)
cr_display = cr_display[["Country","Revenue (£)","Revenue Share %"]]
st.dataframe(cr_display, use_container_width=True)
