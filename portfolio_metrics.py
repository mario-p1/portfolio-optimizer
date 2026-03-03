from datetime import datetime

import pandas as pd

from utils import rename_ticker_columns_to_names


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
        (portfolio_growth_df * allocation).sum(axis=1).to_frame(name="portfolio_value")
    )

    portfolio_growth_df = (
        portfolio_growth_df * 10_000 / portfolio_growth_df.iloc[0]
    ).round(0)

    return portfolio_growth_df


def bin_annual_returns(annual_returns_df: pd.DataFrame, bin_by: int) -> pd.DataFrame:
    min_annual_return = (
        int(annual_returns_df["annual_return"].min() / bin_by - 1) * bin_by
    )
    max_annual_return = (
        int(annual_returns_df["annual_return"].max() / bin_by + 1) * bin_by
    )

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
        annual_bins["annual_return"].ge(0).map({True: "positive", False: "negative"})
    )
    annual_bins["label"] = annual_bins["annual_return"].map(
        lambda x: f"{x} to {x + bin_by} %"
    )

    return annual_bins


def compute_annual_excess_returns(
    annual_returns_df: pd.DataFrame,
    interest_rates_df: pd.DataFrame,
    current_year: int = datetime.now().year,
) -> pd.DataFrame:
    annual_rates_df = annual_returns_df.copy().rename(
        columns={"annual_return": "portfolio_return"}
    )
    annual_rates_df["portfolio_return"] = annual_rates_df["portfolio_return"].div(100)

    annual_rates_df = annual_rates_df.join(interest_rates_df, how="inner").dropna()
    annual_rates_df["excess_return_rate"] = (
        annual_rates_df["portfolio_return"] - annual_rates_df["risk_free_annual_rate"]
    )

    annual_rates_df = annual_rates_df[annual_rates_df.index.year < current_year]

    return annual_rates_df


def compute_sharpe_ratio(annual_rates_df: pd.DataFrame) -> float:
    return (
        annual_rates_df["excess_return_rate"].mean()
        / annual_rates_df["excess_return_rate"].std()
    )


def compute_rolling_volatility(
    portfolio_growth_df: pd.DataFrame,
    windows: list[int] = (6, 12),
) -> pd.DataFrame:
    """Compute annualized rolling volatility of monthly portfolio returns.

    windows: rolling window sizes in months.
    Annualisation factor for monthly returns is sqrt(12).
    """
    monthly_returns = portfolio_growth_df["portfolio_value"].pct_change().dropna()
    vol_df = pd.DataFrame(index=monthly_returns.index)
    for w in windows:
        vol_df[f"{w}m rolling volatility"] = (
            monthly_returns.rolling(w).std() * (12**0.5) * 100
        )
    return vol_df.dropna(how="all")


def compute_drawdown(portfolio_growth_df: pd.DataFrame) -> pd.DataFrame:
    """Compute drawdown (%) from the running peak of portfolio value."""
    values = portfolio_growth_df["portfolio_value"]
    rolling_max = values.cummax()
    drawdown = (values - rolling_max) / rolling_max * 100
    return drawdown.to_frame(name="drawdown")


def compute_max_drawdown(portfolio_growth_df: pd.DataFrame) -> float:
    """Return the maximum drawdown (%) as a positive percentage."""
    return abs(compute_drawdown(portfolio_growth_df)["drawdown"].min())


def compute_downside_deviation(portfolio_growth_df: pd.DataFrame) -> float:
    """Compute annualized downside deviation from monthly portfolio returns."""
    monthly_returns = portfolio_growth_df["portfolio_value"].pct_change().dropna()
    negative_returns = monthly_returns[monthly_returns < 0]
    if negative_returns.empty:
        return 0.0
    return float((negative_returns**2).mean() ** 0.5 * (12**0.5) * 100)
