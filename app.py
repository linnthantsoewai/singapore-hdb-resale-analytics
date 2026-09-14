"""
Singapore HDB Resale Analytics (1990–2026) - Streamlit Dashboard

An institutional data analytics application presenting the results of 5 core PostgreSQL
investigations across 986,548 historical resale transactions.
"""

import psycopg
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

DB_CONN_STR = "dbname=hdb_resale port=5433"

# -----------------------------------------------------------------------------
# 1. Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Singapore HDB Resale Analytics (1990–2026)",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -----------------------------------------------------------------------------
# 2. Professional Light Mode UI Design System
# -----------------------------------------------------------------------------
CSS_VARS = """
<style>
/* Hide default footer */
footer {
    display: none !important;
}

/* App Container */
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], .main, .block-container, section[data-testid="stMain"] {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
}

.block-container {
    padding: 1.5rem 2.2rem 3rem !important;
    max-width: 1400px !important;
}

/* Institutional Brand Header */
.brand-container {
    border-bottom: 1px solid rgba(128, 128, 128, 0.2);
    padding-bottom: 0.9rem;
    margin-bottom: 1.25rem;
}
.brand-title {
    font-size: 1.45rem;
    font-weight: 700;
    color: var(--text-color);
    letter-spacing: -0.025em;
    margin: 0;
}
.brand-subtitle {
    font-size: 0.82rem;
    color: var(--text-color);
    opacity: 0.72;
    margin-top: 0.2rem;
    font-weight: 500;
}

/* Metric KPI Cards */
.metric-card {
    background: var(--secondary-background-color);
    border: 1px solid rgba(128, 128, 128, 0.22);
    border-radius: 8px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.5rem;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.08);
    transition: border-color 0.15s ease;
}
.metric-card:hover {
    border-color: rgba(128, 128, 128, 0.45);
}
.metric-label {
    font-size: 0.72rem;
    color: var(--text-color);
    opacity: 0.7;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.metric-value {
    font-size: 1.55rem;
    font-weight: 700;
    color: var(--text-color);
    letter-spacing: -0.03em;
    margin: 0.2rem 0;
}
.metric-delta {
    font-size: 0.73rem;
    font-weight: 600;
    padding: 2px 7px;
    border-radius: 4px;
    display: inline-flex;
    align-items: center;
    gap: 3px;
}
.delta-up { color: #16a34a; background: rgba(34, 197, 94, 0.14); border: 1px solid rgba(34, 197, 94, 0.3); }
.delta-down { color: #dc2626; background: rgba(239, 68, 68, 0.14); border: 1px solid rgba(239, 68, 68, 0.3); }
.delta-warn { color: #d97706; background: rgba(245, 158, 11, 0.14); border: 1px solid rgba(245, 158, 11, 0.3); }
.delta-neutral { color: var(--text-color); background: rgba(128, 128, 128, 0.12); border: 1px solid rgba(128, 128, 128, 0.2); }

/* Chart Container */
.chart-wrap {
    background: var(--secondary-background-color);
    border: 1px solid rgba(128, 128, 128, 0.22);
    border-radius: 8px;
    padding: 1.15rem 1.25rem 0.75rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.08);
}
.chart-title {
    font-size: 0.9rem;
    font-weight: 700;
    color: var(--text-color);
    margin-bottom: 0.15rem;
}
.chart-subtitle {
    font-size: 0.75rem;
    color: var(--text-color);
    opacity: 0.65;
    margin-bottom: 0.75rem;
}

/* Tables */
.table-container {
    background: var(--secondary-background-color);
    border: 1px solid rgba(128, 128, 128, 0.22);
    border-radius: 8px;
    overflow: hidden;
    margin-top: 0.85rem;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.08);
}
.data-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.81rem;
}
.data-table th {
    text-align: left;
    padding: 0.65rem 0.9rem;
    background: rgba(128, 128, 128, 0.08);
    color: var(--text-color);
    opacity: 0.85;
    font-weight: 600;
    font-size: 0.71rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    border-bottom: 1px solid rgba(128, 128, 128, 0.2);
}
.data-table td {
    padding: 0.65rem 0.9rem;
    color: var(--text-color);
    border-bottom: 1px solid rgba(128, 128, 128, 0.12);
}
.data-table tr:hover {
    background: rgba(128, 128, 128, 0.05);
}
.data-table tr:last-child td {
    border-bottom: none;
}

/* Status Badges */
.badge {
    display: inline-block;
    padding: 2px 7px;
    border-radius: 4px;
    font-size: 0.71rem;
    font-weight: 600;
    letter-spacing: 0.02em;
}
.badge-green { color: #16a34a; background: rgba(34, 197, 94, 0.14); border: 1px solid rgba(34, 197, 94, 0.3); }
.badge-red { color: #dc2626; background: rgba(239, 68, 68, 0.14); border: 1px solid rgba(239, 68, 68, 0.3); }
.badge-amber { color: #d97706; background: rgba(245, 158, 11, 0.14); border: 1px solid rgba(245, 158, 11, 0.3); }
.badge-blue { color: #3b82f6; background: rgba(59, 130, 246, 0.14); border: 1px solid rgba(59, 130, 246, 0.3); }
.badge-neutral { color: var(--text-color); background: rgba(128, 128, 128, 0.12); border: 1px solid rgba(128, 128, 128, 0.2); }

/* Tabs Styling */
button[data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text-color) !important;
    opacity: 0.65;
    font-size: 0.83rem !important;
    font-weight: 600 !important;
    padding: 0.55rem 1rem !important;
    border: 1px solid transparent !important;
    border-radius: 6px !important;
}
button[data-baseweb="tab"] div, button[data-baseweb="tab"] p {
    color: var(--text-color) !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: var(--text-color) !important;
    opacity: 1 !important;
    background: var(--secondary-background-color) !important;
    border: 1px solid rgba(128, 128, 128, 0.22) !important;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.06) !important;
}
button[data-baseweb="tab"][aria-selected="true"] div, button[data-baseweb="tab"][aria-selected="true"] p {
    color: var(--text-color) !important;
    font-weight: 700 !important;
}
[data-baseweb="tab-highlight"], [data-baseweb="tab-border"] {
    display: none !important;
}
[data-baseweb="tab-list"] {
    gap: 4px !important;
    background: rgba(128, 128, 128, 0.08) !important;
    border: 1px solid rgba(128, 128, 128, 0.16) !important;
    border-radius: 8px !important;
    padding: 3px;
    margin-bottom: 1.25rem;
}
</style>
"""
st.markdown(CSS_VARS, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 3. Data Ingestion & Caching Layer (PostgreSQL 16)
# -----------------------------------------------------------------------------
def clean_numeric_df(df: pd.DataFrame) -> pd.DataFrame:
    for col in df.columns:
        if df[col].dtype == object:
            try:
                df[col] = pd.to_numeric(df[col])
            except (ValueError, TypeError):
                pass
    return df


def _fetch_sql(sql_path: str) -> pd.DataFrame:
    """Shared helper: connect to DB, execute a single-statement SQL file, return a clean DataFrame."""
    with psycopg.connect(DB_CONN_STR) as conn:
        with conn.cursor() as cur:
            with open(sql_path, "r") as f:
                cur.execute(f.read())
            cols = [d[0] for d in cur.description]
            return clean_numeric_df(pd.DataFrame(cur.fetchall(), columns=cols))


@st.cache_data(ttl=3600)
def fetch_overview_kpis():
    with psycopg.connect(DB_CONN_STR) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    COUNT(*),
                    MIN(transaction_year),
                    MAX(transaction_year),
                    COUNT(DISTINCT town)
                FROM resale_prices;
            """)
            total_rows, min_year, max_year, total_towns = cur.fetchone()

            cur.execute("""
                SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY resale_price)
                FROM resale_prices
                WHERE transaction_year = (SELECT MAX(transaction_year) FROM resale_prices);
            """)
            latest_median_price = cur.fetchone()[0]

            cur.execute("""
                SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY resale_price)
                FROM resale_prices
                WHERE transaction_year = (SELECT MIN(transaction_year) FROM resale_prices);
            """)
            earliest_median_price = cur.fetchone()[0]

    return {
        "total_rows": total_rows,
        "min_year": min_year,
        "max_year": max_year,
        "total_towns": total_towns,
        "latest_median_price": float(latest_median_price),
        "earliest_median_price": float(earliest_median_price),
    }


@st.cache_data(ttl=3600)
def fetch_lease_decay_data():
    return _fetch_sql("sql/01_lease_decay_cliff.sql")


@st.cache_data(ttl=3600)
def fetch_real_growth_data():
    return _fetch_sql("sql/02_real_vs_nominal_growth.sql")


@st.cache_data(ttl=3600)
def fetch_town_ranking_data():
    return _fetch_sql("sql/03_town_ranking_by_decade.sql")


@st.cache_data(ttl=3600)
def fetch_size_and_storeys_data():
    with psycopg.connect(DB_CONN_STR) as conn:
        with conn.cursor() as cur:
            with open("sql/04_price_per_sqm_storeys.sql", "r") as f:
                stmts = [s.strip() for s in f.read().split(";") if s.strip()]
            cur.execute(stmts[0])
            part1 = clean_numeric_df(pd.DataFrame(cur.fetchall(), columns=[d[0] for d in cur.description]))
            cur.execute(stmts[1])
            part2 = clean_numeric_df(pd.DataFrame(cur.fetchall(), columns=[d[0] for d in cur.description]))
    return part1, part2


@st.cache_data(ttl=3600)
def fetch_policy_impact_data():
    return _fetch_sql("sql/05_policy_event_impact.sql")


def apply_chart_theme(fig, height=380):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
            size=11,
        ),
        margin=dict(l=10, r=10, t=30, b=10),
        height=height,
        xaxis=dict(
            gridcolor="rgba(128, 128, 128, 0.15)",
            zerolinecolor="rgba(128, 128, 128, 0.25)",
        ),
        yaxis=dict(
            gridcolor="rgba(128, 128, 128, 0.15)",
            zerolinecolor="rgba(128, 128, 128, 0.25)",
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
    )
    return fig


def render_html_table(headers: list[str], rows_html: str):
    th_tags = "".join(f"<th>{h}</th>" for h in headers)
    html_content = f"""<div class="table-container"><table class="data-table"><thead><tr>{th_tags}</tr></thead><tbody>{rows_html}</tbody></table></div>"""
    st.html(html_content)


# -----------------------------------------------------------------------------
# 4. Institutional Header & Top KPI Bar
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="brand-container">
        <h1 class="brand-title">Singapore HDB Resale Analytics (1990–2026)</h1>
        <div class="brand-subtitle">
            PostgreSQL 16 Engine • 5 Core Empirical Investigations • 986,548 Public Resale Transactions
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

kpis = fetch_overview_kpis()
k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Dataset Depth</div>
            <div class="metric-value">{kpis['total_rows']:,}</div>
            <div class="metric-delta delta-neutral">Complete Historical Records</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with k2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Temporal Span</div>
            <div class="metric-value">{kpis['min_year']} – {kpis['max_year']}</div>
            <div class="metric-delta delta-neutral">36 Years • {kpis['total_towns']} Estates</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with k3:
    nominal_gain = (
        (kpis["latest_median_price"] - kpis["earliest_median_price"])
        / kpis["earliest_median_price"]
        * 100
    )
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Current Median Resale Price</div>
            <div class="metric-value">${kpis['latest_median_price']:,.0f}</div>
            <div class="metric-delta delta-up">+{nominal_gain:,.0f}% since 1990 ($52.5k)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with k4:
    st.markdown(
        """
        <div class="metric-card">
            <div class="metric-label">Real Purchasing Power CAGR</div>
            <div class="metric-value">4.4% Real</div>
            <div class="metric-delta delta-warn">vs 6.4% Nominal (Inflation = 31%)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")

# -----------------------------------------------------------------------------
# 5. Core Analytical Inquiries (Tabs)
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "1. The Lease Decay Cliff",
    "2. Real vs Nominal Growth",
    "3. Town Ranking by Decade",
    "4. Size & Storey Premiums",
    "5. Macro Policy & Cooling Measures",
])

# -----------------------------------------------------------------------------
# TAB 1: The Lease Decay Cliff (60-Year Boundary)
# -----------------------------------------------------------------------------
with tab1:
    st.markdown("### 1. The Lease Decay Cliff Analysis (60-Year Financing Threshold)")
    st.markdown(
        "In Singapore, commercial banks cap mortgage loans and CPF housing usage restrictions kick in once remaining lease tenure drops below **60 years**. "
        "Does market transaction data exhibit a sharp cliff at this threshold?"
    )

    df_decay = fetch_lease_decay_data()
    avail_towns = sorted(df_decay["town"].unique().tolist())

    col_ctrl1, col_ctrl2 = st.columns([1, 1])
    with col_ctrl1:
        selected_town = st.selectbox(
            "Select Housing Estate / Town:",
            avail_towns,
            index=avail_towns.index("QUEENSTOWN") if "QUEENSTOWN" in avail_towns else 0,
        )
    with col_ctrl2:
        town_df = df_decay[df_decay["town"] == selected_town]
        avail_flats = sorted(town_df["flat_type"].unique().tolist())
        selected_flat = st.selectbox("Select Flat Type:", avail_flats, index=0)

    sub_df = df_decay[
        (df_decay["town"] == selected_town) & (df_decay["flat_type"] == selected_flat)
    ].sort_values("lease_bracket")

    if not sub_df.empty:
        colors = []
        for b in sub_df["lease_bracket"]:
            if "55-59" in b:
                colors.append("#dc2626")  # Vivid Crimson for cliff
            elif "60-64" in b:
                colors.append("#d97706")  # Amber for pre-cliff boundary
            else:
                colors.append("#2563eb")  # Vibrant Royal Blue

        fig_decay = go.Figure()
        fig_decay.add_trace(go.Bar(
            x=sub_df["lease_bracket"],
            y=sub_df["median_psm"],
            marker_color=colors,
            name="Median Price/sqm ($)",
            text=[f"${v:,.0f}" for v in sub_df["median_psm"]],
            textposition="auto",
        ))

        fig_decay.update_layout(
            title=f"Median Price-per-sqm across Lease Brackets: {selected_town} ({selected_flat})",
            xaxis_title="Remaining Lease Tenure Bracket",
            yaxis_title="Median Price per SQM ($)",
        )
        apply_chart_theme(fig_decay, height=420)

        st.markdown("""
        <div class="chart-wrap">
            <div class="chart-title">Tenure Valuation Progression ($/sqm)</div>
            <div class="chart-subtitle">Discontinuity and pricing drop as remaining tenure crosses the 60-year threshold (highlighted in crimson)</div>
        """, unsafe_allow_html=True)
        st.plotly_chart(fig_decay, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

        table_rows = ""
        for _, row in sub_df.iterrows():
            drop_str = f"${row['absolute_psm_drop']:,.0f}" if pd.notna(row['absolute_psm_drop']) else "—"
            pct_str = f"{row['step_change_pct']:+.1f}%" if pd.notna(row['step_change_pct']) else "—"
            
            badge_class = "badge-blue"
            if row['cliff_indicator'] == "CONFIRMED CLIFF":
                badge_class = "badge-red"
            elif row['cliff_indicator'] == "MODERATE IMPACT":
                badge_class = "badge-amber"
            elif row['cliff_indicator'] == "BASELINE":
                badge_class = "badge-neutral"

            is_neg = pd.notna(row['step_change_pct']) and row['step_change_pct'] < 0
            val_style = 'color: #dc2626; font-weight: 700;' if is_neg else ''
            drop_style = 'color: #dc2626;' if is_neg else ''

            table_rows += f"""<tr><td><strong>{row['lease_bracket']}</strong></td><td>{row['sales_count']:,}</td><td><strong>${row['median_psm']:,.0f}</strong></td><td>${row['median_price']:,.0f}</td><td style="{drop_style}">{drop_str}</td><td style="{val_style}">{pct_str}</td><td><span class="badge {badge_class}">{row['cliff_indicator']}</span></td></tr>"""

        render_html_table(
            ["Lease Bracket", "Transactions", "Median PSM ($)", "Median Lump Sum ($)", "PSM Drop ($)", "Step Change (%)", "Cliff Status"],
            table_rows
        )
    else:
        st.info("No transaction data available for this specific combination.")


# -----------------------------------------------------------------------------
# TAB 2: Real vs Nominal Capital Growth (1990–2026)
# -----------------------------------------------------------------------------
with tab2:
    st.markdown("### 2. Real (CPI Inflation-Adjusted) vs. Nominal Price Growth (1990–2026)")
    st.markdown(
        r"Headline resale prices grew from **\$52,500** in 1990 to **\$630,000** in 2026. "
        r"However, adjusting for the official Singapore Department of Statistics Consumer Price Index (CPI) reveals the true purchasing power gain."
    )

    df_real = fetch_real_growth_data()

    r1, r2, r3, r4 = st.columns(4)
    with r1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Nominal 36-Year CAGR</div>
            <div class="metric-value">6.4%</div>
            <div class="metric-delta delta-neutral">Total Gain: +1,100%</div>
        </div>
        """, unsafe_allow_html=True)
    with r2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Real (CPI-Adjusted) CAGR</div>
            <div class="metric-value">4.4%</div>
            <div class="metric-delta delta-warn">Total Gain: +523% (1990 $)</div>
        </div>
        """, unsafe_allow_html=True)
    with r3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">CPI Cumulative Inflation</div>
            <div class="metric-value">92.5%</div>
            <div class="metric-delta delta-down">1990 $1.00 = 2026 $1.925</div>
        </div>
        """, unsafe_allow_html=True)
    with r4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Real Wealth Creation</div>
            <div class="metric-value">+$274,773</div>
            <div class="metric-delta delta-up">Net gain above inflation per flat</div>
        </div>
        """, unsafe_allow_html=True)

    metric_choice = st.radio(
        "Select Valuation Metric to Plot:",
        ["Price per SQM ($/sqm)", "Lump Sum Resale Price ($)"],
        horizontal=True,
    )

    fig_growth = go.Figure()
    if metric_choice == "Price per SQM ($/sqm)":
        y_nom = df_real["nominal_median_psm"]
        y_real = df_real["real_median_psm_1990_dollars"]
        y_label = "Price per SQM ($)"
    else:
        y_nom = df_real["nominal_median_price"]
        y_real = df_real["real_median_price_1990_dollars"]
        y_label = "Median Price ($)"

    fig_growth.add_trace(go.Scatter(
        x=df_real["transaction_year"],
        y=y_nom,
        mode="lines+markers",
        name="Nominal Price (As Reported)",
        line=dict(color="#2563eb", width=2.5),
        marker=dict(size=4),
    ))
    fig_growth.add_trace(go.Scatter(
        x=df_real["transaction_year"],
        y=y_real,
        mode="lines+markers",
        name="Real Price (Deflated to 1990 Base Dollars)",
        line=dict(color="#10b981", width=2.5),
        marker=dict(size=4),
        fill="tonexty",
        fillcolor="rgba(37, 99, 235, 0.08)",
    ))

    fig_growth.update_layout(
        title="36-Year Historical Trajectory: Nominal vs Real Price (Inflation Gap Shaded)",
        xaxis_title="Transaction Year",
        yaxis_title=y_label,
        hovermode="x unified",
    )
    apply_chart_theme(fig_growth, height=450)

    st.markdown("""
    <div class="chart-wrap">
        <div class="chart-title">The Real Purchasing Power Trajectory (1990–2026)</div>
        <div class="chart-subtitle">The shaded region represents the inflation drag accounted for by consumer price index changes</div>
    """, unsafe_allow_html=True)
    st.plotly_chart(fig_growth, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# TAB 3: Town Appreciation Ranking, Decade by Decade
# -----------------------------------------------------------------------------
with tab3:
    st.markdown("### 3. Town Capital Appreciation Ranking, Decade by Decade")
    st.markdown(
        "Are today's premium towns (Queenstown, Bishan, Bukit Timah) consistent long-term winners, "
        "or is town leadership cyclical across market regimes?"
    )

    df_towns = fetch_town_ranking_data()
    decades = ["1990s", "2000s", "2010s", "2020s"]
    chosen_decade = st.segmented_control("Select Market Decade:", decades, default="2020s")

    decade_df = df_towns[df_towns["decade"] == chosen_decade].sort_values("rank_in_decade")

    if not decade_df.empty:
        top3 = decade_df.head(3).to_dict("records")
        p1, p2, p3 = st.columns(3)
        ranks = [
            "Rank 1: Highest Growth Rate",
            "Rank 2: Capital Growth",
            "Rank 3: Capital Growth",
        ]
        cols = [p1, p2, p3]

        for i in range(min(3, len(top3))):
            with cols[i]:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-label">{ranks[i]}</div>
                        <div class="metric-value">{top3[i]['town']}</div>
                        <div class="metric-delta delta-up">+{top3[i]['decade_growth_pct']:.1f}% Price/sqm Gain (${top3[i]['decade_start_psm']:,.0f} → ${top3[i]['decade_end_psm']:,.0f})</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        fig_rank = px.bar(
            decade_df.sort_values("decade_growth_pct", ascending=True),
            x="decade_growth_pct",
            y="town",
            orientation="h",
            color="decade_growth_pct",
            color_continuous_scale="Blues",
            text="decade_growth_pct",
            labels={"decade_growth_pct": "Decade Growth (%)", "town": "Housing Estate"},
        )
        fig_rank.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig_rank.update_layout(coloraxis_showscale=False, showlegend=False)
        apply_chart_theme(fig_rank, height=650)

        st.markdown(f"""
        <div class="chart-wrap">
            <div class="chart-title">Capital Appreciation Leaderboard: {chosen_decade}</div>
            <div class="chart-subtitle">Calculated via decade start vs end price-per-sqm endpoints</div>
        """, unsafe_allow_html=True)
        st.plotly_chart(fig_rank, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

        t_rows = ""
        for _, row in decade_df.iterrows():
            prev_r = f"#{int(row['prev_decade_rank'])}" if pd.notna(row['prev_decade_rank']) else "—"
            traj_badge = "badge-neutral"
            if "RISING" in str(row['trajectory']):
                traj_badge = "badge-green"
            elif "FALLING" in str(row['trajectory']):
                traj_badge = "badge-red"
            elif "NEW" in str(row['trajectory']):
                traj_badge = "badge-blue"
            elif "STABLE" in str(row['trajectory']):
                traj_badge = "badge-amber"

            growth_color = "#16a34a" if row['decade_growth_pct'] > 0 else "#dc2626"
            t_rows += f"""<tr><td><strong>#{row['rank_in_decade']}</strong></td><td><strong>{row['town']}</strong></td><td>${row['decade_start_psm']:,.0f}</td><td>${row['decade_end_psm']:,.0f}</td><td style="color: {growth_color}; font-weight: 700;">{row['decade_growth_pct']:+.1f}%</td><td>{row['total_decade_transactions']:,}</td><td>{prev_r}</td><td><span class="badge {traj_badge}">{row['trajectory']}</span></td></tr>"""

        render_html_table(
            ["Rank", "Estate / Town", "Decade Start PSM", "Decade End PSM", "Appreciation (%)", "Volume", "Prior Rank", "Trajectory"],
            t_rows
        )


# -----------------------------------------------------------------------------
# TAB 4: Price-per-sqm Normalization & Vertical Height Premiums
# -----------------------------------------------------------------------------
with tab4:
    st.markdown("### 4. Size Normalization & Vertical Storey Height Premiums")
    st.markdown(
        "Raw lump-sum resale prices can distort long-term trends because flats built in the 1990s were significantly larger than flats built in the 2020s. "
        "Normalizing to price-per-sqm reveals the true valuation and isolates the vertical height premium."
    )

    df_shrink, df_storeys = fetch_size_and_storeys_data()

    st.markdown("#### Part A: The Flat Size Era Comparison (1990s vs 2020s)")
    fig_shrink = px.bar(
        df_shrink,
        x="flat_type",
        y="avg_floor_area_sqm",
        color="decade",
        barmode="group",
        text="avg_floor_area_sqm",
        labels={"avg_floor_area_sqm": "Avg Floor Area (sqm)", "flat_type": "Flat Type", "decade": "Decade"},
        color_discrete_sequence=["#1e40af", "#3b82f6", "#60a5fa", "#93c5fd"],
    )
    fig_shrink.update_traces(texttemplate="%{text:.1f} m²", textposition="outside")
    apply_chart_theme(fig_shrink, height=360)

    st.markdown("""
    <div class="chart-wrap">
        <div class="chart-title">Average Floor Area (sqm) by Flat Type Across Four Decades</div>
        <div class="chart-subtitle">5-Room flats contracted by -5.3% (124.2m² → 117.6m²), while 4-Room flats contracted by -1.9%</div>
    """, unsafe_allow_html=True)
    st.plotly_chart(fig_shrink, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("#### Part B: The Vertical Storey Height Premium (2020–2026 Market Regimes)")
    storeys_flat = st.segmented_control(
        "Select Flat Type for Storey Premium Analysis:",
        ["4 ROOM", "3 ROOM", "5 ROOM"],
        default="4 ROOM",
    )
    sub_storeys = df_storeys[df_storeys["flat_type"] == storeys_flat]

    col_st1, col_st2 = st.columns([6, 6])
    with col_st1:
        fig_vert = px.bar(
            sub_storeys,
            x="floor_tier",
            y="median_psm",
            color="floor_tier",
            text="median_psm",
            labels={"floor_tier": "Floor Tier", "median_psm": "Median Price/sqm ($)"},
            color_discrete_sequence=["#64748b", "#3b82f6", "#2563eb", "#1d4ed8"],
        )
        fig_vert.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
        fig_vert.update_layout(showlegend=False)
        apply_chart_theme(fig_vert, height=380)

        st.markdown("""
        <div class="chart-wrap">
            <div class="chart-title">Price-per-sqm Across Floor Heights</div>
            <div class="chart-subtitle">Sky tier units command an exceptional premium over lower floors</div>
        """, unsafe_allow_html=True)
        st.plotly_chart(fig_vert, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    with col_st2:
        s_rows = ""
        for _, r in sub_storeys.iterrows():
            prem_str = f"+{r['storey_premium_vs_low_floor_pct']:.1f}%" if r['storey_premium_vs_low_floor_pct'] > 0 else "Baseline"
            step_str = f"+${r['marginal_step_psm_gain']:,.0f}" if pd.notna(r['marginal_step_psm_gain']) else "—"

            s_rows += f"""<tr><td><strong>{r['floor_tier']}</strong></td><td>{r['transaction_count']:,}</td><td>${r['median_raw_price']:,.0f}</td><td><strong>${r['median_psm']:,.0f}</strong></td><td style="color: #16a34a; font-weight: 700;">{prem_str}</td><td>{step_str}</td></tr>"""

        render_html_table(
            ["Floor Tier", "Transactions", "Median Price", "Median PSM", "Premium vs Low", "Marginal Step Gain"],
            s_rows
        )


# -----------------------------------------------------------------------------
# TAB 5: Policy Cooling Measures & Macro Events
# -----------------------------------------------------------------------------
with tab5:
    st.markdown("### 5. Macro Policy Cooling Measures & Market Causality (2013–2022)")
    st.markdown(
        "Singapore has implemented successive rounds of cooling measures to curb real estate speculation and ensure housing affordability. "
        "Here we measure transaction volume and price-per-sqm responses across a **12-month pre-event vs 12-month post-event** window."
    )

    df_policy = fetch_policy_impact_data()

    fig_policy = go.Figure()
    fig_policy.add_trace(go.Bar(
        x=df_policy["event_name"],
        y=df_policy["volume_change_pct"],
        name="12-Month Volume Change (%)",
        marker_color="#dc2626",
        text=[f"{v:+.1f}%" for v in df_policy["volume_change_pct"]],
        textposition="auto",
    ))
    fig_policy.add_trace(go.Bar(
        x=df_policy["event_name"],
        y=df_policy["psm_change_pct"],
        name="12-Month Price/sqm Change (%)",
        marker_color="#2563eb",
        text=[f"{v:+.1f}%" for v in df_policy["psm_change_pct"]],
        textposition="auto",
    ))

    fig_policy.update_layout(
        title="12-Month Pre vs Post Regulatory Impact on Resale Volume & Pricing",
        xaxis_title="Policy Measure / Macro Shock",
        yaxis_title="Change (%)",
        barmode="group",
    )
    apply_chart_theme(fig_policy, height=420)

    st.markdown("""
    <div class="chart-wrap">
        <div class="chart-title">Market Response Across 5 Historical Interventions</div>
        <div class="chart-subtitle">Notice how TDSR in 2013 successfully cooled prices, whereas post-2020 pandemic supply shortages led to continued price increases despite cooling attempts</div>
    """, unsafe_allow_html=True)
    st.plotly_chart(fig_policy, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

    pol_rows = ""
    for _, r in df_policy.iterrows():
        b_class = "badge-green" if "COOLING EFFECTIVE" in r['market_response'] else "badge-amber"
        v_col = "#dc2626" if r['volume_change_pct'] < 0 else "#16a34a"
        p_col = "#dc2626" if r['psm_change_pct'] < 0 else "#16a34a"
        pol_rows += f"""<tr><td><strong>#{r['event_id']}</strong></td><td><strong>{r['event_name']}</strong></td><td>{r['event_month']}</td><td>{r['pre_volume_12m']:,} → {r['post_volume_12m']:,}</td><td style="color: {v_col}; font-weight: 700;">{r['volume_change_pct']:+.1f}%</td><td>${r['pre_median_psm']:,.0f} → ${r['post_median_psm']:,.0f}</td><td style="color: {p_col}; font-weight: 700;">{r['psm_change_pct']:+.1f}%</td><td><span class="badge {b_class}">{r['market_response']}</span></td></tr>"""

    render_html_table(
        ["ID", "Policy Event", "Effective Month", "12M Volume Shift", "Volume Change", "12M PSM Shift", "PSM Change", "Market Regime Response"],
        pol_rows
    )

# -----------------------------------------------------------------------------
# 6. Institutional Footer
# -----------------------------------------------------------------------------
st.write("")
st.markdown("---")
f_left, f_right = st.columns([8, 4])
with f_left:
    st.markdown("""
    <div style="font-size: 0.76rem; color: var(--text-color); opacity: 0.7; line-height: 1.5;">
        <strong>Data Lineage:</strong> Official Singapore Public Housing resale transaction records (1990–2026) from <a href="https://data.gov.sg" target="_blank" style="color: #2563eb;">Data.gov.sg</a> under the Singapore Open Data Licence.<br>
        <strong>Architecture:</strong> Single PostgreSQL 16 table (<code>resale_prices</code>) optimized with 4 B-tree composite indexes, queried directly with zero intermediate caching pipelines.
    </div>
    """, unsafe_allow_html=True)
with f_right:
    st.markdown("""
    <div style="font-size: 0.76rem; color: var(--text-color); opacity: 0.55; text-align: right;">
        <em>Future Feature: Natural Language Data Querying via Gemini NLQ</em>
    </div>
    """, unsafe_allow_html=True)
