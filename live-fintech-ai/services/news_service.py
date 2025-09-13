"""
News Service for Live Fintech AI Assistant
Handles real-time financial news fetching using NewsAPI
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from config import Config

@dataclass
class NewsArticle:
    """Data structure for news articles"""
    title: str
    description: str
    url: str
    published_at: datetime
    source: str
    symbol: Optional[str] = None  # Associated stock symbol

class NewsService:
    """Service for fetching real-time financial news"""
    
    def __init__(self):
        self.api_key = Config.NEWSAPI_KEY
        self.base_url = Config.NEWSAPI_BASE_URL
        self.symbols = Config.STOCK_SYMBOLS
        self.news_cache: Dict[str, List[NewsArticle]] = {symbol: [] for symbol in self.symbols}
        
    def fetch_news_for_symbol(self, symbol: str, hours_back: int = 1) -> List[NewsArticle]:
        """
        Fetch recent news articles for a specific stock symbol
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            hours_back: How many hours back to search for news
            
        Returns:
            List of NewsArticle objects
        """
        try:
            # Calculate time range
            to_date = datetime.now()
            from_date = to_date - timedelta(hours=hours_back)
            
            # Company name mapping for better search results
            company_names = {
                'AAPL': 'Apple',
                'TSLA': 'Tesla',
                'MSFT': 'Microsoft'
            }
            
            company_name = company_names.get(symbol, symbol)
            
            # Search query - include both symbol and company name
            query = f'"{symbol}" OR "{company_name}"'
            
            params = {
                'q': query,
                'language': 'en',
                'sortBy': 'publishedAt',
                'from': from_date.isoformat(),
                'to': to_date.isoformat(),
                'domains': 'reuters.com,bloomberg.com,marketwatch.com,cnbc.com,yahoo.com,wsj.com,ft.com',
                'apiKey': self.api_key
            }
            
            response = requests.get(f"{self.base_url}/everything", params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') != 'ok':
                print(f"❌ NewsAPI error for {symbol}: {data.get('message', 'Unknown error')}")
                return []
            
            articles = []
            for article_data in data.get('articles', []):
                if not article_data.get('title') or article_data.get('title') == '[Removed]':
                    continue
                    
                # Parse published date
                try:
                    published_at = datetime.fromisoformat(
                        article_data['publishedAt'].replace('Z', '+00:00')
                    )
                except (ValueError, TypeError):
                    published_at = datetime.now()
                
                article = NewsArticle(
                    title=article_data['title'],
                    description=article_data.get('description', ''),
                    url=article_data['url'],
                    published_at=published_at,
                    source=article_data.get('source', {}).get('name', 'Unknown'),
                    symbol=symbol
                )
                
                articles.append(article)
            
            # Cache the articles
            self.news_cache[symbol] = articles
            
            print(f"✅ Fetched {len(articles)} news articles for {symbol}")
            return articles
            
        except requests.RequestException as e:
            print(f"❌ Network error fetching news for {symbol}: {e}")
            return []
        except (KeyError, ValueError, TypeError) as e:
            print(f"❌ Data parsing error for {symbol} news: {e}")
            return []
    
    def fetch_all_news(self, hours_back: int = 1) -> Dict[str, List[NewsArticle]]:
        """
        Fetch news for all configured symbols
        
        Args:
            hours_back: How many hours back to search for news
            
        Returns:
            Dictionary mapping symbol to list of NewsArticle objects
        """
        all_news = {}
        
        for symbol in self.symbols:
            news = self.fetch_news_for_symbol(symbol, hours_back)
            all_news[symbol] = news
            
            # Add delay to respect API rate limits
            import time
            time.sleep(0.5)
        
        return all_news
    
    def find_relevant_news(self, symbol: str, timestamp: datetime, window_minutes: int = 5) -> List[NewsArticle]:
        """
        Find news articles relevant to a stock movement within a time window
        
        Args:
            symbol: Stock symbol
            timestamp: Timestamp of the price movement
            window_minutes: Time window in minutes to search for relevant news
            
        Returns:
            List of relevant NewsArticle objects
        """
        if symbol not in self.news_cache:
            return []
        
        # Define time window
        start_time = timestamp - timedelta(minutes=window_minutes)
        end_time = timestamp + timedelta(minutes=window_minutes)
        
        relevant_articles = []
        for article in self.news_cache[symbol]:
            if start_time <= article.published_at <= end_time:
                relevant_articles.append(article)
        
        # Sort by published date (most recent first)
        relevant_articles.sort(key=lambda x: x.published_at, reverse=True)
        
        return relevant_articles
    
    def get_latest_news(self, symbol: str, limit: int = 5) -> List[NewsArticle]:
        """
        Get the latest news articles for a symbol
        
        Args:
            symbol: Stock symbol
            limit: Maximum number of articles to return
            
        Returns:
            List of latest NewsArticle objects
        """
        if symbol not in self.news_cache:
            return []
        
        # Sort by published date and return latest
        sorted_articles = sorted(
            self.news_cache[symbol],
            key=lambda x: x.published_at,
            reverse=True
        )
        
        return sorted_articles[:limit]
    
    def search_breaking_news(self, hours_back: int = 2) -> List[NewsArticle]:
        """
        Search for breaking financial news across all symbols
        
        Args:
            hours_back: How many hours back to search
            
        Returns:
            List of breaking news articles
        """
        try:
            # Calculate time range
            to_date = datetime.now()
            from_date = to_date - timedelta(hours=hours_back)
            
            # Search for breaking financial news
            query = 'stock market OR earnings OR financial OR trading OR shares'
            
            params = {
                'q': query,
                'language': 'en',
                'sortBy': 'publishedAt',
                'from': from_date.isoformat(),
                'to': to_date.isoformat(),
                'category': 'business',
                'apiKey': self.api_key
            }
            
            response = requests.get(f"{self.base_url}/top-headlines", params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') != 'ok':
                print(f"❌ NewsAPI error for breaking news: {data.get('message', 'Unknown error')}")
                return []
            
            articles = []
            for article_data in data.get('articles', []):
                if not article_data.get('title') or article_data.get('title') == '[Removed]':
                    continue
                
                # Parse published date
                try:
                    published_at = datetime.fromisoformat(
                        article_data['publishedAt'].replace('Z', '+00:00')
                    )
                except (ValueError, TypeError):
                    published_at = datetime.now()
                
                article = NewsArticle(
                    title=article_data['title'],
                    description=article_data.get('description', ''),
                    url=article_data['url'],
                    published_at=published_at,
                    source=article_data.get('source', {}).get('name', 'Unknown')
                )
                
                articles.append(article)
            
            print(f"✅ Fetched {len(articles)} breaking news articles")
            return articles
            
        except requests.RequestException as e:
            print(f"❌ Network error fetching breaking news: {e}")
            return []
        except (KeyError, ValueError, TypeError) as e:
            print(f"❌ Data parsing error for breaking news: {e}")
            return []
    
    def get_cached_news(self, symbol: str) -> List[NewsArticle]:
        """
        Get cached news articles for a symbol
        
        Args:
            symbol: Stock symbol
            
        Returns:
            List of cached NewsArticle objects
        """
        return self.news_cache.get(symbol, [])

# Test function
def test_news_service():
    """Test the news service functionality"""
    print("🧪 Testing News Service...")
    
    service = NewsService()
    
    # Test fetching news for a single symbol
    print("\n📰 Testing single symbol news fetch:")
    news = service.fetch_news_for_symbol("AAPL", hours_back=2)
    if news:
        print(f"✅ Successfully fetched {len(news)} articles for AAPL")
        print(f"   Latest: {news[0].title[:50]}..." if news else "   No articles found")
    
    # Test fetching all news
    print("\n📰 Testing multiple symbol news fetch:")
    all_news = service.fetch_all_news(hours_back=1)
    total_articles = sum(len(articles) for articles in all_news.values())
    print(f"✅ Fetched {total_articles} total articles across all symbols")
    
    # Test breaking news
    print("\n🚨 Testing breaking news fetch:")
    breaking_news = service.search_breaking_news(hours_back=2)
    print(f"✅ Found {len(breaking_news)} breaking news articles")

if __name__ == "__main__":
    test_news_service()
