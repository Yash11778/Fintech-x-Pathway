"""
Configuration management for Live Fintech AI Assistant
Handles API keys, constants, and environment variables
"""

import os
from dotenv import load_dotenv
from typing import List

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for the Live Fintech AI Assistant"""
    
    # Data source mode: 'api' or 'webscraping'
    DATA_SOURCE_MODE = os.getenv('DATA_SOURCE_MODE', 'webscraping')
    
    # API Keys (only needed if using API mode)
    ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
    NEWSAPI_KEY = os.getenv('NEWSAPI_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    
    # Stock symbols to track (expanded list)
    STOCK_SYMBOLS: List[str] = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 
        'META', 'NVDA', 'NFLX', 'AMD', 'INTC',
        'UBER', 'COIN', 'PLTR', 'SNOW', 'ZM'
    ]
    
    # Price movement detection settings
    PRICE_MOVEMENT_THRESHOLD_PERCENT = 2.0  # 2% price change threshold
    NEWS_MATCHING_WINDOW_MINUTES = 5  # Match news within 5 minutes
    
    # API endpoints
    ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"
    NEWSAPI_BASE_URL = "https://newsapi.org/v2"
    
    # Database settings
    DB_NAME = "fintech_ai"
    COLLECTION_PRICE_MOVEMENTS = "price_movements"
    COLLECTION_NEWS = "news"
    COLLECTION_EXPLANATIONS = "explanations"
    
    # Streamlit settings
    STREAMLIT_PORT = 8501
    REFRESH_INTERVAL_SECONDS = 30
    
    # OpenAI settings
    OPENAI_MODEL = "gpt-3.5-turbo"
    MAX_TOKENS = 200
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate configuration based on data source mode"""
        if cls.DATA_SOURCE_MODE == 'webscraping':
            # Only OpenAI API key is required for web scraping mode
            if not cls.OPENAI_API_KEY:
                print("❌ Missing required API key: OPENAI_API_KEY")
                print("For web scraping mode, only OpenAI API key is required.")
                print("Please set OPENAI_API_KEY in your .env file.")
                return False
            
            print("✅ Configuration valid for web scraping mode")
            print("   - Stock prices: Yahoo Finance (web scraping)")
            print("   - News: Multiple sources (web scraping)")
            print("   - AI explanations: OpenAI API")
            return True
        
        elif cls.DATA_SOURCE_MODE == 'api':
            # All API keys are required for API mode
            missing_keys = []
            if not cls.ALPHA_VANTAGE_API_KEY:
                missing_keys.append('ALPHA_VANTAGE_API_KEY')
            if not cls.NEWSAPI_KEY:
                missing_keys.append('NEWSAPI_KEY')
            if not cls.OPENAI_API_KEY:
                missing_keys.append('OPENAI_API_KEY')
                
            if missing_keys:
                print(f"❌ Missing required API keys: {', '.join(missing_keys)}")
                print("Please check your .env file and ensure all keys are set.")
                print("Or set DATA_SOURCE_MODE=webscraping to use web scraping instead.")
                return False
                
            print("✅ Configuration valid for API mode")
            print("   - Stock prices: AlphaVantage API")
            print("   - News: NewsAPI")
            print("   - AI explanations: OpenAI API")
            return True
        
        else:
            print(f"❌ Invalid DATA_SOURCE_MODE: {cls.DATA_SOURCE_MODE}")
            print("Must be either 'api' or 'webscraping'")
            return False
