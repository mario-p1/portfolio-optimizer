import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from portfolio_analyzer.market_data_service import get_ticker_details

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

if st.session_state.get("portfolio_df") is not None:
    portfolio_df = st.session_state.portfolio_df
else:
    portfolio_df = pd.DataFrame(
        {
            "ticker": ["IUSQ.DE", "EUNL.DE", "IUSN.DE", "EUNM.DE"],
            "name": [np.nan] * 4,
            "currency": [np.nan] * 4,
            "allocation": [50, 30, 10, 10],
        }
    )

new_portfolio_df = st.data_editor(
    portfolio_df,
    num_rows="dynamic",
    column_config={
        "ticker": st.column_config.TextColumn("Ticker"),
        "name": st.column_config.TextColumn("Name", disabled=True),
        "currency": st.column_config.TextColumn("Currency", disabled=True),
        "allocation": st.column_config.NumberColumn(
            "Allocation (%)", min_value=0, max_value=100, step=1
        ),
    },
)

try:
    new_portfolio_df["name"] = new_portfolio_df["ticker"].apply(
        lambda x: get_ticker_details(x)["name"] if pd.notna(x) else np.nan
    )
    new_portfolio_df["currency"] = new_portfolio_df["ticker"].apply(
        lambda x: get_ticker_details(x)["currency"] if pd.notna(x) else np.nan
    )
except Exception as e:
    st.error(str(e))
    st.stop()

if new_portfolio_df["allocation"].sum() != 100:
    st.error(
        f"Sum of allocation accross all assets must be 100, current sum is: {new_portfolio_df['allocation'].sum()}"
    )
    st.stop()

st.session_state["portfolio_df"] = new_portfolio_df

if not portfolio_df.equals(new_portfolio_df):
    st.rerun()

"# Portfolio Summary"
"## Asset Allocation"
"""The pie chart below shows the allocation of your portfolio across different assets."""

# portfolio pie chart
fig = px.pie(portfolio_df, values="allocation", names="name", hole=0.3)
fig.update_traces(textinfo="label+percent")
fig.update_layout(showlegend=False)
st.plotly_chart(fig)
