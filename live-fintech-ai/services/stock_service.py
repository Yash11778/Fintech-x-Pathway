"""
Stock Service for Live Fintech AI Assistant
Handles real-time stock price fetching using AlphaVantage API
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from config import Config

@dataclass
class StockPrice:
    """Data structure for stock price information"""
    symbol: str
    price: float
    timestamp: datetime
    change_percent: Optional[float] = None
    volume: Optional[int] = None
    previous_close: Optional[float] = None

@dataclass
class PriceMovement:
    """Data structure for detected price movements"""
    symbol: str
    current_price: float
    previous_price: float
    change_percent: float
    timestamp: datetime
    movement_type: str  # "significant_up", "significant_down", "normal"

class StockService:
    """Service for fetching live stock prices and detecting movements"""
    
    def __init__(self):
        self.api_key = Config.ALPHA_VANTAGE_API_KEY
        self.base_url = Config.ALPHA_VANTAGE_BASE_URL
        self.symbols = Config.STOCK_SYMBOLS
        self.threshold = Config.PRICE_MOVEMENT_THRESHOLD_PERCENT
        self.price_history: Dict[str, List[StockPrice]] = {symbol: [] for symbol in self.symbols}
        
    def fetch_current_price(self, symbol: str) -> Optional[StockPrice]:
        """
        Fetch current stock price for a given symbol using AlphaVantage API
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            
        Returns:
            StockPrice object or None if fetch fails
        """
        try:
            # Use GLOBAL_QUOTE function for real-time price
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': symbol,
                'apikey': self.api_key
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'Global Quote' not in data:
                print(f"❌ No data returned for {symbol}: {data}")
                return None
                
            quote = data['Global Quote']
            
            # Extract price information
            current_price = float(quote['05. price'])
            change_percent = float(quote['10. change percent'].rstrip('%'))
            volume = int(quote['06. volume'])
            previous_close = float(quote['08. previous close'])
            
            stock_price = StockPrice(
                symbol=symbol,
                price=current_price,
                timestamp=datetime.now(),
                change_percent=change_percent,
                volume=volume,
                previous_close=previous_close
            )
            
            # Store in price history
            self.price_history[symbol].append(stock_price)
            
            # Keep only last 100 entries per symbol
            if len(self.price_history[symbol]) > 100:
                self.price_history[symbol] = self.price_history[symbol][-100:]
                
            print(f"✅ Fetched {symbol}: ${current_price:.2f} ({change_percent:+.2f}%)")
            return stock_price
            
        except requests.RequestException as e:
            print(f"❌ Network error fetching {symbol}: {e}")
            return None
        except (KeyError, ValueError, TypeError) as e:
            print(f"❌ Data parsing error for {symbol}: {e}")
            return None
    
    def fetch_all_prices(self) -> Dict[str, StockPrice]:
        """
        Fetch current prices for all configured symbols
        
        Returns:
            Dictionary mapping symbol to StockPrice
        """
        prices = {}
        
        for symbol in self.symbols:
            price = self.fetch_current_price(symbol)
            if price:
                prices[symbol] = price
            # Add delay to respect API rate limits
            time.sleep(0.5)
            
        return prices
    
    def detect_price_movements(self, current_prices: Dict[str, StockPrice]) -> List[PriceMovement]:
        """
        Detect significant price movements based on threshold
        
        Args:
            current_prices: Dictionary of current stock prices
            
        Returns:
            List of detected price movements
        """
        movements = []
        
        for symbol, current_price in current_prices.items():
            if len(self.price_history[symbol]) < 2:
                continue  # Need at least 2 data points
                
            # Get previous price (5 minutes ago or closest available)
            history = self.price_history[symbol]
            cutoff_time = datetime.now() - timedelta(minutes=5)
            
            # Find the closest price before cutoff time
            previous_price_obj = None
            for price_obj in reversed(history[:-1]):  # Exclude current price
                if price_obj.timestamp <= cutoff_time:
                    previous_price_obj = price_obj
                    break
                    
            if not previous_price_obj:
                # If no price from 5 minutes ago, use the previous available price
                if len(history) >= 2:
                    previous_price_obj = history[-2]
                else:
                    continue
            
            # Calculate percentage change
            price_change = ((current_price.price - previous_price_obj.price) / previous_price_obj.price) * 100
            
            # Determine movement type
            if abs(price_change) >= self.threshold:
                movement_type = "significant_up" if price_change > 0 else "significant_down"
                
                movement = PriceMovement(
                    symbol=symbol,
                    current_price=current_price.price,
                    previous_price=previous_price_obj.price,
                    change_percent=price_change,
                    timestamp=current_price.timestamp,
                    movement_type=movement_type
                )
                
                movements.append(movement)
                print(f"🚨 Detected {movement_type} for {symbol}: {price_change:+.2f}% (${previous_price_obj.price:.2f} → ${current_price.price:.2f})")
        
        return movements
    
    def get_price_history(self, symbol: str, minutes: int = 60) -> List[StockPrice]:
        """
        Get price history for a symbol within the specified time window
        
        Args:
            symbol: Stock symbol
            minutes: Number of minutes to look back
            
        Returns:
            List of StockPrice objects within the time window
        """
        if symbol not in self.price_history:
            return []
            
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        
        return [
            price for price in self.price_history[symbol]
            if price.timestamp >= cutoff_time
        ]
    
    def get_latest_prices(self) -> Dict[str, StockPrice]:
        """
        Get the latest price for each symbol
        
        Returns:
            Dictionary mapping symbol to latest StockPrice
        """
        latest_prices = {}
        
        for symbol in self.symbols:
            if symbol in self.price_history and self.price_history[symbol]:
                latest_prices[symbol] = self.price_history[symbol][-1]
                
        return latest_prices

# Test function
def test_stock_service():
    """Test the stock service functionality"""
    print("🧪 Testing Stock Service...")
    
    service = StockService()
    
    # Test fetching a single price
    print("\n📊 Testing single price fetch:")
    price = service.fetch_current_price("AAPL")
    if price:
        print(f"✅ Successfully fetched AAPL price: ${price.price:.2f}")
    
    # Test fetching all prices
    print("\n📊 Testing multiple price fetch:")
    prices = service.fetch_all_prices()
    print(f"✅ Fetched prices for {len(prices)} symbols")
    
    # Simulate price movement detection
    print("\n🔍 Testing movement detection:")
    movements = service.detect_price_movements(prices)
    print(f"✅ Detected {len(movements)} movements")

if __name__ == "__main__":
    test_stock_service()
