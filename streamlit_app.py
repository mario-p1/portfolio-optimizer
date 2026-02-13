import pandas as pd
import streamlit as st
import yfinance as yf


@st.cache_data
def get_price_history(ticker: str) -> pd.DataFrame:
    yticker = yf.Ticker(ticker)

    st.text(f"Ticker: {ticker}")
    history_df = yticker.history(period="max")
    return history_df


def downsample_df(df: pd.DataFrame, factor: int = 15) -> pd.DataFrame:
    return df.iloc[range(0, len(df), factor)].copy()


st.title("Portfolio Optimizer")


input_left_col, input_right_col = st.columns(2)

if "n_tickers" not in st.session_state:
    st.session_state.n_tickers = 1

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


for i in range(st.session_state["n_tickers"]):
    ticker_key = f"ticker_{i}"
    if st.session_state[ticker_key]:
        history = get_price_history(st.session_state[ticker_key])
        factor_10k = 10_000 / history.iloc[0]["Close"]
        history["Close"] = history["Close"] * factor_10k
        st.line_chart(downsample_df(history), y="Close")
