import yfinance as yf
import pandas as pd
import os

def fetch_crypto_data(symbol='BTC-USD', period='60d', interval='1h'):
    """
    Fetches OHLCV data from Yahoo Finance.
    
    params:
    symbol: Ticker (e.g., 'BTC-USD')
    period: How far back? (max 730d for hourly data)
    interval: Timeframe (1h, 1d, etc.)
    """
    print(f"Downloading data for {symbol} from Yahoo Finance...")
    
    try:
        # Fetch data
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval)
        
        if df.empty:
            print(f"Warning: No data found for {symbol}")
            return None
            
        # Clean up the data to match our standard format
        # Yahoo returns: Open, High, Low, Close, Volume, Dividends...
        df = df.reset_index()
        
        # Rename columns to lowercase standard
        df.rename(columns={
            'Date': 'timestamp', 
            'Datetime': 'timestamp',
            'Open': 'open',
            'High': 'high', 
            'Low': 'low', 
            'Close': 'close', 
            'Volume': 'volume'
        }, inplace=True)
        
        # Keep only the columns we need
        needed_cols = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        df = df[needed_cols]
        
        # Save to disk
        # We replace '-' with '_' for filenames (BTC-USD -> BTC_USD_price.csv)
        filename = f"{symbol.replace('-', '_')}_price.csv"
        output_dir = os.path.join('data', 'price_history')
        output_path = os.path.join(output_dir, filename)
        
        os.makedirs(output_dir, exist_ok=True)
        df.to_csv(output_path, index=False)
        
        print(f"Saved {len(df)} rows to {output_path}")
        return df

    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None

if __name__ == "__main__":
    # Test with one coin
    fetch_crypto_data('BTC-USD')