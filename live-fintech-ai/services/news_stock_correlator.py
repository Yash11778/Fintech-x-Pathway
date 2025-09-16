"""
NEWS-DRIVEN STOCK ANALYSIS SYSTEM
Real focus: Explain WHY stock prices move using relevant financial news
No fake Pathway usage - just solid news-to-price correlation
"""

import asyncio
import aiohttp
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
import logging
import json
import requests
from bs4 import BeautifulSoup
import re

@dataclass
class StockMovement:
    """Stock price movement with context"""
    symbol: str
    current_price: float
    previous_price: float
    change_percent: float
    change_amount: float
    volume: int
    timestamp: datetime
    market_cap: str = ""
    
@dataclass 
class NewsImpact:
    """News article with potential stock impact"""
    title: str
    summary: str
    url: str
    source: str
    timestamp: datetime
    relevance_score: float  # 0-1 how relevant to stock movement
    sentiment: str  # positive, negative, neutral
    impact_keywords: List[str]

class NewsStockCorrelator:
    """Correlates news with stock movements to explain price changes"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Keywords that indicate high market impact
        self.impact_keywords = {
            'positive': [
                'earnings beat', 'profit surge', 'revenue growth', 'breakthrough',
                'partnership', 'acquisition', 'expansion', 'innovation', 'upgrade',
                'bullish', 'outperform', 'strong results', 'record high'
            ],
            'negative': [
                'earnings miss', 'profit decline', 'revenue drop', 'lawsuit',
                'investigation', 'scandal', 'layoffs', 'downgrade', 'bearish',
                'underperform', 'weak results', 'concerns', 'risks'
            ]
        }
    
    async def get_stock_movements(self, symbols: List[str]) -> Dict[str, StockMovement]:
        """Get current stock movements for analysis"""
        movements = {}
        
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="2d")
                info = ticker.info
                
                if len(hist) >= 2:
                    current = hist['Close'].iloc[-1]
                    previous = hist['Close'].iloc[-2] 
                    
                    change_amount = current - previous
                    change_percent = (change_amount / previous) * 100
                    
                    movements[symbol] = StockMovement(
                        symbol=symbol,
                        current_price=current,
                        previous_price=previous,
                        change_percent=change_percent,
                        change_amount=change_amount,
                        volume=int(hist['Volume'].iloc[-1]),
                        timestamp=datetime.now(),
                        market_cap=info.get('marketCap', 'N/A')
                    )
                    
            except Exception as e:
                self.logger.error(f"Error getting data for {symbol}: {e}")
                
        return movements
    
    async def fetch_relevant_news(self, symbol: str, hours_back: int = 24) -> List[NewsImpact]:
        """Fetch news relevant to a specific stock"""
        news_articles = []
        
        try:
            # Search for company-specific news
            search_terms = [
                f"{symbol} stock",
                f"{symbol} earnings", 
                f"{symbol} news",
                f"{symbol} financial"
            ]
            
            for term in search_terms:
                articles = await self._search_financial_news(term, hours_back)
                news_articles.extend(articles)
                
            # Remove duplicates and sort by relevance
            unique_articles = {}
            for article in news_articles:
                if article.url not in unique_articles:
                    unique_articles[article.url] = article
                    
            sorted_articles = sorted(
                unique_articles.values(),
                key=lambda x: x.relevance_score,
                reverse=True
            )
            
            return sorted_articles[:10]  # Top 10 most relevant
            
        except Exception as e:
            self.logger.error(f"Error fetching news for {symbol}: {e}")
            return []
    
    async def _search_financial_news(self, query: str, hours_back: int) -> List[NewsImpact]:
        """Search for financial news using multiple sources"""
        articles = []
        
        # Source 1: Yahoo Finance
        try:
            articles.extend(await self._fetch_yahoo_news(query))
        except Exception as e:
            self.logger.error(f"Yahoo news error: {e}")
        
        # Source 2: MarketWatch  
        try:
            articles.extend(await self._fetch_marketwatch_news(query))
        except Exception as e:
            self.logger.error(f"MarketWatch news error: {e}")
            
        return articles
    
    async def _fetch_yahoo_news(self, query: str) -> List[NewsImpact]:
        """Fetch news from Yahoo Finance"""
        articles = []
        
        try:
            url = f"https://finance.yahoo.com/quote/{query.split()[0]}/news"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    html = await response.text()
                    
            soup = BeautifulSoup(html, 'html.parser')
            news_items = soup.find_all('div', class_='Ov(h)')
            
            for item in news_items[:5]:
                try:
                    title_elem = item.find('a')
                    if title_elem:
                        title = title_elem.get_text().strip()
                        url = title_elem.get('href', '')
                        
                        if url.startswith('/'):
                            url = f"https://finance.yahoo.com{url}"
                        
                        # Analyze sentiment and relevance
                        sentiment = self._analyze_sentiment(title)
                        relevance = self._calculate_relevance(title, query)
                        keywords = self._extract_impact_keywords(title)
                        
                        articles.append(NewsImpact(
                            title=title,
                            summary=title,  # Use title as summary for now
                            url=url,
                            source="Yahoo Finance",
                            timestamp=datetime.now(),
                            relevance_score=relevance,
                            sentiment=sentiment,
                            impact_keywords=keywords
                        ))
                        
                except Exception as e:
                    continue
                    
        except Exception as e:
            self.logger.error(f"Yahoo Finance scraping error: {e}")
            
        return articles
    
    async def _fetch_marketwatch_news(self, query: str) -> List[NewsImpact]:
        """Fetch news from MarketWatch"""
        articles = []
        
        try:
            symbol = query.split()[0]
            url = f"https://www.marketwatch.com/investing/stock/{symbol}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    html = await response.text()
                    
            soup = BeautifulSoup(html, 'html.parser')
            news_items = soup.find_all('a', class_='link')
            
            for item in news_items[:5]:
                try:
                    title = item.get_text().strip()
                    url = item.get('href', '')
                    
                    if not url.startswith('http'):
                        url = f"https://www.marketwatch.com{url}"
                    
                    if len(title) > 20:  # Filter out very short titles
                        sentiment = self._analyze_sentiment(title)
                        relevance = self._calculate_relevance(title, query)
                        keywords = self._extract_impact_keywords(title)
                        
                        articles.append(NewsImpact(
                            title=title,
                            summary=title,
                            url=url,
                            source="MarketWatch",
                            timestamp=datetime.now(),
                            relevance_score=relevance,
                            sentiment=sentiment,
                            impact_keywords=keywords
                        ))
                        
                except Exception as e:
                    continue
                    
        except Exception as e:
            self.logger.error(f"MarketWatch scraping error: {e}")
            
        return articles
    
    def _analyze_sentiment(self, text: str) -> str:
        """Simple sentiment analysis"""
        text_lower = text.lower()
        
        positive_count = sum(1 for word in self.impact_keywords['positive'] 
                           if word in text_lower)
        negative_count = sum(1 for word in self.impact_keywords['negative'] 
                           if word in text_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def _calculate_relevance(self, text: str, query: str) -> float:
        """Calculate how relevant the text is to the query"""
        text_lower = text.lower()
        query_lower = query.lower()
        
        # Base relevance for containing the symbol
        relevance = 0.5
        
        # Boost for containing query terms
        query_terms = query_lower.split()
        for term in query_terms:
            if term in text_lower:
                relevance += 0.2
        
        # Boost for containing impact keywords
        all_keywords = self.impact_keywords['positive'] + self.impact_keywords['negative']
        for keyword in all_keywords:
            if keyword in text_lower:
                relevance += 0.1
        
        return min(1.0, relevance)
    
    def _extract_impact_keywords(self, text: str) -> List[str]:
        """Extract keywords that indicate market impact"""
        text_lower = text.lower()
        found_keywords = []
        
        all_keywords = self.impact_keywords['positive'] + self.impact_keywords['negative']
        for keyword in all_keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
        
        return found_keywords
    
    async def explain_price_movement(self, symbol: str, movement: StockMovement) -> str:
        """Generate explanation for why a stock price moved"""
        
        # Only explain significant movements (>2%)
        if abs(movement.change_percent) < 2.0:
            return f"{symbol} showed minor movement ({movement.change_percent:+.2f}%) - normal market fluctuation."
        
        # Get relevant news
        news = await self.fetch_relevant_news(symbol)
        
        if not news:
            return f"{symbol} moved {movement.change_percent:+.2f}% with no specific news found. This could be due to general market sentiment or technical trading."
        
        # Find most relevant news
        top_news = news[0]
        
        # Create explanation
        direction = "surged" if movement.change_percent > 0 else "declined"
        
        explanation = f"""
{symbol} {direction} {abs(movement.change_percent):.2f}% to ${movement.current_price:.2f}.

📰 KEY NEWS: {top_news.title}

🔍 ANALYSIS: This {top_news.sentiment} news likely {('drove the stock higher' if movement.change_percent > 0 else 'pressured the stock lower')}. 

💡 IMPACT FACTORS: {', '.join(top_news.impact_keywords) if top_news.impact_keywords else 'Market sentiment and trading volume'}

📊 TRADING DETAILS:
• Price Change: ${movement.change_amount:+.2f} ({movement.change_percent:+.2f}%)
• Volume: {movement.volume:,} shares
• Source: {top_news.source}
        """.strip()
        
        return explanation

# Create global instance
_correlator = None

def get_news_correlator():
    """Get global news correlator instance"""
    global _correlator
    if _correlator is None:
        _correlator = NewsStockCorrelator()
    return _correlator

# Test function
async def test_news_correlation():
    """Test the news correlation system"""
    print("🔍 Testing News-Stock Correlation System...")
    
    correlator = NewsStockCorrelator()
    
    # Test with a few popular stocks
    symbols = ["AAPL", "TSLA", "GOOGL"]
    
    print("\n📊 Getting stock movements...")
    movements = await correlator.get_stock_movements(symbols)
    
    for symbol, movement in movements.items():
        print(f"\n📈 {symbol}: ${movement.current_price:.2f} ({movement.change_percent:+.2f}%)")
        
        if abs(movement.change_percent) > 1.0:  # Significant movement
            print("🔍 Fetching relevant news...")
            explanation = await correlator.explain_price_movement(symbol, movement)
            print(f"\n📰 EXPLANATION:\n{explanation}")
        else:
            print("📊 Minor movement - no detailed analysis needed")

if __name__ == "__main__":
    asyncio.run(test_news_correlation())
