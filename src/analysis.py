import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

def analyze_market():
    print("Loading data...")
    
    price_path = os.path.join('data', 'price_history', 'BTC_USDT_price.csv')
    sent_path = os.path.join('data', 'raw_tweets', 'news_sentiment.csv')
    
    if not os.path.exists(price_path) or not os.path.exists(sent_path):
        print("Data missing! Run data_loader.py and sentiment.py first.")
        return

    price_df = pd.read_csv(price_path)
    sent_df = pd.read_csv(sent_path)

    # Clean Dates
    price_df['timestamp'] = pd.to_datetime(price_df['timestamp'])
    sent_df['date'] = pd.to_datetime(sent_df['date'])
    
    # ---------------------------------------------------------
    # 🧙‍♂️ MOCK DATA GENERATOR (Delete this once you have 1 week of data)
    unique_days = sent_df['date'].dt.date.nunique()
    if unique_days < 5:
        print(f"Only {unique_days} day(s) of data found.")
        print("Generating MOCK historical sentiment for the backtest...")
        dates = price_df['timestamp'].dt.date.unique()
        # Random sentiment between -0.5 and 0.5
        mock_data = {
            'date': pd.to_datetime(dates),
            'sentiment_score': np.random.uniform(-0.5, 0.5, size=len(dates)),
            'headline': 'Mock Data'
        }
        sent_df = pd.DataFrame(mock_data)
    # ---------------------------------------------------------

    # Group by Day
    price_df['day'] = price_df['timestamp'].dt.date
    sent_df['day'] = sent_df['date'].dt.date
    
    daily_price = price_df.groupby('day')['close'].mean().reset_index()
    daily_sent = sent_df.groupby('day')['sentiment_score'].mean().reset_index()

    # Merge Price and Sentiment
    merged = pd.merge(daily_price, daily_sent, on='day', how='inner')
    
    # =========================================================
    # LEVEL 1: THE BACKTEST ENGINE
    # =========================================================
    
    # 1. Calculate Daily Market Returns (Percentage Change)
    merged['market_returns'] = merged['close'].pct_change()
    
    # 2. Define the Signal (The Strategy)
    # If sentiment is positive (> 0), we hold Bitcoin (1). 
    # If sentiment is negative/neutral (<= 0), we go to Cash (0).
    merged['signal'] = np.where(merged['sentiment_score'] > 0, 1, 0)
    
    # 3. Apply the Lag (Crucial Step!)
    # We shift the signal down by 1 day. 
    # Today's returns are based on YESTERDAY's decision.
    merged['strategy_returns'] = merged['market_returns'] * merged['signal'].shift(1)
    
    # 4. Calculate Cumulative Returns (Growth of $1)
    merged['cumulative_market'] = (1 + merged['market_returns']).cumprod()
    merged['cumulative_strategy'] = (1 + merged['strategy_returns']).cumprod()
    
    print("Backtest Complete!")

    # =========================================================
    # VISUALIZATION
    # =========================================================
    plt.style.use('ggplot') # Makes the chart look professional
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

    # Top Chart: The Equity Curve (Money Made)
    ax1.set_title('Strategy Backtest: "Hype" Strategy vs. Buy & Hold')
    ax1.plot(merged['day'], merged['cumulative_market'], label='Buy & Hold BTC', color='gray', alpha=0.6)
    ax1.plot(merged['day'], merged['cumulative_strategy'], label='Sentiment Strategy', color='blue', linewidth=2)
    ax1.set_ylabel('Growth of $1 Investment')
    ax1.legend(loc='upper left')
    ax1.grid(True)

    # Bottom Chart: The Sentiment Signals
    ax2.set_title('Daily Sentiment Score')
    # Color bars green if positive, red if negative
    colors = ['green' if x > 0 else 'red' for x in merged['sentiment_score']]
    ax2.bar(merged['day'], merged['sentiment_score'], color=colors, alpha=0.6)
    ax2.axhline(0, color='black', linewidth=1)
    ax2.set_ylabel('Sentiment Score')
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    analyze_market()