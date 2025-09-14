# preprocessing.py

import pandas as pd
import numpy as np

def preprocess_stock_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean, fill missing values, convert timestamps, and generate helpful metrics.
    Assumes columns: ['symbol', 'dt', 'open', 'high', 'low', 'close', 'volume']
    """
    if df.empty:
        return df

    # 1. Handle missing values
    price_cols = ['open', 'high', 'low', 'close']
    df[price_cols] = df[price_cols].fillna(method='ffill')
    df[price_cols] = df[price_cols].fillna(method='bfill')

    df['volume'] = df['volume'].fillna(0).astype(int)

    # 2. Convert "dt" to pandas datetime if needed
    if not pd.api.types.is_datetime64_any_dtype(df['dt']):
        df['dt'] = pd.to_datetime(df['dt'])

    # 3. Sort for correct order
    df = df.sort_values(['symbol', 'dt']).reset_index(drop=True)

    # 4. Daily returns: pct and log
    df['daily_return_pct'] = df.groupby('symbol')['close'].pct_change().fillna(0)
    df['daily_return_log'] = df.groupby('symbol')['close'].apply(lambda x: np.log(x / x.shift(1))).fillna(0)

    # 5. Rolling window metrics (5, 20 days)
    for window in [5, 20]:
        df[f'close_ma_{window}'] = df.groupby('symbol')['close'].transform(lambda x: x.rolling(window).mean())
        df[f'vol_ma_{window}'] = df.groupby('symbol')['volume'].transform(lambda x: x.rolling(window).mean())

    # 6. Daily volatility as percent
    df['daily_volatility_pct'] = ((df['high'] - df['low']) / df['open']).fillna(0)

    return df

# easy CSV export for results/checking
def export_to_csv(df: pd.DataFrame, filename: str):
    df.to_csv(filename, index=False)
