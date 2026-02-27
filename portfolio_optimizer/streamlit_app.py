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


if "tickers" not in st.session_state:
    st.session_state.tickers = "IUSQ.DE;EUNL.DE;IUSN.DE;EUNM.DE"
    st.session_state["allocation_IUSQ.DE"] = 50
    st.session_state["allocation_EUNL.DE"] = 30
    st.session_state["allocation_IUSN.DE"] = 10
    st.session_state["allocation_EUNM.DE"] = 10

portfolio_items = []
for i, item in enumerate(st.session_state.tickers.split(";")):
    try:
        ticker_data = get_ticker_details(item)
        portfolio_items.append({"ticker": item, **ticker_data})
    except Exception as e:
        st.error(e)
        st.stop()

portfolio_df = pd.DataFrame.from_dict(portfolio_items)

"# Portfolio Optimizer"

"## Portfolio Configuration"

st.text_input("Tickers present in your portfolio (separated by ';')", key="tickers")

columns = st.columns(2)

for item in portfolio_df.itertuples():
    col = columns[item.Index % 2]
    with col:
        st.number_input(
            f"Allocation of '{item.ticker}' (%)",
            min_value=0,
            max_value=100,
            key=f"allocation_{item.ticker}",
        )


portfolio_df["allocation"] = portfolio_df["ticker"].map(
    lambda ticker: st.session_state[f"allocation_{ticker}"]
)

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
annual_returns_df = port_perf_df.resample("YE").last().pct_change().dropna() * 100
annual_returns_df.columns = ["annual_return"]
annual_returns_df["Sign"] = (
    annual_returns_df["annual_return"].ge(0).map({True: "Positive", False: "Negative"})
)


fig = px.bar(
    annual_returns_df,
    color="Sign",
    color_discrete_map={"Positive": "green", "Negative": "red"},
    labels={"Date": "Year", "value": "Annual Return Rate (%)"},
)
fig.update_layout(showlegend=False)
st.plotly_chart(fig)


"### Annual Returns Count"
bin_by = 5
min_annual_return = int(annual_returns_df["annual_return"].min() / bin_by - 1) * bin_by
max_annual_return = int(annual_returns_df["annual_return"].max() / bin_by + 1) * bin_by

bin_region = max(abs(min_annual_return), abs(max_annual_return))

bins = list(range(-bin_region, bin_region + bin_by, bin_by))

annual_bins = (
    pd.cut(annual_returns_df["annual_return"], bins=bins, labels=bins[:-1])
    .value_counts()
    .sort_index()
    .to_frame()
    .reset_index()
)

annual_bins["sign"] = (
    annual_bins["annual_return"].ge(0).map({True: "Positive", False: "Negative"})
)
annual_bins["label"] = annual_bins["annual_return"].map(
    lambda x: f"{x} to {x + bin_by} %"
)


fig = px.bar(
    annual_bins,
    x="label",
    y="count",
    color="sign",
    color_discrete_map={"Positive": "green", "Negative": "red"},
    labels={"count": "Number of Years", "label": "Annual Return Range (%)"},
)


fig.update_layout(showlegend=False)

st.plotly_chart(fig)
