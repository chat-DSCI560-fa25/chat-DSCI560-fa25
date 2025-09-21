import pandas as pd
import pandas_ta as ta

def generate_signals(df, params: dict):
    """
    Generates trading signals for the Consensus Scoring
    """

    df.ta.macd(fast=12, slow=26, signal=9, append=True)
    df.ta.rsi(length=14, append=True)
    df.ta.sma(length=20, append=True)
    df.ta.sma(length=200, append=True)


    df.rename(columns={
        'MACD_12_26_9': 'macd_line',
        'MACDs_12_26_9': 'signal_line',
        'RSI_14': 'rsi_14',
        'SMA_20': 'sma_20'

    }, inplace=True)

    df['score'] = 0
    df.loc[df['macd_line'] > df['signal_line'], 'score'] += 1
    df.loc[df['rsi_14'] > 50, 'score'] += 1
    df.loc[df['close'] > df['sma_20'], 'score'] += 1
    
    df.loc[df['macd_line'] < df['signal_line'], 'score'] -= 1
    df.loc[df['rsi_14'] < 50, 'score'] -= 1
    df.loc[df['close'] < df['sma_20'], 'score'] -= 1
    

    df['signal'] = 0
    sell_condition = (df['score'] == -3)


    if 'SMA_200' in df.columns:
        df.dropna(subset=['SMA_200'], inplace=True)
        df.rename(columns={'SMA_200': 'sma_200'}, inplace=True)
        buy_condition = (df['score'] == 3) & (df['close'] > df['sma_200'])
    else:
       
        df.dropna(inplace=True) 
        buy_condition = (df['score'] == 3)

    df.loc[buy_condition, 'signal'] = 1
    df.loc[sell_condition, 'signal'] = -1
    
    
    return df[['dt', 'signal', 'close', 'rsi_14','score']]