import streamlit as st

from market_data_service import get_prices_df
from utils import ensure_portfolio_configured

ensure_portfolio_configured()
portfolio_df = st.session_state.portfolio_df

"# Portfolio Optimizer - Returns Analysis"
"## Drawdown"

prices_df = get_prices_df(portfolio_df["ticker"].tolist()).dropna(how="any")
drawdown_df = prices_df.copy()

st.write(drawdown_df)
