import requests
from bs4 import BeautifulSoup
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import datetime
import os

def get_crypto_news():
    """
    Scrapes headlines from CoinTelegraph and scores them with VADER.
    """
    url = "https://cointelegraph.com/tags/bitcoin"
    print(f"Scraping news from {url}...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # Initialize VADER (The Social Media Sentiment Analyzer)
    analyzer = SentimentIntensityAnalyzer()
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Note: Class names on websites change! 
        headlines = soup.find_all(class_='post-card-inline__title')
        
        news_data = []
        for item in headlines:
            text = item.get_text(strip=True)
            
            # --- THE UPGRADE ---
            # VADER gives us 4 scores: neg, neu, pos, compound.
            # We only care about 'compound' (the overall score from -1 to 1)
            vs = analyzer.polarity_scores(text)
            score = vs['compound']
            
            print(f" '{text[:30]}...' -> Score: {score}") # Print score to see it working
            
            news_data.append({
                'date': datetime.datetime.now().strftime("%Y-%m-%d"),
                'headline': text,
                'sentiment_score': score
            })
            
        df = pd.DataFrame(news_data)
        
        output_dir = os.path.join('data', 'raw_tweets')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "news_sentiment.csv")
        
        # Append to existing file so we build history
        write_header = not os.path.exists(output_path)
        df.to_csv(output_path, index=False, mode='a', header=write_header)
        
        print(f"Extracted {len(df)} headlines.")
        print(f"New Average Sentiment: {df['sentiment_score'].mean():.4f}")
        return df
        
    except Exception as e:
        print(f"Error scraping: {e}")

if __name__ == "__main__":
    get_crypto_news()