#!/usr/bin/env python3
"""
Quick test to see what Yahoo Finance is returning for AAPL
"""

import requests
from bs4 import BeautifulSoup
import re

def test_yahoo_aapl():
    url = "https://finance.yahoo.com/quote/AAPL"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print("🔍 Testing AAPL price extraction...")
        
        # Find all price-related elements
        price_elements = soup.find_all('fin-streamer', {'data-field': 'regularMarketPrice'})
        print(f"\nFound {len(price_elements)} price elements:")
        
        for i, elem in enumerate(price_elements[:3]):
            symbol = elem.get('data-symbol', 'Unknown')
            price_text = elem.get_text(strip=True)
            print(f"  {i+1}: '{price_text}' (symbol: {symbol})")
        
        # Also try data-testid approach
        qsp_elements = soup.find_all(attrs={'data-testid': 'qsp-price'})
        print(f"\nFound {len(qsp_elements)} qsp-price elements:")
        
        for i, elem in enumerate(qsp_elements[:3]):
            price_text = elem.get_text(strip=True)
            print(f"  {i+1}: '{price_text}'")
        
        # Try JSON extraction
        json_match = re.search(r'"regularMarketPrice":\{"raw":([0-9.]+)', response.text)
        if json_match:
            json_price = json_match.group(1)
            print(f"\nJSON price found: ${json_price}")
        else:
            print("\nNo JSON price found")
        
        # Look for the specific symbol-based element
        aapl_element = soup.find('fin-streamer', {'data-symbol': 'AAPL', 'data-field': 'regularMarketPrice'})
        if aapl_element:
            aapl_price = aapl_element.get_text(strip=True)
            print(f"\nAAPL-specific element: '{aapl_price}'")
        else:
            print("\nNo AAPL-specific element found")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_yahoo_aapl()
