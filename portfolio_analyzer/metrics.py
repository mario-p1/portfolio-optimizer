import math
from datetime import datetime

import pandas as pd
import streamlit as st
from scipy.stats import norm


def compute_portfolio_growth(
    prices_df: pd.DataFrame, portfolio_df: pd.DataFrame, normalize_value: int = 1
) -> pd.DataFrame:
    allocation = portfolio_df.set_index("ticker")["allocation"] / 100

    growth_df = prices_df.dropna(how="any")

    # Calculate asset growth
    growth_df = growth_df.div(growth_df.iloc[0])

    growth_df["portfolio_growth"] = (growth_df * allocation).sum(axis=1)

    growth_df = growth_df * normalize_value / growth_df.iloc[0]

    return growth_df


def calculate_return_rates(
    value_series: pd.Series, current_year: int = datetime.now().year
) -> pd.DataFrame:
    return_rates_df = (value_series.pct_change().dropna() * 100).to_frame(name="return")

    return_rates_df = return_rates_df[return_rates_df.index.year < current_year]

    return_rates_df["sign"] = (
        return_rates_df["return"].ge(0).map({True: "positive", False: "negative"})
    )

    return return_rates_df


def bin_series(
    series: pd.Series,
    bin_by: int,
    label_suffix: str = "",
    sign_threshold: float = 0,
    cutoff_bins: bool = True,
) -> pd.DataFrame:
    min_value = int(series.min() / bin_by - 1) * bin_by
    max_value = int(series.max() / bin_by + 1) * bin_by

    bin_region = max(abs(min_value), abs(max_value))

    bins = list(range(-bin_region, bin_region + bin_by, bin_by))

    bins_df = (
        pd.cut(series, bins=bins, labels=bins[:-1])
        .value_counts()
        .sort_index()
        .to_frame()
        .reset_index(names="bin_left")
    )

    bins_df["bin_left"] = bins_df["bin_left"].astype(int)
    if cutoff_bins:
        bins_df = bins_df[
            bins_df["bin_left"].ge(series.min() - bin_by)
            & bins_df["bin_left"].le(series.max() + bin_by)
        ]

    bins_df["sign"] = (
        bins_df["bin_left"]
        .ge(sign_threshold)
        .map({True: "positive", False: "negative"})
    )
    bins_df["label"] = bins_df["bin_left"].map(
        lambda x: f"{x} to {x + bin_by}{label_suffix}"
    )

    return bins_df


def compute_excess_returns(
    return_series: pd.Series,
    interest_rate_series: pd.Series,
    current_year: int = datetime.now().year,
) -> pd.DataFrame:
    excess_returns_df = return_series.to_frame(name="portfolio_return")
    excess_returns_df["risk_free_rate"] = interest_rate_series
    excess_returns_df["excess_return_rate"] = (
        excess_returns_df["portfolio_return"] - excess_returns_df["risk_free_rate"]
    )
    excess_returns_df = excess_returns_df[excess_returns_df.index.year < current_year]
    return excess_returns_df


def compute_sharpe_ratio(annual_rates_df: pd.DataFrame) -> float:
    return (
        annual_rates_df["excess_return_rate"].mean()
        / annual_rates_df["excess_return_rate"].std()
    )


def calculate_arr(return_series: pd.Series) -> float:
    """Annualized Return Rate"""
    n_years = len(return_series)
    return ((1 + return_series.div(100)).prod() ** (1 / n_years) - 1) * 100


def compute_drawdown_df(growth_series: pd.Series) -> pd.DataFrame:
    drawdown_df = growth_series.to_frame("growth")

    drawdown_df["max_to_date"] = drawdown_df["growth"].expanding().max()
    drawdown_df["drawdown"] = (
        (drawdown_df["growth"] - drawdown_df["max_to_date"])
        / drawdown_df["max_to_date"]
        * 100
    )

    drawdown_df = drawdown_df.resample("ME").min()

    return drawdown_df


def compute_value_at_risk(
    return_series: pd.Series, confidence_level: float = 0.95, scale: int = 1
) -> float:
    z_score = norm.ppf(confidence_level)
    return (
        scale * return_series.mean() - math.sqrt(scale) * z_score * return_series.std()
    ) * 100
