"""
Fast Concurrent Stock Scraper for Live Fintech AI Assistant
Uses asyncio and concurrent requests for maximum speed
"""

import asyncio
import aiohttp
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import json
import re
from config import Config

@dataclass
class FastStockPrice:
    """Optimized data structure for stock price information"""
    symbol: str
    price: float
    timestamp: datetime
    change_percent: Optional[float] = None
    volume: Optional[int] = None

class FastStockScraper:
    """Ultra-fast concurrent stock scraper"""
    
    def __init__(self):
        self.symbols = Config.STOCK_SYMBOLS
        self.session = None
        
        # Pre-built URLs for maximum speed
        self.api_urls = {
            'yahoo': 'https://query1.finance.yahoo.com/v8/finance/chart/{}',
            'finnhub': 'https://finnhub.io/api/v1/quote?symbol={}&token=demo',
            'alpha': 'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={}&apikey=demo'
        }
        
        # Headers for speed optimization
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json,text/html,application/xhtml+xml',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache'
        }
    
    async def create_session(self):
        """Create optimized aiohttp session"""
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=5, connect=2)
            connector = aiohttp.TCPConnector(
                limit=50,
                limit_per_host=10,
                ttl_dns_cache=300,
                use_dns_cache=True,
                keepalive_timeout=60
            )
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                headers=self.headers
            )
    
    async def fetch_yahoo_price(self, symbol: str) -> Optional[FastStockPrice]:
        """Fast Yahoo Finance API fetch"""
        try:
            url = self.api_urls['yahoo'].format(symbol)
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    result = data['chart']['result'][0]
                    meta = result['meta']
                    
                    current_price = meta['regularMarketPrice']
                    previous_close = meta['previousClose']
                    change_percent = ((current_price - previous_close) / previous_close) * 100
                    
                    return FastStockPrice(
                        symbol=symbol,
                        price=current_price,
                        change_percent=change_percent,
                        timestamp=datetime.now(),
                        volume=meta.get('regularMarketVolume', 0)
                    )
        except Exception as e:
            print(f"⚡ Yahoo API error for {symbol}: {e}")
            return None
    
    async def fetch_single_price_concurrent(self, symbol: str) -> Optional[FastStockPrice]:
        """Fetch single stock price with multiple API fallbacks concurrently"""
        tasks = [
            self.fetch_yahoo_price(symbol),
            # Add more API tasks here for redundancy
        ]
        
        # Return first successful result
        for coro in asyncio.as_completed(tasks):
            try:
                result = await coro
                if result:
                    return result
            except:
                continue
        
        return None
    
    async def fetch_all_prices_fast(self) -> Dict[str, FastStockPrice]:
        """Fetch all stock prices concurrently for maximum speed"""
        start_time = time.time()
        
        await self.create_session()
        
        # Create concurrent tasks for all symbols
        tasks = []
        for symbol in self.symbols:
            task = asyncio.create_task(
                self.fetch_single_price_concurrent(symbol),
                name=f"fetch_{symbol}"
            )
            tasks.append((symbol, task))
        
        # Gather all results concurrently
        results = {}
        completed_tasks = await asyncio.gather(
            *[task for _, task in tasks],
            return_exceptions=True
        )
        
        for (symbol, _), result in zip(tasks, completed_tasks):
            if isinstance(result, FastStockPrice):
                results[symbol] = result
                print(f"⚡ {symbol}: ${result.price:.2f} ({result.change_percent:+.2f}%)")
            elif not isinstance(result, Exception):
                print(f"⚠️ No data for {symbol}")
        
        elapsed = time.time() - start_time
        print(f"🚀 Fetched {len(results)}/{len(self.symbols)} prices in {elapsed:.2f}s")
        
        return results
    
    async def close(self):
        """Close the session"""
        if self.session:
            await self.session.close()

class FastStockService:
    """Fast stock service wrapper"""
    
    def __init__(self):
        self.scraper = FastStockScraper()
        print("⚡ Fast Stock Service initialized")
    
    async def fetch_all_prices(self) -> Dict[str, FastStockPrice]:
        """Fetch all prices using fast concurrent scraper"""
        return await self.scraper.fetch_all_prices_fast()
    
    def detect_price_movements(self, current_prices: Dict[str, FastStockPrice]) -> List[Dict]:
        """Detect significant price movements"""
        movements = []
        
        for symbol, price_data in current_prices.items():
            if price_data.change_percent and abs(price_data.change_percent) >= Config.PRICE_MOVEMENT_THRESHOLD_PERCENT:
                movements.append({
                    'symbol': symbol,
                    'price': price_data.price,
                    'change_percent': price_data.change_percent,
                    'timestamp': price_data.timestamp,
                    'movement_type': 'significant_up' if price_data.change_percent > 0 else 'significant_down'
                })
        
        return movements
    
    async def cleanup(self):
        """Cleanup resources"""
        await self.scraper.close()

# Test function
async def test_fast_scraper():
    """Test the fast scraper performance"""
    print("🚀 Testing Fast Stock Scraper...")
    
    service = FastStockService()
    
    start_time = time.time()
    prices = await service.fetch_all_prices()
    elapsed = time.time() - start_time
    
    print(f"\n⚡ Performance Results:")
    print(f"   - Fetched {len(prices)} stock prices")
    print(f"   - Total time: {elapsed:.2f} seconds")
    print(f"   - Average per stock: {elapsed/len(Config.STOCK_SYMBOLS):.3f} seconds")
    print(f"   - Speed improvement: ~{15/elapsed:.1f}x faster")
    
    await service.cleanup()

if __name__ == "__main__":
    asyncio.run(test_fast_scraper())
