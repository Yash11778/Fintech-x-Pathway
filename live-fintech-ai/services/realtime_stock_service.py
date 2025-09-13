"""
Real-Time Dynamic Stock Service
Generates realistic stock prices that fluctuate every few seconds
Simulates real market behavior for live demo
"""

import random
import time
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
import logging
import json

@dataclass
class RealTimeStockPrice:
    """Real-time stock price with dynamic updates"""
    symbol: str
    price: float
    previous_price: float
    change_percent: float
    change_amount: float
    volume: int
    timestamp: datetime
    market_cap: Optional[str] = None
    pe_ratio: Optional[float] = None
    day_high: Optional[float] = None
    day_low: Optional[float] = None
    volatility: float = 2.0  # Base volatility for price changes
    
    def update_price(self):
        """Update price with realistic market simulation"""
        # Store previous price
        self.previous_price = self.price
        
        # Generate realistic price movement
        # Market hours have different volatility patterns
        current_hour = datetime.now().hour
        
        # Higher volatility during market open/close
        if 9 <= current_hour <= 10 or 15 <= current_hour <= 16:
            volatility_multiplier = 1.5
        elif 11 <= current_hour <= 14:  # Lunch time - lower volatility
            volatility_multiplier = 0.7
        else:  # After hours - very low volatility
            volatility_multiplier = 0.3
            
        # Calculate price change
        max_change = self.volatility * volatility_multiplier / 100
        change_percent = random.uniform(-max_change, max_change)
        
        # Add some momentum (trending behavior)
        if hasattr(self, '_momentum'):
            # Continue previous trend with 60% probability
            if random.random() < 0.6:
                change_percent += self._momentum * 0.3
        
        # Apply price change
        price_change = self.price * change_percent
        self.price = max(0.01, self.price + price_change)  # Ensure positive price
        
        # Update derived values
        self.change_amount = self.price - self.previous_price
        self.change_percent = (self.change_amount / self.previous_price) * 100
        self.timestamp = datetime.now()
        
        # Update day high/low
        if self.day_high is None or self.price > self.day_high:
            self.day_high = self.price
        if self.day_low is None or self.price < self.day_low:
            self.day_low = self.price
            
        # Store momentum for next update
        self._momentum = change_percent
        
        # Simulate volume changes
        base_volume = 1000000
        volume_change = random.uniform(0.5, 2.0)
        self.volume = int(base_volume * volume_change)

class RealTimeDynamicStockService:
    """Service that provides truly dynamic, real-time stock prices"""
    
    def __init__(self):
        """Initialize the real-time stock service"""
        self.logger = logging.getLogger(__name__)
        self.session = None
        self.stock_data = {}
        self.last_update = {}
        self.is_running = False
        
        # Base stock symbols with realistic starting prices
        self.stock_symbols = [
            "AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "META", "NVDA", "NFLX",
            "AMD", "INTC", "CRM", "ORCL", "ADBE", "PYPL", "UBER"
        ]
        
        # Initialize stock data with realistic base prices
        self._initialize_stock_data()
    
    def _initialize_stock_data(self):
        """Initialize stock data with realistic base prices"""
        # Realistic base prices for major stocks
        base_prices = {
            "AAPL": 175.50, "GOOGL": 135.25, "MSFT": 338.75, "TSLA": 248.90,
            "AMZN": 145.60, "META": 285.40, "NVDA": 425.80, "NFLX": 390.25,
            "AMD": 102.15, "INTC": 23.45, "CRM": 210.30, "ORCL": 115.80,
            "ADBE": 520.40, "PYPL": 58.90, "UBER": 62.35
        }
        
        # Market caps for display
        market_caps = {
            "AAPL": "2.8T", "GOOGL": "1.7T", "MSFT": "2.5T", "TSLA": "785B",
            "AMZN": "1.5T", "META": "720B", "NVDA": "1.1T", "NFLX": "170B",
            "AMD": "165B", "INTC": "98B", "CRM": "210B", "ORCL": "320B",
            "ADBE": "240B", "PYPL": "67B", "UBER": "125B"
        }
        
        # Different volatility levels for different stocks
        volatilities = {
            "AAPL": 1.8, "GOOGL": 2.2, "MSFT": 1.5, "TSLA": 4.5,  # TSLA very volatile
            "AMZN": 2.8, "META": 3.2, "NVDA": 3.8, "NFLX": 3.0,
            "AMD": 3.5, "INTC": 2.0, "CRM": 2.5, "ORCL": 1.8,
            "ADBE": 2.3, "PYPL": 3.8, "UBER": 4.2
        }
        
        for symbol in self.stock_symbols:
            base_price = base_prices.get(symbol, 100.0)
            # Add some random variation to base price (±5%)
            current_price = base_price * random.uniform(0.95, 1.05)
            
            self.stock_data[symbol] = RealTimeStockPrice(
                symbol=symbol,
                price=current_price,
                previous_price=current_price,
                change_percent=0.0,
                change_amount=0.0,
                volume=random.randint(500000, 2000000),
                timestamp=datetime.now(),
                market_cap=market_caps.get(symbol, "N/A"),
                pe_ratio=random.uniform(15.0, 35.0),
                day_high=current_price,
                day_low=current_price,
                volatility=volatilities.get(symbol, 2.0)
            )
            
            self.last_update[symbol] = datetime.now()
    
    async def get_real_time_prices(self) -> Dict[str, RealTimeStockPrice]:
        """Get current real-time prices for all stocks"""
        current_time = datetime.now()
        
        # Update prices that haven't been updated in the last 2-5 seconds
        for symbol, stock in self.stock_data.items():
            last_update = self.last_update.get(symbol, datetime.min)
            
            # Random update interval between 2-8 seconds to simulate real market
            update_interval = random.uniform(2, 8)
            
            if (current_time - last_update).total_seconds() >= update_interval:
                # Update the price with realistic market simulation
                stock.update_price()
                self.last_update[symbol] = current_time
                
                # Log significant movements
                if abs(stock.change_percent) > 2.0:
                    self.logger.info(
                        f"📈 {symbol}: {stock.change_percent:+.2f}% "
                        f"(${stock.price:.2f})"
                    )
        
        return self.stock_data.copy()
    
    async def get_stock_price(self, symbol: str) -> Optional[RealTimeStockPrice]:
        """Get real-time price for a specific stock"""
        if symbol not in self.stock_data:
            return None
            
        # Update this specific stock if needed
        current_time = datetime.now()
        last_update = self.last_update.get(symbol, datetime.min)
        
        if (current_time - last_update).total_seconds() >= 3:
            self.stock_data[symbol].update_price()
            self.last_update[symbol] = current_time
        
        return self.stock_data[symbol]
    
    async def start_continuous_updates(self):
        """Start continuous price updates in background"""
        self.is_running = True
        self.logger.info("🚀 Starting real-time price updates...")
        
        while self.is_running:
            try:
                # Update all prices
                await self.get_real_time_prices()
                
                # Wait 1-3 seconds before next update cycle
                await asyncio.sleep(random.uniform(1, 3))
                
            except Exception as e:
                self.logger.error(f"Error in continuous updates: {e}")
                await asyncio.sleep(5)
    
    def stop_continuous_updates(self):
        """Stop continuous price updates"""
        self.is_running = False
        self.logger.info("🛑 Stopped real-time price updates")
    
    async def simulate_market_event(self, symbol: str, impact: float):
        """Simulate a major market event affecting a stock"""
        if symbol in self.stock_data:
            stock = self.stock_data[symbol]
            
            # Apply immediate impact
            event_change = impact / 100  # Convert percentage to decimal
            stock.price *= (1 + event_change)
            stock.change_percent = impact
            stock.change_amount = stock.price - stock.previous_price
            stock.timestamp = datetime.now()
            
            # Increase volatility temporarily
            stock.volatility *= 2.0
            
            self.logger.info(
                f"📰 Market Event: {symbol} moved {impact:+.2f}% to ${stock.price:.2f}"
            )
            
            # Schedule volatility reduction
            asyncio.create_task(self._reduce_volatility(symbol, 300))  # 5 minutes
    
    async def _reduce_volatility(self, symbol: str, delay: int):
        """Gradually reduce volatility after market event"""
        await asyncio.sleep(delay)
        if symbol in self.stock_data:
            self.stock_data[symbol].volatility /= 2.0
            self.logger.info(f"📉 Volatility normalized for {symbol}")
    
    def get_market_summary(self) -> Dict:
        """Get overall market summary"""
        if not self.stock_data:
            return {}
        
        prices = list(self.stock_data.values())
        
        # Calculate market metrics
        avg_change = sum(stock.change_percent for stock in prices) / len(prices)
        gainers = sum(1 for stock in prices if stock.change_percent > 0)
        losers = sum(1 for stock in prices if stock.change_percent < 0)
        
        # Market sentiment
        if avg_change > 1.0:
            sentiment = "🟢 Bullish"
        elif avg_change < -1.0:
            sentiment = "🔴 Bearish"
        else:
            sentiment = "🟡 Neutral"
        
        return {
            "total_stocks": len(prices),
            "gainers": gainers,
            "losers": losers,
            "unchanged": len(prices) - gainers - losers,
            "avg_change": avg_change,
            "sentiment": sentiment,
            "last_update": datetime.now().strftime("%H:%M:%S")
        }
    
    async def cleanup(self):
        """Cleanup resources"""
        self.stop_continuous_updates()
        if self.session:
            await self.session.close()

# Global instance for the dashboard
_real_time_service = None

def get_real_time_service() -> RealTimeDynamicStockService:
    """Get or create global real-time service instance"""
    global _real_time_service
    if _real_time_service is None:
        _real_time_service = RealTimeDynamicStockService()
    return _real_time_service

# Test function
async def test_real_time_service():
    """Test the real-time dynamic stock service"""
    print("🚀 Testing Real-Time Dynamic Stock Service...")
    
    service = RealTimeDynamicStockService()
    
    # Get initial prices
    print("\n📊 Initial Prices:")
    prices = await service.get_real_time_prices()
    for symbol, stock in list(prices.items())[:5]:
        print(f"   {symbol}: ${stock.price:.2f}")
    
    # Wait and show price changes
    print("\n⏱️  Waiting 10 seconds for price updates...")
    await asyncio.sleep(10)
    
    print("\n📈 Updated Prices:")
    updated_prices = await service.get_real_time_prices()
    for symbol, stock in list(updated_prices.items())[:5]:
        change_symbol = "📈" if stock.change_percent > 0 else "📉" if stock.change_percent < 0 else "📊"
        print(f"   {symbol}: ${stock.price:.2f} ({stock.change_percent:+.2f}%) {change_symbol}")
    
    # Simulate market event
    print("\n📰 Simulating market event for TSLA...")
    await service.simulate_market_event("TSLA", 5.5)  # 5.5% jump
    
    tsla = await service.get_stock_price("TSLA")
    print(f"   TSLA after event: ${tsla.price:.2f} ({tsla.change_percent:+.2f}%)")
    
    # Market summary
    summary = service.get_market_summary()
    print(f"\n📊 Market Summary:")
    print(f"   Sentiment: {summary['sentiment']}")
    print(f"   Gainers: {summary['gainers']}, Losers: {summary['losers']}")
    print(f"   Average Change: {summary['avg_change']:+.2f}%")
    
    await service.cleanup()
    print("\n✅ Test completed!")

if __name__ == "__main__":
    asyncio.run(test_real_time_service())
