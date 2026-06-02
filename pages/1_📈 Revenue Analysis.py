# ============================================================
# pages/1_📈_Revenue_Analysis.py
# ============================================================

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import plotly.graph_objects as go
import streamlit as st

from utils import (
    inject_css, load_data, render_sidebar_filters,
    apply_layout, mpl_style, section_header, insight,
)

st.set_page_config(
    page_title="📈 Revenue Analysis · Retail Dashboard",
    page_icon="📈", layout="wide", initial_sidebar_state="expanded",
)
inject_css()

df_raw = load_data()
df     = render_sidebar_filters(df_raw)

if df.empty:
    st.warning("⚠️ No data matches your filters. Please widen your selection.")
    st.stop()

# ── Aggregations ─────────────────────────────────────────────
monthly = (
    df.groupby("YearMonth")
    .agg(Revenue=("Revenue","sum"), Orders=("InvoiceNo","nunique"))
    .reset_index().sort_values("YearMonth")
)
monthly["GrowthPct"] = monthly["Revenue"].pct_change() * 100
monthly["Rolling3"]  = monthly["Revenue"].rolling(3, min_periods=1).mean()

# ── Page header ───────────────────────────────────────────────
st.markdown("<h2>📈 Revenue Analysis</h2>", unsafe_allow_html=True)
st.markdown("<p style='color:#6b7280;'>Trends, growth rates and rolling averages across the full data period.</p>", unsafe_allow_html=True)

# ── Chart 1: Monthly Revenue Trend ────────────────────────────
section_header("1 · Monthly Revenue Trend")
fig = go.Figure()
fig.add_trace(go.Bar(
    x=monthly["YearMonth"], y=monthly["Revenue"],
    marker_color="#3b82f6", opacity=0.75, name="Revenue",
    hovertemplate="<b>%{x}</b><br>£%{y:,.0f}<extra></extra>",
))
fig.add_trace(go.Scatter(
    x=monthly["YearMonth"], y=monthly["Rolling3"],
    mode="lines+markers", line=dict(color="#f59e0b", width=2),
    name="3M Rolling Avg",
    hovertemplate="<b>%{x}</b><br>Avg: £%{y:,.0f}<extra></extra>",
))
if not monthly.empty:
    peak = monthly.loc[monthly["Revenue"].idxmax()]
    fig.add_annotation(
        x=peak["YearMonth"], y=peak["Revenue"],
        text=f"🔺 Peak<br>£{peak['Revenue']/1e3:.0f}K",
        showarrow=True, arrowhead=2, arrowcolor="#fbbf24",
        font=dict(color="#fbbf24", size=11),
        bgcolor="#1f2937", bordercolor="#fbbf24",
    )
apply_layout(fig, height=400, legend=dict(orientation="h", y=1.1))
st.plotly_chart(fig, use_container_width=True)

insight(
    "Revenue builds steadily through the year, peaking sharply in November driven by Black Friday and Christmas gifting.",
    "Understanding the peak month helps plan inventory, logistics and staffing well in advance.",
    "Lock in supplier contracts and warehousing by September. Launch Q4 marketing in early October.",
)

# ── Chart 2: MoM Growth % ─────────────────────────────────────
section_header("2 · Month-over-Month Revenue Growth %")
growth = monthly.dropna(subset=["GrowthPct"]).copy()
growth["Color"] = growth["GrowthPct"].apply(lambda v: "#34d399" if v >= 0 else "#f87171")
fig2 = go.Figure(go.Bar(
    x=growth["YearMonth"], y=growth["GrowthPct"],
    marker_color=growth["Color"],
    text=growth["GrowthPct"].map(lambda v: f"{v:+.1f}%"),
    textposition="outside",
    hovertemplate="<b>%{x}</b><br>Growth: %{y:+.1f}%<extra></extra>",
))
fig2.add_hline(y=0, line_dash="dot", line_color="#6b7280")
apply_layout(fig2, height=360)
st.plotly_chart(fig2, use_container_width=True)

insight(
    "Oct–Nov show explosive positive growth (often 30–50%+). Dec–Jan see sharp reversals as demand collapses post-holiday.",
    "Volatile MoM growth signals unpredictable demand — hard to plan for, and risky to over-stock or under-staff.",
    "Introduce mid-year Summer Sale (Jun–Aug) to flatten the curve and generate off-peak cash flow.",
)

# ── Chart 3: Rolling Average (Matplotlib) ─────────────────────
section_header("3 · Revenue Rolling Average (3-Month Smoothed)")
mpl_style()
fig3, ax = plt.subplots(figsize=(12, 4))
x_vals = range(len(monthly))
ax.plot(x_vals, monthly["Revenue"],  color="#60a5fa", lw=1.5, alpha=0.5, label="Monthly Revenue")
ax.plot(x_vals, monthly["Rolling3"], color="#f59e0b", lw=2.5, label="3M Rolling Avg")
ax.fill_between(x_vals, monthly["Revenue"], alpha=0.1, color="#60a5fa")
step = max(1, len(monthly) // 8)
ax.set_xticks(range(0, len(monthly), step))
ax.set_xticklabels(monthly["YearMonth"].iloc[::step], rotation=45, ha="right", fontsize=8)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"£{v/1e3:.0f}K"))
ax.set_title("3-Month Rolling Average vs Monthly Revenue", color="#f9fafb", fontsize=13, pad=10)
ax.set_xlabel("Month"); ax.set_ylabel("Revenue (£)")
ax.legend(framealpha=0.2); ax.grid(True, alpha=0.2)
plt.tight_layout()
st.pyplot(fig3)
plt.close()

insight(
    "The 3-month rolling average reveals a genuine upward trend from mid-2011, confirming underlying business growth beyond seasonal noise.",
    "Rolling averages separate signal from noise — essential for honest trend reporting to executives.",
    "Use this smoothed view in board-level reports. Set quarterly revenue targets based on the rolling average, not raw monthly peaks.",
)
