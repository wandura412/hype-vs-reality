import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from ranker import get_market_rankings
import sys
import io

# We need to capture the output of your ranker script to get the dataframe.
# In a production environment, we would refactor ranker.py to return the df directly.
# For now, we will copy the logic slightly to generate the dataframe for plotting.

import os
import numpy as np

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def generate_dashboard_data():
    data_dir = os.path.join('data', 'price_history')
    ranking_list = []

    for filename in os.listdir(data_dir):
        if filename.endswith(".csv"):
            symbol = filename.replace('_price.csv', '').replace('_', '-')
            filepath = os.path.join(data_dir, filename)
            
            try:
                df = pd.read_csv(filepath)
                if len(df) < 50:
                    continue
                
                # Metrics
                df['returns'] = df['close'].pct_change()
                volatility = df['returns'].std() * np.sqrt(24) * 100
                df['rsi'] = calculate_rsi(df['close'])
                current_rsi = df['rsi'].iloc[-1]
                
                avg_volume = df['volume'].rolling(window=24).mean().iloc[-1]
                current_volume = df['volume'].iloc[-1]
                vol_strength = current_volume / avg_volume if avg_volume > 0 else 0
                
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
                pass

    return pd.DataFrame(ranking_list)

def plot_heatmap():
    print("Generating Market Heatmap...")
    df = generate_dashboard_data()
    
    if df.empty:
        print("No data found to plot.")
        return

    # Set up the ranking metrics
    # We normalize these metrics so they can be compared on the same scale (0 to 1)
    # This is critical for a heatmap.
    
    # 1. Normalize Volatility (Lower is better for safety, Higher for trading)
    df['Norm_Volatility'] = (df['Volatility'] - df['Volatility'].min()) / (df['Volatility'].max() - df['Volatility'].min())
    
    # 2. Normalize RSI
    df['Norm_RSI'] = (df['RSI'] - df['RSI'].min()) / (df['RSI'].max() - df['RSI'].min())
    
    # 3. Normalize Volume
    df['Norm_Volume'] = (df['Volume_Strength'] - df['Volume_Strength'].min()) / (df['Volume_Strength'].max() - df['Volume_Strength'].min())

    # Create the matrix for the heatmap
    # Rows = Coins, Columns = Metrics
    heatmap_data = df.set_index('Symbol')[['Change_24h', 'RSI', 'Volatility', 'Volume_Strength']]
    
    # Sort by 24h Change so the winners are at the top
    heatmap_data = heatmap_data.sort_values(by='Change_24h', ascending=False)

    # Plotting
    plt.figure(figsize=(12, 10))
    sns.set_theme(style="darkgrid")
    
    # We use a divergent color map: Red (Negative) to Blue/Green (Positive)
    # Center=0 makes sure 0% change is neutral color
    sns.heatmap(heatmap_data, annot=True, cmap="RdYlGn", center=50, linewidths=.5)
    
    plt.title('Crypto Market Scanner: The Heatmap', fontsize=16)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    plot_heatmap()