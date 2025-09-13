"""
LLM Service for Live Fintech AI Assistant
Handles AI-powered explanations using OpenAI API
"""

import openai
from typing import List, Optional, Dict
from dataclasses import dataclass
from datetime import datetime
from config import Config
from services.stock_service import PriceMovement
from services.news_service import NewsArticle

@dataclass
class AIExplanation:
    """Data structure for AI-generated explanations"""
    symbol: str
    explanation: str
    confidence_score: float
    timestamp: datetime
    news_articles: List[NewsArticle]
    price_movement: PriceMovement
    explanation_type: str  # "news_based", "technical_analysis", "anomaly"

class LLMService:
    """Service for generating AI explanations of stock movements"""
    
    def __init__(self):
        openai.api_key = Config.OPENAI_API_KEY
        self.model = Config.OPENAI_MODEL
        self.max_tokens = Config.MAX_TOKENS
        
    def generate_movement_explanation(
        self, 
        movement: PriceMovement, 
        news_articles: List[NewsArticle]
    ) -> AIExplanation:
        """
        Generate an AI explanation for a stock price movement
        
        Args:
            movement: PriceMovement object containing price change details
            news_articles: List of relevant NewsArticle objects
            
        Returns:
            AIExplanation object with AI-generated analysis
        """
        try:
            # Determine explanation type based on available news
            explanation_type = "news_based" if news_articles else "anomaly"
            
            # Create context prompt
            prompt = self._build_explanation_prompt(movement, news_articles)
            
            # Generate explanation using OpenAI
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=0.7
            )
            
            explanation_text = response.choices[0].message.content.strip()
            
            # Calculate confidence score based on available information
            confidence_score = self._calculate_confidence(movement, news_articles)
            
            explanation = AIExplanation(
                symbol=movement.symbol,
                explanation=explanation_text,
                confidence_score=confidence_score,
                timestamp=datetime.now(),
                news_articles=news_articles,
                price_movement=movement,
                explanation_type=explanation_type
            )
            
            print(f"✅ Generated explanation for {movement.symbol} ({explanation_type})")
            return explanation
            
        except Exception as e:
            print(f"❌ Error generating explanation for {movement.symbol}: {e}")
            
            # Return fallback explanation
            return self._create_fallback_explanation(movement, news_articles)
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the AI assistant"""
        return """You are a professional financial analyst AI assistant specializing in explaining stock price movements. 

Your role is to:
1. Analyze stock price movements and provide clear, concise explanations
2. Correlate price changes with relevant news when available
3. Identify potential causes for unusual market movements
4. Provide actionable insights for traders and investors
5. Distinguish between news-driven moves and technical/anomalous movements

Guidelines:
- Keep explanations under 150 words
- Use professional but accessible language
- Focus on the most likely causes
- If news is available, explain the connection clearly
- If no news is available, mention it's an unusual movement that may warrant investigation
- Include relevant market context when possible
- Be objective and avoid speculation without basis"""

    def _build_explanation_prompt(self, movement: PriceMovement, news_articles: List[NewsArticle]) -> str:
        """
        Build the prompt for explaining a stock movement
        
        Args:
            movement: PriceMovement object
            news_articles: List of relevant news articles
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""Analyze this stock movement:

Stock: {movement.symbol}
Price Change: {movement.change_percent:+.2f}% (${movement.previous_price:.2f} → ${movement.current_price:.2f})
Time: {movement.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
Movement Type: {movement.movement_type.replace('_', ' ').title()}

"""
        
        if news_articles:
            prompt += "Recent News Articles:\n"
            for i, article in enumerate(news_articles[:3], 1):  # Limit to top 3 articles
                prompt += f"{i}. {article.title}\n"
                if article.description:
                    prompt += f"   Summary: {article.description[:100]}...\n"
                prompt += f"   Source: {article.source} | Published: {article.published_at.strftime('%H:%M')}\n\n"
        else:
            prompt += "No relevant news articles found in the time window.\n\n"
        
        prompt += """Please provide a concise explanation of this price movement. Consider:
1. Is this movement likely related to the news articles (if any)?
2. What might be driving this price change?
3. Is this a normal market reaction or something unusual?
4. Any additional context traders should be aware of?

Provide a clear, professional explanation in 2-3 sentences."""
        
        return prompt
    
    def _calculate_confidence(self, movement: PriceMovement, news_articles: List[NewsArticle]) -> float:
        """
        Calculate confidence score for the explanation
        
        Args:
            movement: PriceMovement object
            news_articles: List of relevant news articles
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        base_confidence = 0.3  # Base confidence for any movement detection
        
        # Add confidence based on news availability
        if news_articles:
            news_confidence = min(0.4, len(news_articles) * 0.1)  # Up to 0.4 for news
            base_confidence += news_confidence
        
        # Add confidence based on movement magnitude
        magnitude_confidence = min(0.3, abs(movement.change_percent) / 10.0)  # Up to 0.3 for large moves
        base_confidence += magnitude_confidence
        
        return min(1.0, base_confidence)
    
    def _create_fallback_explanation(self, movement: PriceMovement, news_articles: List[NewsArticle]) -> AIExplanation:
        """
        Create a fallback explanation when AI generation fails
        
        Args:
            movement: PriceMovement object
            news_articles: List of relevant news articles
            
        Returns:
            Fallback AIExplanation object
        """
        direction = "increased" if movement.change_percent > 0 else "decreased"
        magnitude = "significantly" if abs(movement.change_percent) > 5 else "notably"
        
        if news_articles:
            explanation = f"{movement.symbol} {magnitude} {direction} by {movement.change_percent:+.2f}% " \
                         f"following recent news developments. This movement appears to be related to " \
                         f"market reactions to recent headlines."
            explanation_type = "news_based"
        else:
            explanation = f"{movement.symbol} {magnitude} {direction} by {movement.change_percent:+.2f}% " \
                         f"without clear news catalysts in the immediate timeframe. This could indicate " \
                         f"technical trading patterns or delayed reactions to earlier events."
            explanation_type = "anomaly"
        
        return AIExplanation(
            symbol=movement.symbol,
            explanation=explanation,
            confidence_score=0.3,  # Low confidence for fallback
            timestamp=datetime.now(),
            news_articles=news_articles,
            price_movement=movement,
            explanation_type=explanation_type
        )
    
    def generate_market_summary(self, explanations: List[AIExplanation]) -> str:
        """
        Generate a market summary based on multiple explanations
        
        Args:
            explanations: List of AIExplanation objects
            
        Returns:
            Market summary string
        """
        if not explanations:
            return "No significant market movements detected in the current period."
        
        try:
            # Build summary prompt
            prompt = "Based on these stock movements, provide a brief market summary:\n\n"
            
            for exp in explanations:
                prompt += f"- {exp.symbol}: {exp.price_movement.change_percent:+.2f}% ({exp.explanation_type})\n"
            
            prompt += "\nProvide a 2-3 sentence market overview highlighting key themes and patterns."
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a financial market analyst. Provide concise market summaries."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=100,
                temperature=0.5
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"❌ Error generating market summary: {e}")
            # Fallback summary
            up_moves = len([exp for exp in explanations if exp.price_movement.change_percent > 0])
            down_moves = len(explanations) - up_moves
            
            return f"Market showing mixed activity with {up_moves} stocks moving up and {down_moves} moving down. " \
                   f"Significant movements detected across {len(explanations)} symbols."

# Test function
def test_llm_service():
    """Test the LLM service functionality"""
    print("🧪 Testing LLM Service...")
    
    service = LLMService()
    
    # Create mock data for testing
    from services.stock_service import PriceMovement
    from services.news_service import NewsArticle
    
    # Mock price movement
    mock_movement = PriceMovement(
        symbol="AAPL",
        current_price=175.50,
        previous_price=170.00,
        change_percent=3.24,
        timestamp=datetime.now(),
        movement_type="significant_up"
    )
    
    # Mock news articles
    mock_news = [
        NewsArticle(
            title="Apple Reports Strong Quarterly Earnings",
            description="Apple exceeded analyst expectations with strong iPhone sales",
            url="https://example.com/news1",
            published_at=datetime.now(),
            source="Financial Times",
            symbol="AAPL"
        )
    ]
    
    print("\n🤖 Testing explanation generation:")
    explanation = service.generate_movement_explanation(mock_movement, mock_news)
    print(f"✅ Generated explanation: {explanation.explanation[:50]}...")
    print(f"   Confidence: {explanation.confidence_score:.2f}")
    print(f"   Type: {explanation.explanation_type}")

if __name__ == "__main__":
    test_llm_service()
