import pandas as pd

from portfolio_optimizer.config import EURIBOR_3M_PATH


def load_risk_free_rates():
    df = pd.read_csv(EURIBOR_3M_PATH, usecols=[0, 2], parse_dates=[0])
    df.columns = ["date", "annual_rate"]
    df = df.resample("ME", on="date").last()

    df["annual_rate"] = df["annual_rate"].div(100)

    df["monthly_rate"] = (1 + df["annual_rate"]) ** (1 / 12) - 1
    return df
