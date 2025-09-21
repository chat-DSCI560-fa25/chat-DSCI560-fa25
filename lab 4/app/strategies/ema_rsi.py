import pandas as pd
import pandas_ta as ta

def generate_signals(df, params: dict):
    """
    Trading strategy based on RSI and a fast/slow EMA crossover.
    - Buy when RSI is below 45 and the fast EMA crosses above the slow EMA.
    - Sell when RSI is above 65.
    """
    
    df.ta.ema(length=10, append=True) # Fast EMA
    df.ta.ema(length=30, append=True) # Slow EMA
    df.ta.rsi(length=14, append=True)
    df.dropna(inplace=True)

 
    df.rename(columns={
        'EMA_10': 'ema_10',
        'EMA_30': 'ema_30',
        'RSI_14': 'rsi_14'
    }, inplace=True)

    df['signal'] = 0
    buy_condition = (df['rsi_14'] < 45) & (df['ema_10'] > df['ema_30'])
    sell_condition = (df['rsi_14'] > 65)

    df.loc[buy_condition, 'signal'] = 1  # Buy
    df.loc[sell_condition, 'signal'] = -1 # Sell

    return df[['dt', 'signal', 'close', 'rsi_14']]