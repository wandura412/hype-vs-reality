import pandas as pd
import numpy as np
import os

def calculate_rsi(series, period=14):
    """
    Calculates the Relative Strength Index (RSI) technical indicator.
    """
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

    rs = gain / loss
    return 100 - (100 / (1 + rs))

def get_market_rankings():
    print("Analyzing market data for ranking...")
    
    data_dir = os.path.join('data', 'price_history')
    ranking_list = []

    # Loop through every file in the directory
    for filename in os.listdir(data_dir):
        if filename.endswith(".csv"):
            symbol = filename.replace('_price.csv', '').replace('_', '-')
            filepath = os.path.join(data_dir, filename)
            
            # Load Data
            try:
                df = pd.read_csv(filepath)
                if len(df) < 50:
                    continue # Skip coins with not enough data
                
                # --- THE MATH SECTION ---
                
                # 1. Calculate Volatility (Standard Deviation of returns)
                # We multiply by sqrt(24) to normalize hourly data to daily volatility approximate
                df['returns'] = df['close'].pct_change()
                volatility = df['returns'].std() * np.sqrt(24) * 100
                
                # 2. Calculate RSI (Momentum)
                df['rsi'] = calculate_rsi(df['close'])
                current_rsi = df['rsi'].iloc[-1]
                
                # 3. Calculate Volume Spike (Current Vol vs Moving Average Vol)
                avg_volume = df['volume'].rolling(window=24).mean().iloc[-1]
                current_volume = df['volume'].iloc[-1]
                vol_strength = current_volume / avg_volume if avg_volume > 0 else 0
                
                # 4. Price Change (24h)
                price_change_24h = (df['close'].iloc[-1] - df['close'].iloc[-24]) / df['close'].iloc[-24] * 100
                
                ranking_list.append({
                    'Symbol': symbol,
                    'Price': df['close'].iloc[-1],
                    'Change_24h': price_change_24h,
                    'Volatility': volatility,
                    'RSI': current_rsi,
                    'Volume_Strength': vol_strength
                })
                
            except Exception as e:
                print(f"Error analyzing {symbol}: {e}")

    # Convert list to DataFrame for sorting
    rank_df = pd.DataFrame(ranking_list)
    
    # --- SCORING ALGORITHMS ---
    
    # Algorithm A: The "Safe Hold" Score
    # Low Volatility + Moderate RSI + Positive Trend
    rank_df['Safety_Score'] = (
        (rank_df['Change_24h'] * 0.4) - 
        (rank_df['Volatility'] * 0.4) - 
        (abs(rank_df['RSI'] - 50) * 0.2) # Penalty for being too extreme
    )

    # Algorithm B: The "Day Trade" Score (Degen Score)
    # High Volatility + High Volume + Extreme RSI
    rank_df['Trade_Score'] = (
        (rank_df['Volatility'] * 0.5) +
        (rank_df['Volume_Strength'] * 3) + # Weight volume heavily
        (abs(rank_df['RSI'] - 50) * 0.1)
    )

    print("\n" + "="*50)
    print("TOP 5 ASSETS FOR HOLDING (Low Risk, Steady Growth)")
    print("="*50)
    print(rank_df.sort_values(by='Safety_Score', ascending=False).head(5)[['Symbol', 'Safety_Score', 'Volatility', 'Change_24h']])

    print("\n" + "="*50)
    print("TOP 5 ASSETS FOR DAY TRADING (High Volatility, Volume Spikes)")
    print("="*50)
    print(rank_df.sort_values(by='Trade_Score', ascending=False).head(5)[['Symbol', 'Trade_Score', 'Volatility', 'Volume_Strength']])

if __name__ == "__main__":
    get_market_rankings()