import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings("ignore")

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Veridi Logistics — Delivery Audit",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Brand palette ─────────────────────────────────────────────────────────────
NAVY  = "#0A2342"
TEAL  = "#1B9AAA"
AMBER = "#F4A261"
RED   = "#E63946"
GREEN = "#2DC653"
SLATE = "#64748B"

STATUS_COLORS = {"On Time": GREEN, "Late": AMBER, "Super Late": RED}
REGION_COLORS = {"Core": TEAL, "North/Remote": RED}

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
  html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}

  /* Sidebar */
  [data-testid="stSidebar"] {{
    background: {NAVY} !important;
    border-right: 2px solid {TEAL};
  }}
  [data-testid="stSidebar"] * {{ color: #e0eef5 !important; }}
  [data-testid="stSidebar"] .stSelectbox label,
  [data-testid="stSidebar"] .stMultiSelect label {{ color: {TEAL} !important; font-weight: 600; }}

  /* Top header bar */
  .top-bar {{
    background: linear-gradient(135deg, {NAVY} 0%, #0e3565 100%);
    padding: 22px 32px 18px;
    border-radius: 12px;
    margin-bottom: 22px;
    border-bottom: 3px solid {TEAL};
  }}
  .top-bar h1 {{ color: white; font-size: 1.9rem; font-weight: 800; margin: 0; }}
  .top-bar p  {{ color: #8bbdd4; font-size: 0.88rem; margin: 4px 0 0; }}

  /* KPI cards */
  .kpi-grid {{ display: flex; gap: 14px; margin-bottom: 22px; flex-wrap: wrap; }}
  .kpi-card {{
    flex: 1; min-width: 150px;
    background: white;
    border-radius: 10px;
    padding: 16px 20px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.07);
    border-top: 4px solid {TEAL};
  }}
  .kpi-card.green {{ border-top-color: {GREEN}; }}
  .kpi-card.amber {{ border-top-color: {AMBER}; }}
  .kpi-card.red   {{ border-top-color: {RED};   }}
  .kpi-label {{ font-size: 0.7rem; font-weight: 700; text-transform: uppercase;
                letter-spacing: 0.8px; color: {SLATE}; margin-bottom: 6px; }}
  .kpi-value {{ font-size: 1.85rem; font-weight: 800; color: {NAVY}; line-height: 1; }}
  .kpi-sub   {{ font-size: 0.72rem; color: #94a3b8; margin-top: 5px; }}

  /* Section title */
  .sec-title {{
    font-size: 0.72rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 1px; color: {TEAL};
    border-left: 3px solid {TEAL}; padding-left: 10px;
    margin: 22px 0 12px;
  }}

  /* Chart cards */
  .chart-card {{
    background: white; border-radius: 10px;
    padding: 18px; box-shadow: 0 2px 10px rgba(0,0,0,0.07);
    margin-bottom: 16px;
  }}
  .chart-title {{
    font-size: 0.85rem; font-weight: 700; color: {NAVY};
    margin-bottom: 4px;
  }}
  .chart-sub {{
    font-size: 0.72rem; color: {SLATE}; margin-bottom: 12px;
  }}

  /* Insight box */
  .insight {{
    background: #e8f7f9; border: 1px solid {TEAL};
    border-radius: 8px; padding: 12px 16px;
    font-size: 0.82rem; color: #0d5c66; margin-top: 10px;
  }}
  .insight strong {{ color: {NAVY}; }}

  /* Tab styling */
  .stTabs [data-baseweb="tab-list"] {{
    background: {NAVY}; border-radius: 8px 8px 0 0; padding: 4px 8px 0;
    gap: 4px;
  }}
  .stTabs [data-baseweb="tab"] {{
    color: #8bbdd4 !important; border-radius: 6px 6px 0 0;
    font-weight: 600; font-size: 0.82rem;
    padding: 8px 18px;
  }}
  .stTabs [aria-selected="true"] {{
    background: {TEAL} !important; color: white !important;
  }}
  div[data-testid="stMetric"] {{ display: none; }}
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# DATA LOADING
# ════════════════════════════════════════════════════════════════════════════════
@st.cache_data
def load_data():
    delivered = pd.read_csv("veridi_delivered_clean.csv", parse_dates=[
        "order_purchase_timestamp",
        "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ])
    state_df  = pd.read_csv("veridi_state_summary.csv")
    cat_df    = pd.read_csv("veridi_category_summary.csv")
    return delivered, state_df, cat_df

delivered, state_df, cat_df = load_data()

# Derived columns
delivered["month"] = delivered["order_purchase_timestamp"].dt.to_period("M").astype(str)
delivered["year"]  = delivered["order_purchase_timestamp"].dt.year.astype(str)


# ════════════════════════════════════════════════════════════════════════════════
# SIDEBAR FILTERS
# ════════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"""
    <div style='text-align:center; padding: 10px 0 18px;'>
      <div style='font-size:2rem;'>🚚</div>
      <div style='font-size:1rem; font-weight:800; color:white;'>Veridi Logistics</div>
      <div style='font-size:0.72rem; color:{TEAL}; letter-spacing:1px;'>DELIVERY AUDIT DASHBOARD</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f"<div style='font-size:0.75rem;font-weight:700;color:{TEAL};letter-spacing:1px;margin-bottom:8px;'>FILTERS</div>", unsafe_allow_html=True)

    all_statuses = ["On Time", "Late", "Super Late"]
    sel_status = st.multiselect(
        "Delivery Status",
        options=all_statuses,
        default=all_statuses
    )

    all_regions = sorted(delivered["Region_Type"].unique())
    sel_region = st.multiselect(
        "Region Type",
        options=all_regions,
        default=all_regions
    )

    all_states = sorted(delivered["customer_state"].unique())
    sel_states = st.multiselect(
        "States (leave blank = all)",
        options=all_states,
        default=[]
    )

    score_range = st.slider("Review Score Range", 1, 5, (1, 5))

    st.markdown("---")
    st.markdown(f"""
    <div style='font-size:0.7rem; color:#5a8fa8; padding: 8px 0;'>
      Dataset: Olist Brazilian E-Commerce<br>
      Orders analysed: <b style='color:{TEAL};'>{len(delivered):,}</b><br>
      Period: 2017 – 2018
    </div>
    """, unsafe_allow_html=True)

# ── Apply filters ─────────────────────────────────────────────────────────────
df = delivered.copy()
if sel_status:
    df = df[df["Delivery_Status"].isin(sel_status)]
if sel_region:
    df = df[df["Region_Type"].isin(sel_region)]
if sel_states:
    df = df[df["customer_state"].isin(sel_states)]
df = df[df["review_score"].between(score_range[0], score_range[1])]


# ════════════════════════════════════════════════════════════════════════════════
# TOP HEADER
# ════════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="top-bar">
  <h1>🚚 Veridi Logistics — Last Mile Delivery Audit</h1>
  <p>Olist Brazilian E-Commerce Dataset &nbsp;·&nbsp; {len(df):,} orders shown &nbsp;·&nbsp; 2017–2018</p>
</div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# KPI CARDS
# ════════════════════════════════════════════════════════════════════════════════
total      = len(df)
on_time_n  = (df["Delivery_Status"] == "On Time").sum()
late_n     = (df["Delivery_Status"] == "Late").sum()
super_n    = (df["Delivery_Status"] == "Super Late").sum()
on_time_p  = on_time_n / total * 100 if total else 0
late_p     = late_n    / total * 100 if total else 0
super_p    = super_n   / total * 100 if total else 0
avg_score  = df["review_score"].mean()
avg_delay  = df["Days_Difference"].mean()

k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    st.markdown(f"""<div class="kpi-card">
      <div class="kpi-label">Total Orders</div>
      <div class="kpi-value">{total:,}</div>
      <div class="kpi-sub">filtered selection</div>
    </div>""", unsafe_allow_html=True)
with k2:
    st.markdown(f"""<div class="kpi-card green">
      <div class="kpi-label">On-Time Rate</div>
      <div class="kpi-value" style="color:{GREEN};">{on_time_p:.1f}%</div>
      <div class="kpi-sub">{on_time_n:,} orders</div>
    </div>""", unsafe_allow_html=True)
with k3:
    st.markdown(f"""<div class="kpi-card amber">
      <div class="kpi-label">Late Rate</div>
      <div class="kpi-value" style="color:{AMBER};">{late_p:.1f}%</div>
      <div class="kpi-sub">{late_n:,} orders</div>
    </div>""", unsafe_allow_html=True)
with k4:
    st.markdown(f"""<div class="kpi-card red">
      <div class="kpi-label">Super Late</div>
      <div class="kpi-value" style="color:{RED};">{super_p:.1f}%</div>
      <div class="kpi-sub">{super_n:,} orders</div>
    </div>""", unsafe_allow_html=True)
with k5:
    st.markdown(f"""<div class="kpi-card">
      <div class="kpi-label">Avg Review Score</div>
      <div class="kpi-value">{avg_score:.2f}★</div>
      <div class="kpi-sub">avg delay {avg_delay:+.1f} days</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# TABS
# ════════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs([
    "📦  Overview",
    "🗺️  Geographic",
    "⭐  Sentiment",
    "🏆  DPRS & Categories"
])

# ────────────────────────────────────────────────────────────────────────────────
# TAB 1 — OVERVIEW
# Dataset: veridi_delivered_clean.csv
# ────────────────────────────────────────────────────────────────────────────────
with tab1:
    st.markdown('<div class="sec-title">📦 Dataset 1 — veridi_delivered_clean.csv — Delivery Overview</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    # ── Chart 1: Donut — Delivery Status Distribution ─────────────────────────
    with col1:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">Chart 1 — Delivery Status Distribution</div>', unsafe_allow_html=True)
        st.markdown('<div class="chart-sub">X: Status categories &nbsp;·&nbsp; Y: Count / % of orders (Story 2)</div>', unsafe_allow_html=True)

        status_counts = df["Delivery_Status"].value_counts().reset_index()
        status_counts.columns = ["Delivery_Status", "Count"]
        status_counts["Pct"] = (status_counts["Count"] / status_counts["Count"].sum() * 100).round(1)

        fig = go.Figure(go.Pie(
            labels=status_counts["Delivery_Status"],
            values=status_counts["Count"],
            hole=0.52,
            marker=dict(colors=[STATUS_COLORS.get(s, SLATE) for s in status_counts["Delivery_Status"]]),
            textinfo="label+percent",
            textfont=dict(size=12),
            hovertemplate="<b>%{label}</b><br>Orders: %{value:,}<br>Share: %{percent}<extra></extra>"
        ))
        fig.add_annotation(
            text=f"<b>{total:,}</b><br>Orders",
            x=0.5, y=0.5, font_size=14, showarrow=False,
            font=dict(color=NAVY)
        )
        fig.update_layout(
            margin=dict(t=10, b=10, l=10, r=10),
            height=310,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
            paper_bgcolor="white", plot_bgcolor="white"
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('<div class="insight"><strong>Looker Studio:</strong> Pie/Donut Chart · Dimension = <code>Delivery_Status</code> · Metric = <code>COUNT(order_id)</code></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Chart 2: Histogram — Delay Distribution ────────────────────────────────
    with col2:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">Chart 2 — Delivery Delay Distribution</div>', unsafe_allow_html=True)
        st.markdown('<div class="chart-sub">X: Days_Difference (Estimated−Actual) &nbsp;·&nbsp; Y: Order count</div>', unsafe_allow_html=True)

        fig2 = px.histogram(
            df, x="Days_Difference", nbins=35,
            color_discrete_sequence=[TEAL],
            labels={"Days_Difference": "Days (Estimated − Actual)", "count": "Orders"},
        )
        fig2.add_vline(x=0, line_dash="dash", line_color=RED,
                       annotation_text="Deadline", annotation_position="top right",
                       annotation_font_color=RED)
        fig2.update_layout(
            height=310, margin=dict(t=10, b=40, l=10, r=10),
            paper_bgcolor="white", plot_bgcolor="white",
            bargap=0.05,
            xaxis=dict(gridcolor="#f1f5f9", title="Days (positive = early, negative = late)"),
            yaxis=dict(gridcolor="#f1f5f9", title="Number of Orders"),
        )
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('<div class="insight"><strong>Looker Studio:</strong> Bar Chart · Dimension = <code>Days_Difference</code> (binned) · Metric = <code>COUNT(order_id)</code></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Chart 3: Line — Orders over time coloured by status ────────────────────
    st.markdown('<div class="sec-title">Orders Over Time</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">Chart 3 — Monthly Order Volume by Delivery Status</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-sub">X: order_purchase_timestamp (monthly) &nbsp;·&nbsp; Y: COUNT(order_id) &nbsp;·&nbsp; Color: Delivery_Status</div>', unsafe_allow_html=True)

    time_df = (
        df.groupby(["month", "Delivery_Status"])
        .size().reset_index(name="Count")
        .sort_values("month")
    )
    fig3 = px.line(
        time_df, x="month", y="Count", color="Delivery_Status",
        color_discrete_map=STATUS_COLORS,
        markers=True,
        labels={"month": "Month", "Count": "Orders", "Delivery_Status": "Status"},
    )
    fig3.update_traces(line=dict(width=2.5))
    fig3.update_layout(
        height=320, margin=dict(t=10, b=60, l=10, r=10),
        paper_bgcolor="white", plot_bgcolor="white",
        xaxis=dict(gridcolor="#f1f5f9", tickangle=-45),
        yaxis=dict(gridcolor="#f1f5f9"),
        legend=dict(orientation="h", yanchor="bottom", y=-0.35, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown('<div class="insight"><strong>Looker Studio:</strong> Time Series Chart · Dimension = <code>order_purchase_timestamp</code> (Month) · Metric = <code>COUNT(order_id)</code> · Breakdown = <code>Delivery_Status</code></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Chart 4: Stacked bar — Region Type vs Status ───────────────────────────
    col3, col4 = st.columns([1, 1])
    with col3:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">Chart 4 — Late Rate: Core vs Remote Regions</div>', unsafe_allow_html=True)
        st.markdown('<div class="chart-sub">X: Region_Type &nbsp;·&nbsp; Y: % Late orders</div>', unsafe_allow_html=True)

        region_df = (
            df.groupby("Region_Type")
            .agg(
                Orders=("order_id", "count"),
                Late_Pct=("Delivery_Status", lambda x: round((x != "On Time").mean() * 100, 1)),
                Avg_Score=("review_score", lambda x: round(x.mean(), 2))
            ).reset_index()
        )
        fig4 = px.bar(
            region_df, x="Region_Type", y="Late_Pct",
            color="Region_Type",
            color_discrete_map=REGION_COLORS,
            text="Late_Pct",
            labels={"Region_Type": "Region", "Late_Pct": "Late Delivery %"},
        )
        fig4.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig4.update_layout(
            height=310, margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor="white", plot_bgcolor="white",
            showlegend=False,
            yaxis=dict(gridcolor="#f1f5f9", range=[0, region_df["Late_Pct"].max() + 8]),
        )
        st.plotly_chart(fig4, use_container_width=True)
        st.markdown('<div class="insight"><strong>Looker Studio:</strong> Bar Chart · Dimension = <code>Region_Type</code> · Metric = <code>AVG(Late_flag)</code> calculated field</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col4:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">Chart 5 — Review Score Distribution (Heatmap)</div>', unsafe_allow_html=True)
        st.markdown('<div class="chart-sub">X: review_score (1–5) &nbsp;·&nbsp; Y: Delivery_Status &nbsp;·&nbsp; Color: % of orders</div>', unsafe_allow_html=True)

        heat_df = (
            df.groupby(["Delivery_Status", "review_score"])
            .size().reset_index(name="Count")
        )
        heat_pivot = heat_df.pivot(index="Delivery_Status", columns="review_score", values="Count").fillna(0)
        heat_pct   = heat_pivot.div(heat_pivot.sum(axis=1), axis=0) * 100

        fig5 = px.imshow(
            heat_pct,
            text_auto=".1f",
            color_continuous_scale=[[0, "#f0f9fb"], [0.5, TEAL], [1, NAVY]],
            labels={"x": "Review Score (1–5)", "y": "Delivery Status", "color": "%"},
            aspect="auto"
        )
        fig5.update_layout(
            height=310, margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor="white",
            coloraxis_colorbar=dict(title="%", thickness=12)
        )
        st.plotly_chart(fig5, use_container_width=True)
        st.markdown('<div class="insight"><strong>Looker Studio:</strong> Pivot Table · Row = <code>Delivery_Status</code> · Column = <code>review_score</code> · Metric = <code>COUNT(order_id)</code></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────────────────────────
# TAB 2 — GEOGRAPHIC
# Dataset: veridi_state_summary.csv
# ────────────────────────────────────────────────────────────────────────────────
with tab2:
    st.markdown('<div class="sec-title">🗺️ Dataset 2 — veridi_state_summary.csv — Geographic Analysis</div>', unsafe_allow_html=True)

    # Filter state df by selected states if any
    s_df = state_df.copy()
    if sel_states:
        s_df = s_df[s_df["customer_state"].isin(sel_states)]

    s_df_sorted_late = s_df.sort_values("Late_Pct", ascending=False)

    col1, col2 = st.columns([1.4, 1])

    # ── Chart 6: Horizontal bar — Late % by State ──────────────────────────────
    with col1:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">Chart 6 — Late Delivery Rate by State (%)</div>', unsafe_allow_html=True)
        st.markdown('<div class="chart-sub">X: Late_Pct &nbsp;·&nbsp; Y: customer_state &nbsp;·&nbsp; Color: severity (Story 3)</div>', unsafe_allow_html=True)

        bar_colors = []
        for p in s_df_sorted_late["Late_Pct"]:
            if p >= 25:   bar_colors.append(RED)
            elif p >= 15: bar_colors.append(AMBER)
            else:         bar_colors.append(GREEN)

        fig6 = go.Figure(go.Bar(
            x=s_df_sorted_late["Late_Pct"],
            y=s_df_sorted_late["customer_state"],
            orientation="h",
            marker_color=bar_colors,
            text=s_df_sorted_late["Late_Pct"].apply(lambda x: f"{x:.1f}%"),
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Late: %{x:.1f}%<extra></extra>"
        ))
        fig6.update_layout(
            height=520, margin=dict(t=10, b=10, l=10, r=60),
            paper_bgcolor="white", plot_bgcolor="white",
            xaxis=dict(gridcolor="#f1f5f9", title="Late Delivery %", range=[0, s_df_sorted_late["Late_Pct"].max() + 8]),
            yaxis=dict(autorange="reversed", title=""),
        )
        st.plotly_chart(fig6, use_container_width=True)
        st.markdown('<div class="insight"><strong>Looker Studio:</strong> Bar Chart · Dimension = <code>customer_state</code> · Metric = <code>Late_Pct</code> · Sort = Descending</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Chart 7: Scatter — Late % vs Avg Review Score by State ────────────────
    with col2:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">Chart 7 — Late % vs Avg Review Score by State</div>', unsafe_allow_html=True)
        st.markdown('<div class="chart-sub">X: Late_Pct &nbsp;·&nbsp; Y: Avg_Review_Score &nbsp;·&nbsp; Size: Total_Orders</div>', unsafe_allow_html=True)

        fig7 = px.scatter(
            s_df, x="Late_Pct", y="Avg_Review_Score",
            size="Total_Orders", text="customer_state",
            color="Late_Pct",
            color_continuous_scale=[[0, GREEN], [0.4, AMBER], [1, RED]],
            size_max=40,
            labels={"Late_Pct": "Late Delivery %", "Avg_Review_Score": "Avg Review Score"},
            hover_data=["Total_Orders", "DPRS"]
        )
        fig7.update_traces(textposition="top center", textfont_size=9)
        fig7.update_layout(
            height=520, margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor="white", plot_bgcolor="white",
            xaxis=dict(gridcolor="#f1f5f9"),
            yaxis=dict(gridcolor="#f1f5f9", range=[3.5, 4.5]),
            coloraxis_showscale=False
        )
        st.plotly_chart(fig7, use_container_width=True)
        st.markdown('<div class="insight"><strong>Looker Studio:</strong> Scatter Chart · X = <code>Late_Pct</code> · Y = <code>Avg_Review_Score</code> · Bubble = <code>Total_Orders</code></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Chart 8: Bar — Avg Delay Days by State ─────────────────────────────────
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">Chart 8 — Average Delay Days by State</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-sub">X: customer_state &nbsp;·&nbsp; Y: Avg_Delay_Days &nbsp;·&nbsp; (negative = late, positive = early)</div>', unsafe_allow_html=True)

    s_sorted_delay = s_df.sort_values("Avg_Delay_Days")
    delay_colors = [RED if v < -3 else AMBER if v < 0 else GREEN for v in s_sorted_delay["Avg_Delay_Days"]]

    fig8 = go.Figure(go.Bar(
        x=s_sorted_delay["customer_state"],
        y=s_sorted_delay["Avg_Delay_Days"],
        marker_color=delay_colors,
        text=s_sorted_delay["Avg_Delay_Days"].apply(lambda x: f"{x:+.1f}d"),
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Avg Delay: %{y:+.2f} days<extra></extra>"
    ))
    fig8.add_hline(y=0, line_dash="dash", line_color=SLATE, line_width=1.5)
    fig8.update_layout(
        height=320, margin=dict(t=10, b=40, l=10, r=10),
        paper_bgcolor="white", plot_bgcolor="white",
        xaxis=dict(gridcolor="#f1f5f9", title="State"),
        yaxis=dict(gridcolor="#f1f5f9", title="Avg Delay Days (negative = late)"),
    )
    st.plotly_chart(fig8, use_container_width=True)
    st.markdown('<div class="insight"><strong>Looker Studio:</strong> Bar Chart · Dimension = <code>customer_state</code> · Metric = <code>AVG(Avg_Delay_Days)</code> · Sort = Ascending</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────────────────────────
# TAB 3 — SENTIMENT
# Dataset: veridi_delivered_clean.csv
# ────────────────────────────────────────────────────────────────────────────────
with tab3:
    st.markdown('<div class="sec-title">⭐ Dataset 1 — veridi_delivered_clean.csv — Customer Sentiment (Story 4)</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    # ── Chart 9: Bar — Avg Review Score by Delivery Status ────────────────────
    with col1:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">Chart 9 — Avg Review Score by Delivery Status</div>', unsafe_allow_html=True)
        st.markdown('<div class="chart-sub">X: Delivery_Status &nbsp;·&nbsp; Y: AVG(review_score) &nbsp;·&nbsp; Story 4 core chart</div>', unsafe_allow_html=True)

        rev_df = (
            df[df["Delivery_Status"] != "Not Delivered"]
            .dropna(subset=["review_score"])
            .groupby("Delivery_Status")
            .agg(Avg_Score=("review_score", "mean"), n=("review_score", "count"))
            .reset_index()
            .sort_values("Avg_Score", ascending=False)
        )
        fig9 = px.bar(
            rev_df, x="Delivery_Status", y="Avg_Score",
            color="Delivery_Status",
            color_discrete_map=STATUS_COLORS,
            text=rev_df["Avg_Score"].apply(lambda x: f"{x:.2f}★"),
            labels={"Delivery_Status": "Delivery Status", "Avg_Score": "Avg Review Score"},
        )
        fig9.update_traces(textposition="outside")
        fig9.update_layout(
            height=340, margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor="white", plot_bgcolor="white",
            showlegend=False,
            yaxis=dict(range=[0, 5.3], gridcolor="#f1f5f9", title="Avg Review Score"),
            xaxis=dict(title="Delivery Status",
                       categoryorder="array",
                       categoryarray=["On Time", "Late", "Super Late"])
        )
        st.plotly_chart(fig9, use_container_width=True)
        st.markdown('<div class="insight"><strong>Looker Studio:</strong> Bar Chart · Dimension = <code>Delivery_Status</code> · Metric = <code>AVG(review_score)</code></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Chart 10: Box plot — Score distribution by Status ─────────────────────
    with col2:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">Chart 10 — Review Score Distribution (Box Plot)</div>', unsafe_allow_html=True)
        st.markdown('<div class="chart-sub">X: Delivery_Status &nbsp;·&nbsp; Y: review_score &nbsp;·&nbsp; Shows spread + outliers</div>', unsafe_allow_html=True)

        plot_box = df[df["Delivery_Status"].isin(["On Time", "Late", "Super Late"])].dropna(subset=["review_score"])
        fig10 = px.box(
            plot_box, x="Delivery_Status", y="review_score",
            color="Delivery_Status",
            color_discrete_map=STATUS_COLORS,
            points="outliers",
            labels={"Delivery_Status": "Delivery Status", "review_score": "Review Score (1–5)"},
            category_orders={"Delivery_Status": ["On Time", "Late", "Super Late"]}
        )
        fig10.update_layout(
            height=340, margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor="white", plot_bgcolor="white",
            showlegend=False,
            yaxis=dict(gridcolor="#f1f5f9", title="Review Score (1–5)"),
        )
        st.plotly_chart(fig10, use_container_width=True)
        st.markdown('<div class="insight"><strong>Looker Studio:</strong> Scorecard / Table · Group by <code>Delivery_Status</code> · Show AVG, MEDIAN, COUNT of <code>review_score</code></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Chart 11: Scatter — Delay days vs avg review ───────────────────────────
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">Chart 11 — Review Score vs. Delay Days</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-sub">X: Days_Difference (bucketed) &nbsp;·&nbsp; Y: AVG(review_score) &nbsp;·&nbsp; Bubble size: order volume &nbsp;·&nbsp; LOWESS trend</div>', unsafe_allow_html=True)

    scatter_df = df.dropna(subset=["review_score"]).copy()
    scatter_df["delay_bucket"] = scatter_df["Days_Difference"].clip(-20, 15).astype(int)
    scatter_agg = (
        scatter_df.groupby("delay_bucket")
        .agg(Avg_Score=("review_score", "mean"), n=("review_score", "count"))
        .reset_index()
    )
    fig11 = px.scatter(
        scatter_agg, x="delay_bucket", y="Avg_Score", size="n",
        color="Avg_Score",
        color_continuous_scale=[[0, RED], [0.5, AMBER], [1, GREEN]],
        trendline="lowess", trendline_color_override=NAVY,
        labels={"delay_bucket": "Days (Estimated − Actual) | Negative = Late",
                "Avg_Score": "Avg Review Score (1–5)", "n": "Orders"},
        size_max=35
    )
    fig11.add_vline(x=0, line_dash="dash", line_color=SLATE,
                    annotation_text="Deadline", annotation_position="top right",
                    annotation_font_color=SLATE)
    fig11.update_layout(
        height=340, margin=dict(t=10, b=40, l=10, r=10),
        paper_bgcolor="white", plot_bgcolor="white",
        xaxis=dict(gridcolor="#f1f5f9"),
        yaxis=dict(gridcolor="#f1f5f9", range=[1.5, 5.2]),
        coloraxis_showscale=False
    )
    st.plotly_chart(fig11, use_container_width=True)
    st.markdown('<div class="insight"><strong>Looker Studio:</strong> Scatter Chart · Dimension = <code>Days_Difference</code> (binned) · Metric = <code>AVG(review_score)</code> · Bubble = <code>COUNT(order_id)</code></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Stat callout row ───────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    scores = df.groupby("Delivery_Status")["review_score"].mean()
    for col, status, color in [
        (c1, "On Time",    GREEN),
        (c2, "Late",       AMBER),
        (c3, "Super Late", RED),
    ]:
        v = scores.get(status, 0)
        col.markdown(f"""<div class="kpi-card" style="border-top-color:{color}">
          <div class="kpi-label">{status}</div>
          <div class="kpi-value" style="color:{color};">{v:.2f}★</div>
          <div class="kpi-sub">avg review score</div>
        </div>""", unsafe_allow_html=True)
    drop = scores.get("On Time", 0) - scores.get("Super Late", 0)
    c4.markdown(f"""<div class="kpi-card red">
      <div class="kpi-label">Score Drop</div>
      <div class="kpi-value" style="color:{RED};">−{drop:.2f}★</div>
      <div class="kpi-sub">On Time → Super Late</div>
    </div>""", unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────────────────────────
# TAB 4 — DPRS & CATEGORIES
# Datasets: veridi_state_summary.csv + veridi_category_summary.csv
# ────────────────────────────────────────────────────────────────────────────────
with tab4:
    st.markdown('<div class="sec-title">🏆 Datasets 2 & 3 — DPRS Leaderboard & Category Analysis</div>', unsafe_allow_html=True)

    # ── Chart 12: DPRS bar — state leaderboard ────────────────────────────────
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">Chart 12 — Delivery Promise Reliability Score (DPRS) by State</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-sub">X: DPRS score (0–100) &nbsp;·&nbsp; Y: customer_state &nbsp;·&nbsp; Color: score band &nbsp;·&nbsp; Dataset: veridi_state_summary.csv</div>', unsafe_allow_html=True)

    dprs_df = s_df.sort_values("DPRS", ascending=True)
    dprs_colors = [RED if v < 30 else AMBER if v < 70 else GREEN for v in dprs_df["DPRS"]]

    fig12 = go.Figure(go.Bar(
        x=dprs_df["DPRS"],
        y=dprs_df["customer_state"],
        orientation="h",
        marker_color=dprs_colors,
        text=dprs_df["DPRS"].apply(lambda x: f"{x:.0f}"),
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>DPRS: %{x:.0f}/100<br>Late: " +
                      dprs_df["Late_Pct"].astype(str).str.cat(["%"] * len(dprs_df)) +
                      "<extra></extra>"
    ))
    fig12.update_layout(
        height=560, margin=dict(t=10, b=10, l=10, r=60),
        paper_bgcolor="white", plot_bgcolor="white",
        xaxis=dict(gridcolor="#f1f5f9", title="DPRS Score (0 = worst → 100 = best)", range=[0, 115]),
        yaxis=dict(title=""),
    )
    # Add score zones
    fig12.add_vrect(x0=0,  x1=30,  fillcolor=RED,   opacity=0.05, line_width=0, annotation_text="HIGH RISK", annotation_position="top left",  annotation_font_size=8, annotation_font_color=RED)
    fig12.add_vrect(x0=30, x1=70,  fillcolor=AMBER,  opacity=0.05, line_width=0, annotation_text="MEDIUM",    annotation_position="top left",  annotation_font_size=8, annotation_font_color=AMBER)
    fig12.add_vrect(x0=70, x1=100, fillcolor=GREEN,  opacity=0.05, line_width=0, annotation_text="RELIABLE",  annotation_position="top right", annotation_font_size=8, annotation_font_color=GREEN)
    st.plotly_chart(fig12, use_container_width=True)
    st.markdown('<div class="insight"><strong>Looker Studio:</strong> Bar Chart · Dimension = <code>customer_state</code> · Metric = <code>DPRS</code> · Sort = Ascending · Color by score band (calculated field)</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])

    # ── Chart 13: Category late rate bar ──────────────────────────────────────
    with col1:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">Chart 13 — Late Rate by Product Category</div>', unsafe_allow_html=True)
        st.markdown('<div class="chart-sub">X: Late_Pct &nbsp;·&nbsp; Y: Category &nbsp;·&nbsp; Dataset: veridi_category_summary.csv (Bonus)</div>', unsafe_allow_html=True)

        c_df = cat_df.sort_values("Late_Pct", ascending=True)
        cat_colors = [RED if v >= 30 else AMBER if v >= 18 else GREEN for v in c_df["Late_Pct"]]

        fig13 = go.Figure(go.Bar(
            x=c_df["Late_Pct"],
            y=c_df["Category"].str.replace("_", " ").str.title(),
            orientation="h",
            marker_color=cat_colors,
            text=c_df["Late_Pct"].apply(lambda x: f"{x:.1f}%"),
            textposition="outside",
        ))
        fig13.update_layout(
            height=480, margin=dict(t=10, b=10, l=10, r=55),
            paper_bgcolor="white", plot_bgcolor="white",
            xaxis=dict(gridcolor="#f1f5f9", title="Late Delivery %", range=[0, c_df["Late_Pct"].max() + 8]),
            yaxis=dict(title=""),
        )
        st.plotly_chart(fig13, use_container_width=True)
        st.markdown('<div class="insight"><strong>Looker Studio:</strong> Bar Chart · Dimension = <code>Category</code> · Metric = <code>Late_Pct</code> · Sort = Descending</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Chart 14: Category review score vs late % scatter ─────────────────────
    with col2:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">Chart 14 — Category: Late % vs Avg Review Score</div>', unsafe_allow_html=True)
        st.markdown('<div class="chart-sub">X: Late_Pct &nbsp;·&nbsp; Y: Avg_Score &nbsp;·&nbsp; Size: Orders &nbsp;·&nbsp; Dataset: veridi_category_summary.csv</div>', unsafe_allow_html=True)

        fig14 = px.scatter(
            cat_df,
            x="Late_Pct", y="Avg_Score",
            size="Orders", text="Category",
            color="Late_Pct",
            color_continuous_scale=[[0, GREEN], [0.4, AMBER], [1, RED]],
            size_max=38,
            labels={"Late_Pct": "Late Delivery %", "Avg_Score": "Avg Review Score", "Orders": "Order Volume"},
        )
        fig14.update_traces(
            textposition="top center", textfont_size=7,
            text=cat_df["Category"].str.replace("_", " ").str.title()
        )
        fig14.update_layout(
            height=480, margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor="white", plot_bgcolor="white",
            xaxis=dict(gridcolor="#f1f5f9"),
            yaxis=dict(gridcolor="#f1f5f9"),
            coloraxis_showscale=False
        )
        st.plotly_chart(fig14, use_container_width=True)
        st.markdown('<div class="insight"><strong>Looker Studio:</strong> Scatter Chart · X = <code>Late_Pct</code> · Y = <code>Avg_Score</code> · Bubble = <code>Orders</code></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# LOOKER STUDIO REFERENCE TABLE
# ════════════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown('<div class="sec-title">📋 Looker Studio — Complete X/Y Reference for All 14 Charts</div>', unsafe_allow_html=True)

ref_data = {
    "Chart": [
        "1 — Delivery Status Donut",
        "2 — Delay Histogram",
        "3 — Orders Over Time",
        "4 — Core vs Remote Bar",
        "5 — Score Heatmap",
        "6 — Late % by State Bar",
        "7 — Late % vs Score Scatter",
        "8 — Avg Delay by State",
        "9 — Avg Score by Status Bar",
        "10 — Score Box Plot",
        "11 — Score vs Delay Scatter",
        "12 — DPRS Leaderboard",
        "13 — Category Late Rate",
        "14 — Category Score Scatter",
    ],
    "Chart Type": [
        "Donut / Pie",  "Bar (histogram)", "Time Series Line",
        "Bar",          "Pivot Table / Heatmap",
        "Bar (horiz.)", "Bubble Scatter",  "Bar",
        "Bar",          "Table + Scorecard", "Bubble Scatter",
        "Bar (horiz.)", "Bar (horiz.)",    "Bubble Scatter",
    ],
    "Dimension (X)": [
        "Delivery_Status", "Days_Difference (binned)", "order_purchase_timestamp (Month)",
        "Region_Type", "Delivery_Status (rows) × review_score (cols)",
        "customer_state", "Late_Pct", "customer_state",
        "Delivery_Status", "Delivery_Status", "Days_Difference (binned)",
        "customer_state", "Category", "Late_Pct",
    ],
    "Metric (Y)": [
        "COUNT(order_id)", "COUNT(order_id)", "COUNT(order_id)",
        "AVG(late_flag) × 100", "COUNT(order_id) as %",
        "Late_Pct", "Avg_Review_Score", "Avg_Delay_Days",
        "AVG(review_score)", "AVG / MEDIAN(review_score)", "AVG(review_score)",
        "DPRS", "Late_Pct", "Avg_Score",
    ],
    "Extra / Color": [
        "—", "—", "Breakdown: Delivery_Status",
        "—", "—",
        "Color: Late_Pct band", "Bubble: Total_Orders", "Color: delay band",
        "Color: Delivery_Status", "—", "Bubble: COUNT(order_id)",
        "Color: DPRS band", "Color: Late_Pct band", "Bubble: Orders",
    ],
    "Dataset": [
        "delivered_clean","delivered_clean","delivered_clean",
        "delivered_clean","delivered_clean",
        "state_summary","state_summary","state_summary",
        "delivered_clean","delivered_clean","delivered_clean",
        "state_summary","category_summary","category_summary",
    ],
    "Story": [
        "Story 2","Story 2","Extra",
        "Story 3","Story 4",
        "Story 3","Story 3","Story 3",
        "Story 4","Story 4","Story 4",
        "Candidate's","Bonus","Bonus",
    ],
}

ref_df = pd.DataFrame(ref_data)
st.dataframe(
    ref_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Chart":        st.column_config.TextColumn(width="medium"),
        "Chart Type":   st.column_config.TextColumn(width="small"),
        "Dimension (X)":st.column_config.TextColumn(width="large"),
        "Metric (Y)":   st.column_config.TextColumn(width="large"),
        "Story":        st.column_config.TextColumn(width="small"),
    }
)

st.markdown(f"""
<div style='text-align:center; padding:18px; color:{SLATE}; font-size:0.75rem; margin-top:10px;'>
  Veridi Logistics Delivery Audit Dashboard &nbsp;·&nbsp;
  Olist Brazilian E-Commerce Dataset 2017–2018 &nbsp;·&nbsp;
  Built with Streamlit + Plotly
</div>
""", unsafe_allow_html=True)
