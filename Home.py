import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from portfolio_analyzer.market_data_service import get_prices_df, get_ticker_details
from portfolio_analyzer.metrics import calculate_return_rates, compute_portfolio_growth
from portfolio_analyzer.utils import rename_ticker_columns_to_names

"# Portfolio Analyzer"
"## Disclaimer"
"""This project is a **experimental tool** created for learning and demonstration purposes.

**It is not intended for production use or real financial decision-making.**

The models and results provided may be simplified and are not guaranteed to be accurate.
Use at your own risk.
"""

"## Overview"
"""
Portfolio Analyzer helps you assess your portfolio's risk and return.

Start by configuring your portfolio: enter the tickers of your assets and their allocations.
Next, explore the tabs on the left sidebar to analyze performance and risk.
Use Monte Carlo simulations to forecast future performance and optimize your portfolio composition.
"""

"# Portfolio Configuration"
"""
Configure your portfolio by entering its assets and their allocations.
All analyses and results throughout the app will use this setup.

- **Ticker**: The asset's ticker symbol (Yahoo Finance format, e.g., `AAPL`, `IUSQ.DE`).
- **Allocation (%)**: The percentage of your portfolio for each asset.
All allocations must add up to 100%.

Note: You can add or remove assets dynamically.
The app will automatically fetch asset details and validate your inputs.
"""
portfolio_df = st.session_state.get(
    "portfolio_df",
    pd.DataFrame(
        {
            "ticker": ["IUSQ.DE", "EUNL.DE", "IUSN.DE", "EUNM.DE"],
            "allocation": [50, 30, 10, 10],
        }
    ),
)
portfolio_df.index = pd.RangeIndex(start=1, stop=len(portfolio_df) + 1, step=1)

new_portfolio_df = st.data_editor(
    portfolio_df[["ticker", "allocation"]],
    num_rows="dynamic",
    column_config={
        "ticker": st.column_config.TextColumn("Ticker"),
        "allocation": st.column_config.NumberColumn(
            "Allocation (%)", min_value=0, max_value=100, step=1
        ),
    },
)

portfolio_df = new_portfolio_df.copy()

if portfolio_df["allocation"].sum() != 100:
    st.error(
        f"Sum of allocation accross all assets must be 100, current sum is: {portfolio_df['allocation'].sum()}"
    )
    st.stop()

try:
    portfolio_df["name"] = portfolio_df["ticker"].apply(
        lambda x: get_ticker_details(x)["name"]
    )
    portfolio_df["currency"] = portfolio_df["ticker"].apply(
        lambda x: get_ticker_details(x)["currency"]
    )
except Exception as e:
    st.error(str(e))
    st.stop()

st.session_state["portfolio_df"] = portfolio_df

"# Portfolio Summary"
"## Asset Allocation"
"""The pie chart below shows the allocation of your portfolio across different assets."""

# portfolio pie chart
fig = px.pie(portfolio_df, values="allocation", names="name", hole=0.3)
fig.update_traces(textinfo="label+percent")
fig.update_layout(showlegend=False)
st.plotly_chart(fig)

"## Asset Correlations"
prices_df = get_prices_df(portfolio_df["ticker"].tolist())

monthly_prices_df = prices_df.resample("ME").last()

portfolio_growth_df = compute_portfolio_growth(
    monthly_prices_df, portfolio_df, normalize_value=10_000
).round(0)

indv_growth_df = portfolio_growth_df[portfolio_df["ticker"]]
indv_growth_df = rename_ticker_columns_to_names(indv_growth_df, portfolio_df)

for col in indv_growth_df.columns:
    indv_growth_df[col] = calculate_return_rates(indv_growth_df[col])["return"]

corr_df = indv_growth_df.corr()

fig = px.imshow(corr_df)

st.plotly_chart(fig)
