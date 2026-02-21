import pandas as pd
import plotly.express as px
import streamlit as st

from portfolio_optimizer.market_data_service import get_prices_df, get_ticker_details
from portfolio_optimizer.portfolio_metrics import (
    compute_asset_growth_index,
    compute_portfolio_growth_index,
)

fig_layout = {
    "hovermode": "x unified",
    "legend": {
        "title": "",
        "orientation": "h",
        "yanchor": "top",
        "y": -0.2,
        "xanchor": "center",
        "x": 0.5,
    },
}


if "n_tickers" not in st.session_state:
    st.session_state.n_tickers = 4

    st.session_state.ticker_0 = "IUSQ.DE"
    st.session_state.allocation_0 = 50
    st.session_state.ticker_1 = "EUNL.DE"
    st.session_state.allocation_1 = 30
    st.session_state.ticker_2 = "IUSN.DE"
    st.session_state.allocation_2 = 10
    st.session_state.ticker_3 = "EUNM.DE"
    st.session_state.allocation_3 = 10

"# Portfolio Optimizer"

"## Portfolio Configuration"
input_left_col, input_right_col = st.columns(2)
with input_left_col:
    for i in range(st.session_state.n_tickers):
        st.text_input("Ticker", key=f"ticker_{i}")
with input_right_col:
    for i in range(st.session_state.n_tickers):
        st.number_input(
            "Allocation (%)", min_value=0, max_value=100, key=f"allocation_{i}"
        )

if st.button("Add Asset"):
    st.session_state.n_tickers += 1
    st.rerun()


portfolio_items = []
for i in range(st.session_state.n_tickers):
    ticker = st.session_state[f"ticker_{i}"]
    allocation = st.session_state[f"allocation_{i}"]

    try:
        ticker_data = get_ticker_details(ticker)
        portfolio_items.append(
            {"ticker": ticker, "allocation": allocation, **ticker_data}
        )
    except Exception as e:
        st.error(e)
        st.stop()

portfolio_df = pd.DataFrame.from_dict(portfolio_items)

if portfolio_df["allocation"].sum() != 100:
    st.error("Sum of allocation accross all assets must be 100")
    st.stop()

"## Portfolio"
"### Assets"
# portfolio pie chart
fig = px.pie(portfolio_df, values="allocation", names="name", hole=0.3)
fig.update_traces(textinfo="label+percent")
fig.update_layout(showlegend=False)
st.plotly_chart(fig)

# portfolio df
st.dataframe(
    portfolio_df[["ticker", "name", "currency", "allocation"]], hide_index=True
)

"## Growth Index"

prices_df = get_prices_df(portfolio_df["ticker"].tolist())

"### Comparative Asset Performance"
"""Each asset receives 10.000 €, invested at the same time,
beginning from the newest fund's starting date."""
indv_perf_df = compute_asset_growth_index(prices_df, portfolio_df)

fig = px.line(indv_perf_df, labels={"variable": "Asset", "value": "Value"})
fig.update_layout(**fig_layout)

st.plotly_chart(fig)

"### Portfolio Performance"
"""Your portfolio receives 10.000 €, invested at the beggining from the newest fund's starting date.
The growth of the portfolio is calculated as the weighted average of the growth of each asset, according to the allocation you defined."""
port_perf_df = compute_portfolio_growth_index(prices_df, portfolio_df)
fig = px.line(port_perf_df)
fig.update_layout(**fig_layout, showlegend=False)

st.plotly_chart(fig)

"## Returns"
"### Annual Returns"
annual_returns_df = port_perf_df.resample("Y").last().pct_change().dropna() * 100
annual_returns_df.columns = ["annual_return"]
annual_returns_df["Sign"] = (
    annual_returns_df["annual_return"].ge(0).map({True: "Positive", False: "Negative"})
)


fig = px.bar(
    annual_returns_df,
    x=annual_returns_df.index.year,
    y="annual_return",
    labels={"x": "Year", "annual_return": "Annual Return (%)"},
    color="Sign",
    color_discrete_map={"Positive": "green", "Negative": "red"},
)
fig.update_layout(showlegend=False)
st.plotly_chart(fig)
