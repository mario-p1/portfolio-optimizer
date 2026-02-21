import pandas as pd


def replace_tickers_columns(df: pd.DataFrame, ticker_df: pd.DataFrame) -> pd.DataFrame:
    names_dict = ticker_df.set_index("ticker")["name"].to_dict()
    return df.rename(columns=names_dict)
