import pandas as pd
import streamlit as st
import yfinance as yf
import plotly.express as px


@st.cache_data
def get_ticker_details(ticker):
    data = yf.Ticker(ticker).get_info()

    if "longName" not in data.keys():
        raise ValueError(f"Ticker '{ticker}' doesn't exist.")

    return {"name": data["longName"], "currency": data["currency"]}


@st.cache_data
def get_price_history(ticker: str) -> pd.DataFrame:
    yticker = yf.Ticker(ticker)

    history_df = yticker.history(period="max", interval="1mo")
    return history_df


def get_prices_df(tickers: list[str]) -> pd.DataFrame:
    prices_df = pd.DataFrame()
    for ticker in tickers:
        history = get_price_history(ticker)["Close"].to_frame().reset_index(drop=False)
        history["Date"] = history["Date"].dt.date
        history = history.set_index("Date")

        prices_df = prices_df.merge(
            history["Close"], left_index=True, right_index=True, how="outer"
        ).rename(columns={"Close": ticker})

    return prices_df


def replace_tickers_columns(df: pd.DataFrame, ticker_df: pd.DataFrame) -> pd.DataFrame:
    names_dict = ticker_df.set_index("ticker")["name"].to_dict()
    return df.rename(columns=names_dict)


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

"## Growth of 10.000 € Investment"

prices_df = get_prices_df(portfolio_df["ticker"].tolist())

"### Comparative Asset Performance"
"""Each asset receives 10.000 €, invested at the same time,
beginning from the newest fund's starting date."""
indv_growth_df = prices_df.dropna(how="any")
indv_growth_df = replace_tickers_columns(indv_growth_df, portfolio_df)


for column in indv_growth_df.columns:
    shares_10k = 10_000 / indv_growth_df[column].iloc[0]
    indv_growth_df[column] = indv_growth_df[column] * shares_10k
indv_growth_df = indv_growth_df.round(0)

st.line_chart(indv_growth_df, y_label="Portfolio Value (€)")
