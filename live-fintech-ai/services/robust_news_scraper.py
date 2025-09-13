"""
Robust Web Scraping News Service for Live Fintech AI Assistant
Scrapes from multiple reliable sources: Reuters, Yahoo Finance, MarketWatch, CNN Business
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import re
from config import Config
import random

@dataclass
class NewsArticle:
    """Data structure for news articles"""
    title: str
    url: str
    summary: str
    timestamp: datetime
    source: str
    symbols: List[str]  # Stock symbols mentioned in the article
    sentiment: Optional[str] = None  # "positive", "negative", "neutral"

class RobustNewsScraper:
    """Robust news scraper with multiple reliable sources"""
    
    def __init__(self):
        self.symbols = Config.STOCK_SYMBOLS
        self.processed_urls = set()  # To avoid duplicate articles
        
        # Company name mappings
        self.company_mappings = {
            'AAPL': ['Apple', 'Apple Inc', 'AAPL', 'iPhone', 'iPad', 'Mac', 'Tim Cook'],
            'MSFT': ['Microsoft', 'Microsoft Corp', 'MSFT', 'Windows', 'Azure', 'Office', 'Satya Nadella'],
            'GOOGL': ['Google', 'Alphabet', 'GOOGL', 'YouTube', 'Android', 'Sundar Pichai', 'Search'],
            'AMZN': ['Amazon', 'Amazon.com', 'AMZN', 'AWS', 'Prime', 'Jeff Bezos', 'Andy Jassy'],
            'TSLA': ['Tesla', 'TSLA', 'Elon Musk', 'Model S', 'Model 3', 'Model Y', 'Cybertruck'],
            'META': ['Meta', 'Facebook', 'META', 'Instagram', 'WhatsApp', 'Mark Zuckerberg', 'Metaverse'],
            'NVDA': ['NVIDIA', 'NVDA', 'Jensen Huang', 'GPU', 'AI chips', 'gaming'],
            'NFLX': ['Netflix', 'NFLX', 'streaming', 'Reed Hastings'],
            'AMD': ['AMD', 'Advanced Micro Devices', 'Lisa Su', 'Ryzen', 'Radeon'],
            'INTC': ['Intel', 'INTC', 'Pat Gelsinger', 'processors', 'chips'],
            'UBER': ['Uber', 'UBER', 'rideshare', 'Dara Khosrowshahi'],
            'COIN': ['Coinbase', 'COIN', 'cryptocurrency', 'Bitcoin', 'crypto exchange'],
            'PLTR': ['Palantir', 'PLTR', 'data analytics', 'Alex Karp'],
            'SNOW': ['Snowflake', 'SNOW', 'cloud computing', 'data warehouse'],
            'ZM': ['Zoom', 'ZM', 'video conferencing', 'Eric Yuan']
        }
        
        # User agents for rotation
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0'
        ]
        
        self.session = requests.Session()
        self._rotate_user_agent()
    
    def _rotate_user_agent(self):
        """Rotate user agent to avoid detection"""
        headers = {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
        self.session.headers.update(headers)
    
    def _extract_symbols_from_text(self, text: str) -> List[str]:
        """Extract stock symbols mentioned in text"""
        found_symbols = []
        text_lower = text.lower()
        
        for symbol, keywords in self.company_mappings.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    if symbol not in found_symbols:
                        found_symbols.append(symbol)
                    break
        
        return found_symbols
    
    def scrape_reuters_business(self) -> List[NewsArticle]:
        """
        Scrape financial news from Reuters Business section
        """
        articles = []
        
        try:
            url = "https://www.reuters.com/business/"
            
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Reuters article selectors - multiple fallbacks
            article_selectors = [
                'article[data-testid="ArticleCard"]',
                '.story-collection__item',
                '[data-module="ArticleCard"]',
                'article',
                '.story-card',
                '[data-testid*="article"]',
                '.media-story-card'
            ]
            
            articles_found = []
            for selector in article_selectors:
                found = soup.select(selector)
                if found:
                    articles_found = found
                    break
            
            if not articles_found:
                # Fallback: look for any links that look like article URLs
                articles_found = soup.find_all('a', href=re.compile(r'/(business|markets|technology)/.*\d{4}'))[:20]
            
            for article in articles_found[:15]:  # Limit to 15 articles
                try:
                    # Extract title
                    title_element = article.find(['h3', 'h2', 'h4']) or article.find('a')
                    if not title_element:
                        continue
                    
                    title = title_element.get_text(strip=True)
                    if not title or len(title) < 10:
                        continue
                    
                    # Extract URL
                    link_element = article.find('a') or article
                    if not link_element or not link_element.get('href'):
                        continue
                    
                    article_url = link_element['href']
                    if article_url.startswith('/'):
                        article_url = 'https://www.reuters.com' + article_url
                    
                    if article_url in self.processed_urls:
                        continue
                    
                    # Extract summary/snippet
                    summary_element = article.find(['p', 'div'], class_=re.compile(r'summary|excerpt|snippet'))
                    summary = summary_element.get_text(strip=True) if summary_element else title
                    
                    # Check if article is relevant to our stocks
                    full_text = f"{title} {summary}".lower()
                    relevant_symbols = self._extract_symbols_from_text(full_text)
                    
                    if relevant_symbols:
                        news_article = NewsArticle(
                            title=title,
                            url=article_url,
                            summary=summary,
                            timestamp=datetime.now(),
                            source="Reuters",
                            symbols=relevant_symbols
                        )
                        
                        articles.append(news_article)
                        self.processed_urls.add(article_url)
                
                except Exception as e:
                    continue
            
            print(f"✅ Reuters: Found {len(articles)} relevant articles")
            return articles
            
        except Exception as e:
            print(f"❌ Reuters scraping error: {e}")
            return []
    
    def scrape_yahoo_finance_news(self) -> List[NewsArticle]:
        """
        Scrape financial news from Yahoo Finance
        """
        articles = []
        
        try:
            url = "https://finance.yahoo.com/news/"
            
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Yahoo Finance news selectors - multiple fallbacks
            selectors_to_try = [
                'div[data-test-locator="mega"] li',
                '.Ov\\(h\\) .Pend\\(44px\\)',
                'div[data-module="stream"] li',
                '.js-stream-content li',
                '[data-module="StreamStore"] li',
                'ul[data-module="stream"] li',
                'article',
                '.story-item'
            ]
            
            news_items = []
            for selector in selectors_to_try:
                items = soup.select(selector)
                if items:
                    news_items = items
                    break
            
            for item in news_items[:20]:  # Limit to 20 articles
                try:
                    # Extract title and URL
                    link_element = item.find('a')
                    if not link_element:
                        continue
                    
                    title = link_element.get_text(strip=True)
                    if not title or len(title) < 10:
                        continue
                    
                    article_url = link_element.get('href', '')
                    if article_url.startswith('/'):
                        article_url = 'https://finance.yahoo.com' + article_url
                    elif not article_url.startswith('http'):
                        continue
                    
                    if article_url in self.processed_urls:
                        continue
                    
                    # Extract summary
                    summary_element = item.find('p') or item.find('div', class_=re.compile(r'summary|excerpt'))
                    summary = summary_element.get_text(strip=True) if summary_element else title
                    
                    # Check relevance
                    full_text = f"{title} {summary}".lower()
                    relevant_symbols = self._extract_symbols_from_text(full_text)
                    
                    if relevant_symbols:
                        news_article = NewsArticle(
                            title=title,
                            url=article_url,
                            summary=summary,
                            timestamp=datetime.now(),
                            source="Yahoo Finance",
                            symbols=relevant_symbols
                        )
                        
                        articles.append(news_article)
                        self.processed_urls.add(article_url)
                
                except Exception as e:
                    continue
            
            print(f"✅ Yahoo Finance: Found {len(articles)} relevant articles")
            return articles
            
        except Exception as e:
            print(f"❌ Yahoo Finance news scraping error: {e}")
            return []
    
    def scrape_marketwatch_news(self) -> List[NewsArticle]:
        """
        Scrape financial news from MarketWatch
        """
        articles = []
        
        try:
            url = "https://www.marketwatch.com/latest-news"
            
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # MarketWatch news selectors
            news_items = (soup.select('.collection__element') or 
                         soup.select('.article__content') or
                         soup.select('div[data-module="ArticleCard"]'))
            
            for item in news_items[:15]:  # Limit to 15 articles
                try:
                    # Extract title and URL
                    link_element = item.find('a')
                    if not link_element:
                        continue
                    
                    title = link_element.get_text(strip=True)
                    if not title or len(title) < 10:
                        continue
                    
                    article_url = link_element.get('href', '')
                    if article_url.startswith('/'):
                        article_url = 'https://www.marketwatch.com' + article_url
                    elif not article_url.startswith('http'):
                        continue
                    
                    if article_url in self.processed_urls:
                        continue
                    
                    # Extract summary
                    summary_element = item.find('p') or item.find('div', class_=re.compile(r'summary|excerpt'))
                    summary = summary_element.get_text(strip=True) if summary_element else title
                    
                    # Check relevance
                    full_text = f"{title} {summary}".lower()
                    relevant_symbols = self._extract_symbols_from_text(full_text)
                    
                    if relevant_symbols:
                        news_article = NewsArticle(
                            title=title,
                            url=article_url,
                            summary=summary,
                            timestamp=datetime.now(),
                            source="MarketWatch",
                            symbols=relevant_symbols
                        )
                        
                        articles.append(news_article)
                        self.processed_urls.add(article_url)
                
                except Exception as e:
                    continue
            
            print(f"✅ MarketWatch: Found {len(articles)} relevant articles")
            return articles
            
        except Exception as e:
            print(f"❌ MarketWatch news scraping error: {e}")
            return []
    
    def scrape_cnn_business(self) -> List[NewsArticle]:
        """
        Scrape financial news from CNN Business
        """
        articles = []
        
        try:
            url = "https://www.cnn.com/business"
            
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # CNN Business news selectors
            news_items = (soup.select('[data-module-name="card-media-over-text"]') or
                         soup.select('.container__headline') or
                         soup.select('article'))
            
            for item in news_items[:15]:  # Limit to 15 articles
                try:
                    # Extract title and URL
                    link_element = item.find('a')
                    if not link_element:
                        continue
                    
                    title_element = link_element.find(['h3', 'span', 'h2']) or link_element
                    title = title_element.get_text(strip=True)
                    
                    if not title or len(title) < 10:
                        continue
                    
                    article_url = link_element.get('href', '')
                    if article_url.startswith('/'):
                        article_url = 'https://www.cnn.com' + article_url
                    elif not article_url.startswith('http'):
                        continue
                    
                    if article_url in self.processed_urls:
                        continue
                    
                    # Extract summary
                    summary_element = item.find('div', class_=re.compile(r'summary|excerpt|description'))
                    summary = summary_element.get_text(strip=True) if summary_element else title
                    
                    # Check relevance
                    full_text = f"{title} {summary}".lower()
                    relevant_symbols = self._extract_symbols_from_text(full_text)
                    
                    if relevant_symbols:
                        news_article = NewsArticle(
                            title=title,
                            url=article_url,
                            summary=summary,
                            timestamp=datetime.now(),
                            source="CNN Business",
                            symbols=relevant_symbols
                        )
                        
                        articles.append(news_article)
                        self.processed_urls.add(article_url)
                
                except Exception as e:
                    continue
            
            print(f"✅ CNN Business: Found {len(articles)} relevant articles")
            return articles
            
        except Exception as e:
            print(f"❌ CNN Business scraping error: {e}")
            return []
    
    def scrape_bloomberg_news(self) -> List[NewsArticle]:
        """
        Scrape financial news from Bloomberg
        Note: Bloomberg has strict anti-scraping measures, so this is a basic attempt
        """
        articles = []
        
        try:
            url = "https://www.bloomberg.com/markets"
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Bloomberg often blocks scrapers, so we'll try basic extraction
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for article links
            links = soup.find_all('a', href=re.compile(r'/news/articles/'))
            
            for link in links[:10]:  # Limit attempts
                try:
                    title = link.get_text(strip=True)
                    if not title or len(title) < 10:
                        continue
                    
                    article_url = link.get('href', '')
                    if article_url.startswith('/'):
                        article_url = 'https://www.bloomberg.com' + article_url
                    
                    if article_url in self.processed_urls:
                        continue
                    
                    # Check relevance
                    relevant_symbols = self._extract_symbols_from_text(title)
                    
                    if relevant_symbols:
                        news_article = NewsArticle(
                            title=title,
                            url=article_url,
                            summary=title,  # Use title as summary for Bloomberg
                            timestamp=datetime.now(),
                            source="Bloomberg",
                            symbols=relevant_symbols
                        )
                        
                        articles.append(news_article)
                        self.processed_urls.add(article_url)
                
                except Exception as e:
                    continue
            
            print(f"✅ Bloomberg: Found {len(articles)} relevant articles")
            return articles
            
        except Exception as e:
            print(f"❌ Bloomberg scraping error: {e}")
            return []
    
    def fetch_financial_news(self) -> List[NewsArticle]:
        """
        Fetch financial news from all sources
        """
        all_articles = []
        
        print("📰 Fetching financial news from multiple sources...")
        
        # Rotate user agent
        self._rotate_user_agent()
        
        # Try all sources
        sources = [
            ("Reuters Business", self.scrape_reuters_business),
            ("Yahoo Finance", self.scrape_yahoo_finance_news),
            ("MarketWatch", self.scrape_marketwatch_news),
            ("CNN Business", self.scrape_cnn_business),
            ("Bloomberg", self.scrape_bloomberg_news)
        ]
        
        for source_name, scrape_func in sources:
            try:
                print(f"\n🔍 Scraping {source_name}...")
                articles = scrape_func()
                all_articles.extend(articles)
                
                # Small delay between sources
                time.sleep(2)
                
            except Exception as e:
                print(f"❌ {source_name} failed: {e}")
                continue
        
        # Remove duplicates based on title similarity
        unique_articles = self._remove_duplicate_articles(all_articles)
        
        # Sort by timestamp (newest first)
        unique_articles.sort(key=lambda x: x.timestamp, reverse=True)
        
        print(f"\n✅ Total unique articles found: {len(unique_articles)}")
        
        # Print summary by source
        source_counts = {}
        for article in unique_articles:
            source_counts[article.source] = source_counts.get(article.source, 0) + 1
        
        for source, count in source_counts.items():
            print(f"  📊 {source}: {count} articles")
        
        return unique_articles
    
    def _remove_duplicate_articles(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        """Remove duplicate articles based on title similarity"""
        unique_articles = []
        seen_titles = set()
        
        for article in articles:
            # Create a normalized title for comparison
            normalized_title = re.sub(r'[^\w\s]', '', article.title.lower()).strip()
            words = normalized_title.split()
            
            # Create a key from first few words
            title_key = ' '.join(words[:5]) if len(words) >= 5 else normalized_title
            
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_articles.append(article)
        
        return unique_articles
    
    def get_news_for_symbol(self, symbol: str, limit: int = 10) -> List[NewsArticle]:
        """Get recent news articles for a specific symbol"""
        all_news = self.fetch_financial_news()
        
        symbol_news = [
            article for article in all_news
            if symbol in article.symbols
        ]
        
        return symbol_news[:limit]
    
    def get_trending_news(self, limit: int = 20) -> List[NewsArticle]:
        """Get trending financial news across all sources"""
        return self.fetch_financial_news()[:limit]

# Alias for backwards compatibility
WebScrapingNewsService = RobustNewsScraper

# Test function
def test_robust_news_scraper():
    """Test the robust news scraper functionality"""
    print("🧪 Testing Robust News Scraper...")
    
    scraper = RobustNewsScraper()
    
    # Test fetching news
    articles = scraper.fetch_financial_news()
    
    print(f"\n📊 Found {len(articles)} articles:")
    
    for i, article in enumerate(articles[:5], 1):  # Show first 5
        print(f"\n{i}. {article.title}")
        print(f"   Source: {article.source}")
        print(f"   Symbols: {', '.join(article.symbols)}")
        print(f"   URL: {article.url}")
        if article.summary != article.title:
            print(f"   Summary: {article.summary[:100]}...")
    
    # Test symbol-specific news
    if articles:
        test_symbol = articles[0].symbols[0] if articles[0].symbols else 'AAPL'
        symbol_news = scraper.get_news_for_symbol(test_symbol)
        print(f"\n📰 Found {len(symbol_news)} articles for {test_symbol}")
    
    print("\n🎉 Test completed!")

if __name__ == "__main__":
    test_robust_news_scraper()
