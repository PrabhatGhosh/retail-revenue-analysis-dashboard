# ============================================================
# pages/6_🕒_Time_Analysis.py
# ============================================================

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import plotly.express as px
import streamlit as st

from utils import (
    inject_css, load_data, render_sidebar_filters,
    apply_layout, mpl_style, PLOTLY_LAYOUT,
    section_header, insight, DAY_ORDER,
)

st.set_page_config(
    page_title="🕒 Time Analysis · Retail Dashboard",
    page_icon="🕒", layout="wide", initial_sidebar_state="expanded",
)
inject_css()

df_raw = load_data()
df     = render_sidebar_filters(df_raw)

if df.empty:
    st.warning("⚠️ No data matches your filters. Please widen your selection.")
    st.stop()

st.markdown("<h2>🕒 Time-based Analysis</h2>", unsafe_allow_html=True)
st.markdown("<p style='color:#6b7280;'>When do customers buy? Day of week, hour of day and quarterly revenue patterns.</p>", unsafe_allow_html=True)

# ── Chart 16: Day of Week ─────────────────────────────────
section_header("16 · Revenue by Day of Week")
dow = df.groupby("DayOfWeek")["Revenue"].sum().reindex(DAY_ORDER).reset_index()
dow.columns = ["Day","Revenue"]
dow.dropna(inplace=True)

mpl_style()
palette = sns.color_palette("coolwarm", len(dow))
fig, ax = plt.subplots(figsize=(10, 4.5))
bars = ax.bar(dow["Day"], dow["Revenue"], color=palette, edgecolor="#0f1117", linewidth=0.5)
ax.set_title("Revenue by Day of Week", color="#f9fafb", fontsize=13, pad=10)
ax.set_ylabel("Revenue (£)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"£{v/1e3:.0f}K"))
for bar, val in zip(bars, dow["Revenue"]):
    ax.text(
        bar.get_x() + bar.get_width() / 2, bar.get_height() + 800,
        f"£{val/1e3:.0f}K", ha="center", va="bottom", fontsize=9, color="#d1d5db",
    )
ax.grid(axis="y", alpha=0.2)
plt.tight_layout()
st.pyplot(fig)
plt.close()

insight(
    "Thursday and Wednesday are the highest revenue days. Saturday and Sunday are the lowest — a clear B2B buying pattern.",
    "B2B buyers place orders during business hours and working days. Understanding this means marketing spend at weekends is largely wasted.",
    "Schedule promotional emails and flash sale alerts for Monday–Thursday mornings. Avoid weekend campaigns for this audience.",
)

# ── Chart 17: Hour of Day ─────────────────────────────────
section_header("17 · Revenue by Hour of Day")
hourly = df.groupby("Hour")["Revenue"].sum().reset_index()
fig2 = px.area(
    hourly, x="Hour", y="Revenue",
    color_discrete_sequence=["#a78bfa"],
    labels={"Revenue": "Revenue (£)", "Hour": "Hour of Day"},
)
fig2.update_traces(
    fill="tozeroy",
    fillcolor="rgba(167,139,250,0.15)",
    hovertemplate="<b>%{x}:00</b><br>£%{y:,.0f}<extra></extra>",
)
if not hourly.empty:
    peak_hour = int(hourly.loc[hourly["Revenue"].idxmax(), "Hour"])
    fig2.add_vline(
        x=peak_hour, line_dash="dot", line_color="#fbbf24",
        annotation_text=f"⏰ Peak: {peak_hour}:00",
        annotation_font_color="#fbbf24",
    )
apply_layout(fig2, height=360)
st.plotly_chart(fig2, use_container_width=True)

insight(
    "Revenue peaks around midday (11:00–13:00) — buyers complete morning reviews and place orders before lunch. Very little revenue after 17:00.",
    "Hour-of-day patterns are critical for customer service staffing, batch processing schedules, and marketing timing.",
    "Ensure customer service is fully staffed 09:00–14:00. Schedule system maintenance and batch jobs after 18:00 only.",
)

# ── Chart 18: Quarterly Funnel ────────────────────────────
section_header("18 · Quarterly Revenue Breakdown")
quarterly = df.groupby("Quarter")["Revenue"].sum().reset_index().sort_values("Quarter")

col1, col2 = st.columns([2, 3])

with col1:
    fig3 = px.funnel(
        quarterly.sort_values("Revenue", ascending=False),
        x="Revenue", y="Quarter",
        color_discrete_sequence=["#38bdf8"],
    )
    fig3.update_layout(**PLOTLY_LAYOUT, height=360)
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    # Also show as a bar for clarity
    fig4 = px.bar(
        quarterly, x="Quarter", y="Revenue",
        color="Revenue", color_continuous_scale="Blues",
        text=quarterly["Revenue"].map(lambda v: f"£{v/1e3:.0f}K"),
    )
    fig4.update_traces(textposition="outside")
    apply_layout(fig4, height=360, coloraxis_showscale=False)
    st.plotly_chart(fig4, use_container_width=True)

insight(
    "Q4 (Oct–Dec) dominates all quarters, typically accounting for 40–50% of annual revenue. Q1 is the weakest quarter by a significant margin.",
    "A single quarter generating half the annual revenue creates dangerous operational, financial, and inventory risk.",
    "Develop a Q2/Q3 Summer Sales Strategy. Consider subscription boxes, loyalty bundles, and seasonal promotions to fill the mid-year trough.",
)
