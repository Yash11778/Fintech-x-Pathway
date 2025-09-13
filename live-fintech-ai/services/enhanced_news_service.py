"""
Enhanced News Service for Beautiful Frontend
Provides comprehensive news data with sentiment analysis and categorization
"""

import aiohttp
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json
import logging
from dataclasses import dataclass, asdict
import random

from services.news_service import NewsArticle
from services.web_news_service import WebScrapingNewsService

@dataclass
class EnhancedNewsArticle(NewsArticle):
    """Enhanced news article with additional metadata"""
    category: str = "general"
    sentiment_score: float = 0.0  # -1 to 1 scale
    impact_level: str = "medium"  # low, medium, high
    market_relevance: float = 0.5  # 0 to 1 scale
    keywords: List[str] = None
    read_time: int = 3  # estimated minutes
    
    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []

class EnhancedNewsService:
    """Enhanced news service with sentiment analysis and categorization"""
    
    def __init__(self):
        """Initialize enhanced news service"""
        self.web_service = WebScrapingNewsService()
        self.logger = logging.getLogger(__name__)
        
        # News categories
        self.categories = {
            "earnings": ["earnings", "quarterly", "revenue", "profit", "financial results"],
            "mergers": ["merger", "acquisition", "deal", "takeover", "buyout"],
            "tech": ["innovation", "technology", "AI", "software", "digital"],
            "regulatory": ["SEC", "FDA", "regulation", "compliance", "policy"],
            "market": ["market", "trading", "volume", "price", "volatility"]
        }
        
        # Impact keywords
        self.high_impact_keywords = [
            "breakthrough", "major", "significant", "unprecedented", "massive",
            "record", "historic", "game-changing", "revolutionary", "critical"
        ]
        
        self.low_impact_keywords = [
            "minor", "slight", "small", "limited", "modest", "gradual", "routine"
        ]
    
    async def fetch_enhanced_news(self, symbol: Optional[str] = None, limit: int = 20) -> List[EnhancedNewsArticle]:
        """Fetch enhanced news with analysis"""
        try:
            # Get base news articles
            if symbol:
                articles = self.web_service.fetch_news_for_symbol(symbol, limit)
            else:
                articles = self.web_service.fetch_trending_news(limit)
            
            # Enhance each article
            enhanced_articles = []
            for article in articles:
                enhanced = await self._enhance_article(article)
                enhanced_articles.append(enhanced)
            
            # Sort by relevance and impact
            enhanced_articles.sort(
                key=lambda x: (x.market_relevance * 0.6 + 
                              (1 if x.impact_level == "high" else 0.5 if x.impact_level == "medium" else 0.2) * 0.4),
                reverse=True
            )
            
            return enhanced_articles
            
        except Exception as e:
            self.logger.error(f"Error fetching enhanced news: {e}")
            return []
    
    async def _enhance_article(self, article: NewsArticle) -> EnhancedNewsArticle:
        """Enhance article with additional metadata"""
        try:
            title = getattr(article, 'title', '').lower()
            description = getattr(article, 'description', '').lower()
            content = f"{title} {description}"
            
            # Categorize article
            category = self._categorize_article(content)
            
            # Analyze sentiment (simplified)
            sentiment_score = self._analyze_sentiment(content)
            
            # Determine impact level
            impact_level = self._determine_impact(content)
            
            # Calculate market relevance
            market_relevance = self._calculate_market_relevance(content, getattr(article, 'symbol', ''))
            
            # Extract keywords
            keywords = self._extract_keywords(content)
            
            # Estimate read time
            read_time = max(1, len(content.split()) // 200)
            
            return EnhancedNewsArticle(
                title=getattr(article, 'title', ''),
                url=getattr(article, 'url', ''),
                description=getattr(article, 'description', ''),
                source=getattr(article, 'source', 'Unknown'),
                timestamp=getattr(article, 'timestamp', datetime.now()),
                symbol=getattr(article, 'symbol', ''),
                category=category,
                sentiment_score=sentiment_score,
                impact_level=impact_level,
                market_relevance=market_relevance,
                keywords=keywords,
                read_time=read_time
            )
            
        except Exception as e:
            self.logger.error(f"Error enhancing article: {e}")
            # Return basic enhanced article
            return EnhancedNewsArticle(
                title=getattr(article, 'title', ''),
                url=getattr(article, 'url', ''),
                description=getattr(article, 'description', ''),
                source=getattr(article, 'source', 'Unknown'),
                timestamp=getattr(article, 'timestamp', datetime.now()),
                symbol=getattr(article, 'symbol', '')
            )
    
    def _categorize_article(self, content: str) -> str:
        """Categorize article based on content"""
        for category, keywords in self.categories.items():
            if any(keyword in content for keyword in keywords):
                return category
        return "general"
    
    def _analyze_sentiment(self, content: str) -> float:
        """Simple sentiment analysis"""
        positive_words = [
            "growth", "increase", "profit", "success", "strong", "positive", 
            "breakthrough", "innovation", "surge", "rally", "bullish", "gains"
        ]
        
        negative_words = [
            "decline", "loss", "failure", "weak", "negative", "crash", 
            "drop", "fall", "bearish", "concerns", "risks", "challenges"
        ]
        
        positive_count = sum(1 for word in positive_words if word in content)
        negative_count = sum(1 for word in negative_words if word in content)
        
        total_words = len(content.split())
        if total_words == 0:
            return 0.0
        
        sentiment = (positive_count - negative_count) / max(total_words / 100, 1)
        return max(-1.0, min(1.0, sentiment))
    
    def _determine_impact(self, content: str) -> str:
        """Determine impact level of news"""
        if any(keyword in content for keyword in self.high_impact_keywords):
            return "high"
        elif any(keyword in content for keyword in self.low_impact_keywords):
            return "low"
        else:
            return "medium"
    
    def _calculate_market_relevance(self, content: str, symbol: str) -> float:
        """Calculate market relevance score"""
        relevance = 0.5  # Base relevance
        
        # Higher relevance for specific symbols
        if symbol and symbol.upper() in content.upper():
            relevance += 0.3
        
        # Market-related keywords boost relevance
        market_keywords = [
            "stock", "shares", "trading", "market", "investor", "financial",
            "earnings", "revenue", "price", "valuation", "analyst"
        ]
        
        keyword_count = sum(1 for keyword in market_keywords if keyword in content)
        relevance += min(0.2, keyword_count * 0.05)
        
        return min(1.0, relevance)
    
    def _extract_keywords(self, content: str) -> List[str]:
        """Extract key keywords from content"""
        # Simple keyword extraction
        words = content.split()
        
        # Filter common financial keywords
        financial_keywords = [
            "earnings", "revenue", "profit", "growth", "market", "stock",
            "trading", "investment", "analyst", "forecast", "valuation"
        ]
        
        keywords = [word for word in words if word in financial_keywords]
        return list(set(keywords))[:5]  # Return top 5 unique keywords
    
    async def get_market_sentiment_summary(self) -> Dict:
        """Get overall market sentiment summary"""
        try:
            # Get recent trending news
            articles = await self.fetch_enhanced_news(limit=50)
            
            if not articles:
                return {
                    "overall_sentiment": "neutral",
                    "sentiment_score": 0.0,
                    "article_count": 0,
                    "categories": {},
                    "high_impact_count": 0
                }
            
            # Calculate overall sentiment
            total_sentiment = sum(article.sentiment_score for article in articles)
            avg_sentiment = total_sentiment / len(articles)
            
            # Categorize sentiment
            if avg_sentiment > 0.2:
                overall_sentiment = "bullish"
            elif avg_sentiment < -0.2:
                overall_sentiment = "bearish"
            else:
                overall_sentiment = "neutral"
            
            # Count categories
            categories = {}
            for article in articles:
                category = article.category
                categories[category] = categories.get(category, 0) + 1
            
            # Count high impact articles
            high_impact_count = sum(1 for article in articles if article.impact_level == "high")
            
            return {
                "overall_sentiment": overall_sentiment,
                "sentiment_score": avg_sentiment,
                "article_count": len(articles),
                "categories": categories,
                "high_impact_count": high_impact_count,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting market sentiment: {e}")
            return {
                "overall_sentiment": "neutral",
                "sentiment_score": 0.0,
                "article_count": 0,
                "categories": {},
                "high_impact_count": 0
            }
    
    async def get_symbol_news_analysis(self, symbol: str) -> Dict:
        """Get detailed news analysis for specific symbol"""
        try:
            articles = await self.fetch_enhanced_news(symbol=symbol, limit=20)
            
            if not articles:
                return {
                    "symbol": symbol,
                    "sentiment": "neutral",
                    "sentiment_score": 0.0,
                    "article_count": 0,
                    "recent_headlines": [],
                    "impact_summary": "No recent news"
                }
            
            # Calculate sentiment
            sentiment_scores = [article.sentiment_score for article in articles]
            avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
            
            sentiment_label = "bullish" if avg_sentiment > 0.1 else "bearish" if avg_sentiment < -0.1 else "neutral"
            
            # Get recent headlines
            recent_headlines = [article.title for article in articles[:5]]
            
            # Create impact summary
            high_impact = sum(1 for article in articles if article.impact_level == "high")
            impact_summary = f"{high_impact} high-impact stories in recent news"
            
            return {
                "symbol": symbol,
                "sentiment": sentiment_label,
                "sentiment_score": avg_sentiment,
                "article_count": len(articles),
                "recent_headlines": recent_headlines,
                "impact_summary": impact_summary,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing symbol news: {e}")
            return {
                "symbol": symbol,
                "sentiment": "neutral",
                "sentiment_score": 0.0,
                "article_count": 0,
                "recent_headlines": [],
                "impact_summary": "Analysis unavailable"
            }
    
    def get_news_by_category(self, articles: List[EnhancedNewsArticle], category: str) -> List[EnhancedNewsArticle]:
        """Filter articles by category"""
        return [article for article in articles if article.category == category]
    
    def get_high_impact_news(self, articles: List[EnhancedNewsArticle]) -> List[EnhancedNewsArticle]:
        """Get high impact news articles"""
        return [article for article in articles if article.impact_level == "high"]

# Example usage and testing
async def test_enhanced_news_service():
    """Test the enhanced news service"""
    service = EnhancedNewsService()
    
    print("🚀 Testing Enhanced News Service...")
    
    # Test trending news
    trending = await service.fetch_enhanced_news(limit=5)
    print(f"📰 Found {len(trending)} enhanced articles")
    
    if trending:
        print("\n📊 Sample Enhanced Article:")
        article = trending[0]
        print(f"Title: {article.title}")
        print(f"Category: {article.category}")
        print(f"Sentiment: {article.sentiment_score:.2f}")
        print(f"Impact: {article.impact_level}")
        print(f"Relevance: {article.market_relevance:.2f}")
        print(f"Keywords: {article.keywords}")
    
    # Test market sentiment
    sentiment = await service.get_market_sentiment_summary()
    print(f"\n📈 Market Sentiment: {sentiment['overall_sentiment']}")
    print(f"📊 Sentiment Score: {sentiment['sentiment_score']:.2f}")
    print(f"📰 Articles Analyzed: {sentiment['article_count']}")

if __name__ == "__main__":
    asyncio.run(test_enhanced_news_service())
