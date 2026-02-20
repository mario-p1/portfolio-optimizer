import pandas as pd
import streamlit as st
import yfinance as yf
import plotly.express as px


@st.cache_data
def check_ticker_exists(ticker: str) -> bool:
    if "longName" in yf.Ticker(ticker).get_info().keys():
        return True

    return False


@st.cache_data
def get_price_history(ticker: str) -> pd.DataFrame:
    yticker = yf.Ticker(ticker)

    history_df = yticker.history(period="max")
    return history_df


def downsample_df(df: pd.DataFrame, factor: int = 15) -> pd.DataFrame:
    return df.iloc[range(0, len(df), factor)].copy()


@st.cache_data
def get_ticker_details(ticker):
    data = yf.Ticker(ticker).get_info()

    return data["longName"], data["currency"]


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

    if check_ticker_exists(ticker):
        portfolio_items.append({"ticker": ticker, "allocation": allocation})
    else:
        st.error(f"Ticker {ticker} does not exist")
        st.stop()

portfolio_df = pd.DataFrame.from_dict(portfolio_items)

if portfolio_df["allocation"].sum() != 100:
    st.error("Sum of allocation accross all assets must be 100")
    st.stop()

"## Growth of 10.000 € Investment"
# "### Performance of 10.000 € Invested in Each Asset"

prices_df = pd.DataFrame()

# TODO: Rewrite using portfolio df
for i in range(st.session_state["n_tickers"]):
    ticker_key = f"ticker_{i}"
    if st.session_state[ticker_key]:
        ticker = st.session_state[ticker_key]
        history = get_price_history(ticker)["Close"].to_frame()

        name, currency = get_ticker_details(ticker)

        prices_df = prices_df.merge(
            history["Close"], left_index=True, right_index=True, how="outer"
        ).rename(columns={"Close": name})

        # f"#### {name}"
        # indv_chart_df = history["Close"] * 10_000 / history.iloc[0]["Close"]
        # st.line_chart(downsample_df(indv_chart_df))

"### Comparative Asset Performance"
"""Each asset receives 10.000 €, invested at the same time,
beginning from the newest fund's starting date."""
indv_growth_df = prices_df.dropna(how="any")
indv_growth_df = downsample_df(indv_growth_df)
for column in indv_growth_df.columns:
    shares_10k = (
        10_000 / indv_growth_df.loc[indv_growth_df[column].first_valid_index(), column]
    )
    indv_growth_df[column] = indv_growth_df[column] * shares_10k
indv_growth_df = indv_growth_df.round(0)

st.line_chart(indv_growth_df, y_label=f"Portfolio Value ({currency})")

"## Portfolio"
"### Assets"
fig = px.pie(portfolio_df, values="allocation", names="ticker", hole=0.3)
fig.update_traces(textinfo="label+percent")
st.plotly_chart(fig)
