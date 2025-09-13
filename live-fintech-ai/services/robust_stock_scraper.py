"""
Robust Web Scraping Stock Service for Live Fintech AI Assistant
Scrapes from multiple reliable sources: Yahoo Finance, Google Finance, MarketWatch
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

class RobustStockScraper:
    """Robust stock scraper with multiple fallback sources"""
    
    def __init__(self):
        self.symbols = Config.STOCK_SYMBOLS
        self.threshold = Config.PRICE_MOVEMENT_THRESHOLD_PERCENT
        self.price_history: Dict[str, List[StockPrice]] = {symbol: [] for symbol in self.symbols}
        
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
    
    def scrape_yahoo_finance(self, symbol: str) -> Optional[StockPrice]:
        """
        Scrape stock price from Yahoo Finance
        Most reliable source with good data structure
        """
        try:
            url = f"https://finance.yahoo.com/quote/{symbol}"
            
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            # Try to find JSON data in the page (most reliable method)
            json_patterns = [
                r'root\.App\.main = (\{.*?\});',
                r'"QuoteSummaryStore":\{.*?"financialData":\{.*?"currentPrice":\{"raw":([0-9.]+)',
                rf'"symbol":"{symbol}".*?"regularMarketPrice":\{{"raw":([0-9.]+)',
            ]
            
            for pattern in json_patterns:
                json_match = re.search(pattern, response.text)
                if json_match:
                    try:
                        if 'root.App.main' in pattern:
                            data = json.loads(json_match.group(1))
                            quote_summary = data.get('context', {}).get('dispatcher', {}).get('stores', {}).get('QuoteSummaryStore', {})
                            price_data = quote_summary.get('financialData', {})
                            
                            if price_data:
                                current_price = price_data.get('currentPrice', {}).get('raw')
                                if current_price and 0.01 <= float(current_price) <= 100000:
                                    return StockPrice(
                                        symbol=symbol,
                                        price=float(current_price),
                                        timestamp=datetime.now(),
                                        change_percent=None
                                    )
                        else:
                            # Direct price extraction from JSON pattern
                            price_val = float(json_match.group(1))
                            if 0.01 <= price_val <= 100000:
                                return StockPrice(
                                    symbol=symbol,
                                    price=price_val,
                                    timestamp=datetime.now(),
                                    change_percent=None
                                )
                    except:
                        continue
            
            # Fallback to HTML parsing
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Multiple selectors for price - Yahoo Finance specific, prioritize symbol-specific
            price_selectors = [
                # Try symbol-specific selectors first
                f'fin-streamer[data-symbol="{symbol}"][data-field="regularMarketPrice"]',
                f'[data-testid="qsp-price"][data-symbol="{symbol}"]',
                f'[data-symbol="{symbol}"] fin-streamer[data-field="regularMarketPrice"]',
                # Then try the main quote price (most reliable for individual stock pages)
                '[data-testid="qsp-price"]',
                # Fallback selectors
                '.Trsdu\\(0\\.3s\\).Fw\\(b\\).Fz\\(36px\\).Mb\\(-4px\\).D\\(ib\\)',
            ]
            
            current_price = None
            for selector in price_selectors:
                try:
                    price_element = soup.select_one(selector)
                    if price_element:
                        price_text = price_element.get_text(strip=True)
                        # More careful price extraction with better validation
                        price_match = re.search(r'(\d{1,4}(?:,\d{3})*(?:\.\d{2})?)', price_text)
                        if price_match:
                            price_str = price_match.group(1).replace(',', '')
                            try:
                                price_val = float(price_str)
                                # More realistic price range check for major stocks
                                if 1.0 <= price_val <= 10000:  # $1 to $10k range for most stocks
                                    print(f"    Found price via selector {selector}: ${price_val:.2f}")
                                    current_price = price_val
                                    break
                                else:
                                    print(f"    Rejected unrealistic price: ${price_val:.2f} from selector {selector}")
                            except ValueError:
                                continue
                except:
                    continue
            
            if not current_price:
                # Last resort: regex search in page content for symbol-specific data
                price_patterns = [
                    rf'"regularMarketPrice".*?"raw":([0-9.]+).*?"{symbol}"',
                    rf'"{symbol}".*?"regularMarketPrice".*?"raw":([0-9.]+)',
                    r'"regularMarketPrice":\{"raw":([0-9.]+)',
                    r'"price":\{"raw":([0-9.]+)',
                    rf'data-symbol="{symbol}"[^>]*data-field="regularMarketPrice"[^>]*>([0-9.,]+)',
                ]
                
                for pattern in price_patterns:
                    matches = re.search(pattern, response.text, re.IGNORECASE)
                    if matches:
                        try:
                            price_str = matches.group(1).replace(',', '')
                            price_val = float(price_str)
                            if 0.01 <= price_val <= 100000:  # Reasonable range
                                current_price = price_val
                                break
                        except:
                            continue
            
            if current_price:
                # Try to get change percentage - symbol specific
                change_percent = None
                change_selectors = [
                    f'fin-streamer[data-symbol="{symbol}"][data-field="regularMarketChangePercent"]',
                    f'[data-testid="qsp-price-change-percent"][data-symbol="{symbol}"]',
                    'fin-streamer[data-field="regularMarketChangePercent"]',
                    '[data-testid="qsp-price-change-percent"]'
                ]
                
                for selector in change_selectors:
                    try:
                        change_element = soup.select_one(selector)
                        if change_element:
                            change_text = change_element.get_text(strip=True)
                            change_match = re.search(r'([+-]?[0-9.]+)%', change_text)
                            if change_match:
                                change_val = float(change_match.group(1))
                                # Reasonable change range (-50% to +50%)
                                if -50 <= change_val <= 50:
                                    change_percent = change_val
                                    break
                    except:
                        continue
                
                return StockPrice(
                    symbol=symbol,
                    price=current_price,
                    timestamp=datetime.now(),
                    change_percent=change_percent
                )
            
            return None
            
        except Exception as e:
            print(f"❌ Yahoo Finance error for {symbol}: {e}")
            return None
    
    def scrape_google_finance(self, symbol: str) -> Optional[StockPrice]:
        """
        Scrape stock price from Google Finance
        Reliable backup source
        """
        try:
            # Try different Google Finance URLs
            urls = [
                f"https://www.google.com/finance/quote/{symbol}:NASDAQ",
                f"https://www.google.com/finance/quote/{symbol}:NYSE",
                f"https://www.google.com/finance/quote/{symbol}"
            ]
            
            for url in urls:
                try:
                    response = self.session.get(url, timeout=10)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Google Finance price selectors
                    price_selectors = [
                        '.YMlKec.fxKbKc',  # Main price element
                        '[data-last-price]',
                        '.kf1m0',
                        'div[jsname="ip75Cb"]'
                    ]
                    
                    for selector in price_selectors:
                        try:
                            price_element = soup.select_one(selector)
                            if price_element:
                                price_text = price_element.get_text(strip=True)
                                # Clean price text
                                price_text = re.sub(r'[^\d.]', '', price_text)
                                if price_text and '.' in price_text:
                                    current_price = float(price_text)
                                    
                                    # Try to get change percentage
                                    change_percent = None
                                    change_selectors = ['.P6K39c', '.JwB6zf']
                                    
                                    for change_selector in change_selectors:
                                        try:
                                            change_element = soup.select_one(change_selector)
                                            if change_element:
                                                change_text = change_element.get_text(strip=True)
                                                change_match = re.search(r'([+-]?[0-9.]+)%', change_text)
                                                if change_match:
                                                    change_percent = float(change_match.group(1))
                                                    break
                                        except:
                                            continue
                                    
                                    return StockPrice(
                                        symbol=symbol,
                                        price=current_price,
                                        timestamp=datetime.now(),
                                        change_percent=change_percent
                                    )
                        except:
                            continue
                    
                    # If regular selectors fail, try to find price in script tags
                    scripts = soup.find_all('script')
                    for script in scripts:
                        if script.string:
                            price_match = re.search(r'"(\d+\.\d+)"', script.string)
                            if price_match:
                                try:
                                    price = float(price_match.group(1))
                                    if 0.01 < price < 10000:  # Reasonable price range
                                        return StockPrice(
                                            symbol=symbol,
                                            price=price,
                                            timestamp=datetime.now()
                                        )
                                except:
                                    continue
                    
                except Exception as e:
                    continue
            
            return None
            
        except Exception as e:
            print(f"❌ Google Finance error for {symbol}: {e}")
            return None
    
    def scrape_marketwatch(self, symbol: str) -> Optional[StockPrice]:
        """
        Scrape stock price from MarketWatch
        Another reliable backup source
        """
        try:
            url = f"https://www.marketwatch.com/investing/stock/{symbol.lower()}"
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # MarketWatch price selectors
            price_selectors = [
                '.intraday__price .value',
                'bg-quote .value',
                '.price .value',
                'h2.intraday__price',
                '.price-value'
            ]
            
            for selector in price_selectors:
                try:
                    price_element = soup.select_one(selector)
                    if price_element:
                        price_text = price_element.get_text(strip=True)
                        # Extract numeric value
                        price_match = re.search(r'([0-9,]+\.?[0-9]*)', price_text)
                        if price_match:
                            price_str = price_match.group(1).replace(',', '')
                            current_price = float(price_str)
                            
                            # Try to get change percentage
                            change_percent = None
                            change_selectors = [
                                '.intraday__change .value',
                                '.change--percent',
                                'bg-quote .change'
                            ]
                            
                            for change_selector in change_selectors:
                                try:
                                    change_element = soup.select_one(change_selector)
                                    if change_element:
                                        change_text = change_element.get_text(strip=True)
                                        change_match = re.search(r'([+-]?[0-9.]+)%', change_text)
                                        if change_match:
                                            change_percent = float(change_match.group(1))
                                            break
                                except:
                                    continue
                            
                            return StockPrice(
                                symbol=symbol,
                                price=current_price,
                                timestamp=datetime.now(),
                                change_percent=change_percent
                            )
                except:
                    continue
            
            return None
            
        except Exception as e:
            print(f"❌ MarketWatch error for {symbol}: {e}")
            return None
    
    def scrape_investing_com(self, symbol: str) -> Optional[StockPrice]:
        """
        Scrape stock price from Investing.com
        Additional backup source
        """
        try:
            # Investing.com often requires specific stock IDs, so we'll try a search approach
            search_url = f"https://www.investing.com/search/?q={symbol}"
            
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for stock links in search results
            stock_links = soup.find_all('a', href=re.compile(r'/equities/'))
            
            for link in stock_links[:3]:  # Try first 3 results
                try:
                    stock_url = "https://www.investing.com" + link['href']
                    
                    stock_response = self.session.get(stock_url, timeout=10)
                    stock_response.raise_for_status()
                    
                    stock_soup = BeautifulSoup(stock_response.content, 'html.parser')
                    
                    # Investing.com price selectors
                    price_selectors = [
                        '[data-test="instrument-price-last"]',
                        '.text-2xl',
                        '.instrument-price_last__JQN7O'
                    ]
                    
                    for selector in price_selectors:
                        try:
                            price_element = stock_soup.select_one(selector)
                            if price_element:
                                price_text = price_element.get_text(strip=True)
                                price_match = re.search(r'([0-9,]+\.?[0-9]*)', price_text)
                                if price_match:
                                    price_str = price_match.group(1).replace(',', '')
                                    current_price = float(price_str)
                                    
                                    return StockPrice(
                                        symbol=symbol,
                                        price=current_price,
                                        timestamp=datetime.now()
                                    )
                        except:
                            continue
                    
                except:
                    continue
            
            return None
            
        except Exception as e:
            print(f"❌ Investing.com error for {symbol}: {e}")
            return None
    
    def fetch_current_price(self, symbol: str) -> Optional[StockPrice]:
        """
        Fetch current stock price with multiple fallback sources
        """
        print(f"🔍 Fetching price for {symbol}...")
        
        # Rotate user agent for each request
        self._rotate_user_agent()
        
        # Try sources in order of reliability
        sources = [
            ("Yahoo Finance", self.scrape_yahoo_finance),
            ("Google Finance", self.scrape_google_finance),
            ("MarketWatch", self.scrape_marketwatch),
            ("Investing.com", self.scrape_investing_com)
        ]
        
        for source_name, scrape_func in sources:
            try:
                print(f"  Trying {source_name}...")
                price = scrape_func(symbol)
                
                if price and price.price > 0:
                    # Store in price history
                    self.price_history[symbol].append(price)
                    
                    # Keep only last 100 entries per symbol
                    if len(self.price_history[symbol]) > 100:
                        self.price_history[symbol] = self.price_history[symbol][-100:]
                    
                    change_str = f" ({price.change_percent:+.2f}%)" if price.change_percent else ""
                    print(f"✅ {symbol}: ${price.price:.2f}{change_str} (via {source_name})")
                    return price
                
                # Small delay between source attempts
                time.sleep(1)
                
            except Exception as e:
                print(f"  ❌ {source_name} failed: {e}")
                continue
        
        print(f"❌ All sources failed for {symbol}")
        return None
    
    def fetch_all_prices(self) -> Dict[str, StockPrice]:
        """
        Fetch current prices for all configured symbols
        """
        prices = {}
        
        print(f"📊 Fetching prices for {len(self.symbols)} symbols...")
        
        for i, symbol in enumerate(self.symbols, 1):
            print(f"\n[{i}/{len(self.symbols)}] Processing {symbol}...")
            
            price = self.fetch_current_price(symbol)
            if price:
                prices[symbol] = price
            
            # Add delay between symbols to be respectful
            if i < len(self.symbols):  # Don't sleep after last symbol
                time.sleep(2)
        
        print(f"\n✅ Successfully fetched {len(prices)} out of {len(self.symbols)} stock prices")
        return prices
    
    def detect_price_movements(self, current_prices: Dict[str, StockPrice]) -> List[PriceMovement]:
        """
        Detect significant price movements based on threshold
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
        """Get price history for a symbol within the specified time window"""
        if symbol not in self.price_history:
            return []
            
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        
        return [
            price for price in self.price_history[symbol]
            if price.timestamp >= cutoff_time
        ]
    
    def get_latest_prices(self) -> Dict[str, StockPrice]:
        """Get the latest price for each symbol"""
        latest_prices = {}
        
        for symbol in self.symbols:
            if symbol in self.price_history and self.price_history[symbol]:
                latest_prices[symbol] = self.price_history[symbol][-1]
                
        return latest_prices

# Alias for backwards compatibility
WebScrapingStockService = RobustStockScraper

# Test function
def test_robust_stock_scraper():
    """Test the robust stock scraper functionality"""
    print("🧪 Testing Robust Stock Scraper...")
    
    scraper = RobustStockScraper()
    
    # Test with a few symbols
    test_symbols = ['AAPL', 'MSFT', 'GOOGL']
    
    for symbol in test_symbols:
        print(f"\n📊 Testing {symbol}:")
        price = scraper.fetch_current_price(symbol)
        
        if price:
            change_str = f" ({price.change_percent:+.2f}%)" if price.change_percent else ""
            print(f"✅ {symbol}: ${price.price:.2f}{change_str}")
        else:
            print(f"❌ Failed to fetch {symbol}")
    
    print("\n🎉 Test completed!")

if __name__ == "__main__":
    test_robust_stock_scraper()
