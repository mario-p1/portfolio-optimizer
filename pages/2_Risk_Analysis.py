import plotly.express as px
import streamlit as st

from market_data_service import get_prices_df
from portfolio_metrics import (
    compute_drawdown,
    compute_downside_deviation,
    compute_max_drawdown,
    compute_portfolio_growth_index,
    compute_rolling_volatility,
)
from utils import fig_layout, rename_ticker_columns_to_names

"# Portfolio Optimizer"

"## Risk Analysis"

# Load state
portfolio_df = st.session_state.portfolio_df
prices_df = get_prices_df(portfolio_df["ticker"].tolist())

portfolio_growth_df = compute_portfolio_growth_index(prices_df, portfolio_df)

# ---------------------------------------------------------------------------
# Rolling Volatility
# ---------------------------------------------------------------------------
"### Rolling Volatility"
"""Annualized rolling standard deviation of monthly portfolio returns,
shown for 6-month and 12-month windows."""

rolling_vol_df = compute_rolling_volatility(portfolio_growth_df, windows=[6, 12])
fig = px.line(
    rolling_vol_df,
    labels={"variable": "Window", "value": "Annualized Volatility (%)"},
)
fig.update_layout(**fig_layout)
st.plotly_chart(fig)

# ---------------------------------------------------------------------------
# Maximum Drawdown
# ---------------------------------------------------------------------------
"### Maximum Drawdown"
"""Drawdown measures the decline from a portfolio's historical peak.
The chart shows the drawdown at each point in time."""

drawdown_df = compute_drawdown(portfolio_growth_df)
max_drawdown = compute_max_drawdown(portfolio_growth_df)

fig = px.area(
    drawdown_df,
    y="drawdown",
    labels={"drawdown": "Drawdown (%)", "date": "Date"},
    color_discrete_sequence=["red"],
)
fig.update_layout(**fig_layout, showlegend=False)
st.plotly_chart(fig)

st.metric(label="Maximum Drawdown", value=f"-{max_drawdown:.2f}%")

# ---------------------------------------------------------------------------
# Asset Correlation Matrix
# ---------------------------------------------------------------------------
"### Asset Correlation Matrix"
"""Pearson correlation of monthly returns between all assets in the portfolio."""

corr_df = (
    rename_ticker_columns_to_names(prices_df, portfolio_df)
    .pct_change()
    .corr()
    .round(2)
)

fig = px.imshow(
    corr_df,
    text_auto=True,
    color_continuous_scale="RdBu_r",
    zmin=-1,
    zmax=1,
)
fig.update_layout(**fig_layout)
st.plotly_chart(fig)

# ---------------------------------------------------------------------------
# Summary Risk Metrics
# ---------------------------------------------------------------------------
"### Summary Risk Metrics"

avg_vol = rolling_vol_df.mean().mean()
downside_dev = compute_downside_deviation(portfolio_growth_df)

col1, col2, col3 = st.columns(3)
col1.metric(label="Avg. Annualized Volatility", value=f"{avg_vol:.2f}%")
col2.metric(label="Maximum Drawdown", value=f"-{max_drawdown:.2f}%")
col3.metric(label="Downside Deviation (ann.)", value=f"{downside_dev:.2f}%")
