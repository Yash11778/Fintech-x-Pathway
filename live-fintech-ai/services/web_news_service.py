"""
Web Scraping News Service for Live Fintech AI Assistant
Now uses the robust news scraper with multiple reliable sources
"""

try:
    from .robust_news_scraper import RobustNewsScraper, NewsArticle
except ImportError:
    from robust_news_scraper import RobustNewsScraper, NewsArticle

from config import Config
from typing import Dict, List, Optional
from datetime import datetime, timedelta

class WebScrapingNewsService:
    """Web scraping implementation of news service using robust scraper"""
    
    def __init__(self):
        print("🔧 Initializing Web Scraping News Service with robust scraper...")
        self.scraper = RobustNewsScraper()
        self.symbols = Config.STOCK_SYMBOLS
        self.news_cache: Dict[str, List[NewsArticle]] = {symbol: [] for symbol in self.symbols}
    
    def fetch_news_for_symbol(self, symbol: str, limit: int = 10) -> List[NewsArticle]:
        """Fetch news articles for a specific stock symbol"""
        print(f"📰 Fetching news for {symbol}...")
        return self.scraper.get_news_for_symbol(symbol, limit)
    
    def fetch_trending_news(self, limit: int = 20) -> List[NewsArticle]:
        """Fetch trending financial news across all sources"""
        print("📰 Fetching trending financial news...")
        return self.scraper.get_trending_news(limit)
    
    def fetch_all_news(self) -> List[NewsArticle]:
        """Fetch financial news from all sources"""
        print("📰 Fetching all financial news...")
        return self.scraper.fetch_financial_news()
    
    def refresh_news_for_symbol(self, symbol: str) -> List[NewsArticle]:
        """Refresh news cache for a specific symbol"""
        print(f"🔄 Refreshing news for {symbol}")
        
        try:
            articles = self.fetch_news_for_symbol(symbol)
            
            # Update cache
            self.news_cache[symbol] = articles
            
            print(f"✅ Cached {len(articles)} articles for {symbol}")
            return articles
            
        except Exception as e:
            print(f"❌ Error refreshing news for {symbol}: {e}")
            return []
    
    def get_cached_news(self, symbol: str) -> List[NewsArticle]:
        """Get cached news articles for a symbol"""
        return self.news_cache.get(symbol, [])
    
    def get_recent_news(self, symbol: str, hours: int = 24) -> List[NewsArticle]:
        """Get recent news articles for a symbol within specified hours"""
        all_news = self.fetch_news_for_symbol(symbol)
        
        # Filter by time (assuming timestamp is available)
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_news = [
            article for article in all_news
            if article.timestamp >= cutoff_time
        ]
        
        return recent_news
    
    def initialize_news_cache(self):
        """Initialize news cache for all symbols"""
        print("📰 Initializing news cache for all symbols...")
        
        for symbol in self.symbols:
            try:
                self.refresh_news_for_symbol(symbol)
            except Exception as e:
                print(f"❌ Failed to initialize news for {symbol}: {e}")
                continue
        
        total_articles = sum(len(articles) for articles in self.news_cache.values())
        print(f"✅ News cache initialized with {total_articles} total articles")
    
    def run_once(self) -> Dict[str, List[NewsArticle]]:
        """Run a single iteration of news fetching"""
        try:
            print("📰 Running news service iteration...")
            
            # Fetch news for all symbols
            all_news = {}
            
            for symbol in self.symbols:
                try:
                    articles = self.fetch_news_for_symbol(symbol, limit=5)
                    all_news[symbol] = articles
                    
                    # Update cache
                    self.news_cache[symbol] = articles
                    
                except Exception as e:
                    print(f"❌ Error fetching news for {symbol}: {e}")
                    all_news[symbol] = []
            
            total_articles = sum(len(articles) for articles in all_news.values())
            print(f"✅ Fetched {total_articles} total articles across {len(self.symbols)} symbols")
            
            return all_news
            
        except Exception as e:
            print(f"❌ Error in news service: {e}")
            return {}
    
    def start_monitoring(self):
        """Start continuous monitoring (for compatibility)"""
        print("🚀 Starting news monitoring...")
        print("💡 Note: This service is designed for single-run operations.")
        print("💡 Use run_once() method for individual news fetches.")
        
        # Initialize cache
        self.initialize_news_cache()
        
        return self.news_cache

# Test function
def test_web_scraping_news_service():
    """Test the web scraping news service"""
    print("🧪 Testing Web Scraping News Service...")
    
    service = WebScrapingNewsService()
    
    # Test single symbol news fetch
    print("\n1. Testing news fetch for AAPL:")
    articles = service.fetch_news_for_symbol('AAPL', limit=3)
    
    if articles:
        print(f"✅ Found {len(articles)} articles for AAPL")
        for i, article in enumerate(articles[:2], 1):  # Show first 2
            print(f"   {i}. {article.title[:60]}...")
            print(f"      Source: {article.source}")
    else:
        print("❌ No articles found for AAPL")
    
    # Test trending news
    print("\n2. Testing trending news:")
    trending = service.fetch_trending_news(limit=5)
    
    if trending:
        print(f"✅ Found {len(trending)} trending articles")
        for article in trending[:2]:  # Show first 2
            print(f"   📰 {article.title[:60]}...")
            print(f"      Symbols: {', '.join(article.symbols)}")
    else:
        print("❌ No trending articles found")
    
    # Test full service run
    print("\n3. Testing full service run:")
    all_news = service.run_once()
    
    total_articles = sum(len(articles) for articles in all_news.values())
    print(f"✅ Service run completed with {total_articles} total articles")
    
    print("\n🎉 Test completed!")

if __name__ == "__main__":
    test_web_scraping_news_service()
