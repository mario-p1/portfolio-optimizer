import pandas as pd

from portfolio_optimizer.config import EURIBOR_3M_PATH


def load_interest_data():
    df = pd.read_csv(
        EURIBOR_3M_PATH, usecols=[0, 2], parse_dates=["DATE"], index_col="DATE"
    )
    df.columns = ["value"]

    return df
