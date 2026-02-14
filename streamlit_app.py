import pandas as pd
import streamlit as st
import yfinance as yf


@st.cache_data
def get_price_history(ticker: str) -> pd.DataFrame:
    yticker = yf.Ticker(ticker)

    history_df = yticker.history(period="max")
    return history_df


def downsample_df(df: pd.DataFrame, factor: int = 15) -> pd.DataFrame:
    return df.iloc[range(0, len(df), factor)].copy()


if "n_tickers" not in st.session_state:
    st.session_state.n_tickers = 2
    st.session_state.ticker_0 = "VWCE.DE"
    st.session_state.allocation_0 = 90
    st.session_state.ticker_1 = "IUSN.DE"
    st.session_state.allocation_1 = 10

st.title("Portfolio Optimizer")

st.header("Portfolio Configuration")
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

allocation_sum = sum(
    [st.session_state[f"allocation_{i}"] for i in range(st.session_state.n_tickers)]
)
if allocation_sum != 100:
    st.error("Sum of allocation accross all assets must be 100")

st.header("Growth of 10.000 € Investment")
st.subheader("Performance of 10.000 € Invested in Each Asset")
for i in range(st.session_state["n_tickers"]):
    ticker_key = f"ticker_{i}"
    if st.session_state[ticker_key]:
        history = get_price_history(st.session_state[ticker_key])
        factor_10k = 10_000 / history.iloc[0]["Close"]
        history["Close"] = (history["Close"] * factor_10k).round(0)

        yt = yf.Ticker(st.session_state[ticker_key])

        st.write(yt.get_info()["longName"])
        currency = yt.get_info()["currency"]
        st.line_chart(
            downsample_df(history), y="Close", y_label=f"Portfolio Value ({currency})"
        )
