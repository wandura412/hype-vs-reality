import yfinance as yf

def get_top_tickers():
    """
    Returns a manual list of top crypto assets formatted for Yahoo Finance.
    Yahoo uses the format 'BTC-USD', 'ETH-USD', etc.
    """
    # Top 20 liquid assets (Standard Universe)
    # We use the Yahoo Finance ticker format (COIN-USD)
    universe = [
        'BTC-USD', 'ETH-USD', 'BNB-USD', 'SOL-USD', 'XRP-USD',
        'ADA-USD', 'DOGE-USD', 'AVAX-USD', 'TRX-USD', 'DOT-USD',
        'LINK-USD', 'MATIC-USD', 'LTC-USD', 'BCH-USD', 'UNI7083-USD',
        'ATOM-USD', 'XLM-USD', 'ETC-USD', 'FIL-USD', 'HBAR-USD'
    ]
    
    print(f"Selected manual universe of {len(universe)} assets.")
    return universe

if __name__ == "__main__":
    assets = get_top_tickers()
    print(assets)