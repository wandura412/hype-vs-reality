import time
from universe_selector import get_top_tickers
from data_loader import fetch_crypto_data

def update_market_data():
    """
    Orchestrates the download of the entire crypto universe.
    """
    print("Initializing Market Data Update...")
    
    # 1. Get the list of assets
    tickers = get_top_tickers()
    
    success_count = 0
    fail_count = 0
    
    # 2. Loop through each ticker and download data
    print(f"Starting download for {len(tickers)} assets...")
    print("-" * 40)
    
    for symbol in tickers:
        # We add a small delay to be polite to Yahoo's servers
        time.sleep(1) 
        
        result = fetch_crypto_data(symbol)
        
        if result is not None:
            success_count += 1
        else:
            fail_count += 1
            
    print("-" * 40)
    print(f"Update Complete.")
    print(f"Successful: {success_count}")
    print(f"Failed: {fail_count}")

if __name__ == "__main__":
    update_market_data()