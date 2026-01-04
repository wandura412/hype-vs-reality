import ccxt
import pandas as pd
import os

def fetch_crypto_data(symbol='BTC/USDT', timeframe='1h', limit=1000):
    """
    Fetches free public OHLCV data from Binance.
    """
    print(f"Connecting to Binance for {symbol}...")
    
    # We use Binance because they have the most volume (the "Real" price)
    exchange = ccxt.binance()
    
    # Fetch the data (Timestamp, Open, High, Low, Close, Volume)
    # This does NOT require an API key for public data
    bars = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    
    # Organize into a nice table
    df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    
    # Define the output path
    # We use os.path.join to make it work on both Windows and Mac cleanly
    output_dir = os.path.join('data', 'price_history')
    output_path = os.path.join(output_dir, f"{symbol.replace('/', '_')}_price.csv")
    
    # Ensure directory exists before saving (just in case)
    os.makedirs(output_dir, exist_ok=True)
    
    df.to_csv(output_path, index=False)
    print(f"Saved {len(df)} rows to {output_path}")
    return df

if __name__ == "__main__":
    fetch_crypto_data()