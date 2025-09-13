#!/usr/bin/env python3
"""
Quick test script for web scraping functionality
"""
import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Set web scraping mode
os.environ['DATA_SOURCE_MODE'] = 'webscraping'

try:
    from services.web_stock_service import WebScrapingStockService
except ImportError as e:
    print(f"Import error: {e}")
    print(f"Current directory: {current_dir}")
    print(f"Python path: {sys.path}")
    
    # Try importing requests directly
    try:
        import requests
        print("✅ requests module is available")
    except ImportError:
        print("❌ requests module not found")
    
    # Try importing BeautifulSoup
    try:
        from bs4 import BeautifulSoup
        print("✅ BeautifulSoup is available")
    except ImportError:
        print("❌ BeautifulSoup not found")
    
    exit(1)

def test_scraping():
    print("🧪 Testing Web Scraping Stock Service...")
    
    service = WebScrapingStockService()
    
    print("\n📊 Testing AAPL price scraping:")
    price = service.fetch_current_price("AAPL")
    
    if price:
        print(f"✅ Successfully scraped AAPL: ${price.price:.2f}")
        if price.change_percent:
            print(f"   Change: {price.change_percent:+.2f}%")
        print(f"   Timestamp: {price.timestamp}")
    else:
        print("❌ Failed to scrape AAPL price")
    
    print("\n📊 Testing multiple symbols:")
    prices = service.fetch_all_prices()
    
    for symbol, price in prices.items():
        change_str = f" ({price.change_percent:+.2f}%)" if price.change_percent else ""
        print(f"   {symbol}: ${price.price:.2f}{change_str}")
    
    print(f"\n✅ Test completed! Scraped {len(prices)} symbols successfully.")

if __name__ == "__main__":
    test_scraping()
