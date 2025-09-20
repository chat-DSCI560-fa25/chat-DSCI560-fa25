import pandas as pd

def generate_signals(data: pd.DataFrame, params: dict):

    short_window = int(params.get("short", 10))
    long_window = int(params.get("long", 30))

    signals = data.copy()

    signals.fillna(method='ffill', inplace=True)

    # --- 2. Indicator Calculation ---
    signals['sma_short'] = signals['close'].rolling(window=short_window, min_periods=1).mean()
    signals['sma_long'] = signals['close'].rolling(window=long_window, min_periods=1).mean()


    signals['position'] = 0
    signals.loc[signals['sma_short'] > signals['sma_long'], 'position'] = 1

  
    signals['signal'] = signals['position'].diff()

    return signals