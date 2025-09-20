import pandas as pd
import yfinance as yf
import pyarrow.parquet as pq
import pyarrow as pa
from datetime import datetime
import os


"""We decided to use,Fetches stock data and stores it in a Parquet file."""
def fetch_and_store_prices(symbol: str, start: str, end: str) -> pd.DataFrame:
   
    try:
        data_dir = 'data'
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)


        file_path = os.path.join(data_dir, f"{symbol}.parquet")
        
        data = yf.download(symbol, start=start, end=end)
        if data.empty:
            print(f"No data found for {symbol}")
            return pd.DataFrame()

        data.reset_index(inplace=True)
        data.rename(columns={'Date': 'dt', 'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Adj Close': 'adj_close', 'Volume': 'volume'}, inplace=True)
        
        table = pa.Table.from_pandas(data)
        pq.write_table(table, file_path)
        print(f"Data for {symbol} saved to {file_path}")
        return data
    except Exception as e:
        print(f"Error fetching/storing data for {symbol}: {e}")
        return pd.DataFrame()