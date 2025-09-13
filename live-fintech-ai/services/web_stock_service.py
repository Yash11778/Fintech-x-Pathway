"""
Web Scraping Stock Service for Live Fintech AI Assistant
Now uses the robust stock scraper with multiple reliable sources
"""

try:
    from .robust_stock_scraper import RobustStockScraper, StockPrice, PriceMovement
except ImportError:
    from robust_stock_scraper import RobustStockScraper, StockPrice, PriceMovement

from config import Config
from typing import Dict, List, Optional
from datetime import datetime

class WebScrapingStockService:
    """Web scraping implementation of stock service using robust scraper"""
    
    def __init__(self):
        print("🔧 Initializing Web Scraping Stock Service with robust scraper...")
        self.scraper = RobustStockScraper()
        self.symbols = Config.STOCK_SYMBOLS
        self.threshold = Config.PRICE_MOVEMENT_THRESHOLD_PERCENT
    
    def fetch_current_prices(self) -> Dict[str, StockPrice]:
        """Fetch current stock prices for all symbols"""
        print("📊 Fetching current stock prices...")
        return self.scraper.fetch_all_prices()
    
    def fetch_all_prices(self) -> Dict[str, StockPrice]:
        """Fetch all stock prices for all symbols (alias for compatibility)"""
        return self.fetch_current_prices()
    
    def fetch_current_price(self, symbol: str) -> Optional[StockPrice]:
        """Fetch current price for a single symbol"""
        return self.scraper.fetch_current_price(symbol)
    
    def detect_price_movements(self, current_prices: Dict[str, StockPrice]) -> List[PriceMovement]:
        """Detect significant price movements"""
        return self.scraper.detect_price_movements(current_prices)
    
    def get_price_history(self, symbol: str, minutes: int = 60) -> List[StockPrice]:
        """Get price history for a symbol"""
        return self.scraper.get_price_history(symbol, minutes)
    
    def get_latest_prices(self) -> Dict[str, StockPrice]:
        """Get latest cached prices"""
        return self.scraper.get_latest_prices()
    
    def run_once(self) -> List[PriceMovement]:
        """Run a single iteration of price checking"""
        try:
            # Fetch current prices
            current_prices = self.fetch_current_prices()
            
            if not current_prices:
                print("⚠️ No prices fetched, skipping movement detection")
                return []
            
            # Detect movements
            movements = self.detect_price_movements(current_prices)
            
            print(f"✅ Processed {len(current_prices)} prices, detected {len(movements)} movements")
            return movements
            
        except Exception as e:
            print(f"❌ Error in stock service: {e}")
            return []
    
    def start_monitoring(self):
        """Start continuous monitoring (for compatibility)"""
        print("🚀 Starting stock price monitoring...")
        print("💡 Note: This service is designed for single-run operations.")
        print("💡 Use run_once() method for individual price checks.")
        
        # Run once to demonstrate
        movements = self.run_once()
        return movements

# Test function
def test_web_scraping_stock_service():
    """Test the web scraping stock service"""
    print("🧪 Testing Web Scraping Stock Service...")
    
    service = WebScrapingStockService()
    
    # Test single price fetch
    print("\n1. Testing single price fetch for AAPL:")
    price = service.fetch_current_price('AAPL')
    if price:
        print(f"✅ AAPL: ${price.price:.2f}")
    else:
        print("❌ Failed to fetch AAPL price")
    
    # Test full service run
    print("\n2. Testing full service run:")
    movements = service.run_once()
    
    if movements:
        print(f"✅ Detected {len(movements)} price movements")
        for movement in movements[:3]:  # Show first 3
            print(f"   🚨 {movement.symbol}: {movement.change_percent:+.2f}%")
    else:
        print("📊 No significant movements detected")
    
    # Test price history
    print("\n3. Testing price history:")
    history = service.get_price_history('AAPL', minutes=30)
    print(f"📈 Found {len(history)} historical prices for AAPL")
    
    print("\n🎉 Test completed!")

if __name__ == "__main__":
    test_web_scraping_stock_service()
