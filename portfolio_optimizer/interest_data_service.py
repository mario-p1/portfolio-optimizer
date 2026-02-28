import pandas as pd

from portfolio_optimizer.config import EURIBOR_3M_PATH


def load_risk_free_rates():
    df = pd.read_csv(EURIBOR_3M_PATH, usecols=[0, 2], parse_dates=[0])
    df.columns = ["date", "value"]
    df = df.resample("ME", on="date").last()
    return df
