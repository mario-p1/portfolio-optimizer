import pandas as pd

from portfolio_optimizer.utils import rename_ticker_columns_to_names


def compute_asset_growth_index(
    prices_df: pd.DataFrame, portfolio_df: pd.DataFrame
) -> pd.DataFrame:
    indv_growth_df = prices_df.dropna(how="any")
    indv_growth_df = rename_ticker_columns_to_names(indv_growth_df, portfolio_df)
    indv_growth_df = (indv_growth_df * 10_000 / indv_growth_df.iloc[0]).round(0)

    return indv_growth_df


def compute_portfolio_growth_index(
    prices_df: pd.DataFrame, portfolio_df: pd.DataFrame
) -> pd.DataFrame:
    portfolio_growth_df = prices_df.dropna(how="any")

    allocation = (portfolio_df.set_index("ticker")["allocation"] / 100).sort_values(
        ascending=True
    )
    portfolio_growth_df = (
        (portfolio_growth_df * allocation).sum(axis=1).to_frame(name="Portfolio Value")
    )
    portfolio_growth_df = (
        portfolio_growth_df * 10_000 / portfolio_growth_df.iloc[0]
    ).round(0)

    return portfolio_growth_df
