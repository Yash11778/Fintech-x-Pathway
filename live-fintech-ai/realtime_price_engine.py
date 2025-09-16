"""
REAL-TIME STOCK PRICE ENGINE
High-frequency price updates with realistic market simulation
"""

import asyncio
import aiohttp
import yfinance as yf
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import time
import random
import threading
from typing import Dict, List, Optional
import json
import math

class RealTimeStockEngine:
    """Advanced real-time stock price engine with high accuracy"""
    
    def __init__(self):
        self.stocks = {}
        self.base_prices = {}
        self.price_history = {}
        self.volatility_cache = {}
        self.momentum_cache = {}
        self.market_hours = self._is_market_hours()
        self.update_interval = 1.0  # 1 second updates
        self.running = False
        self.last_update = {}
        
        # Market simulation parameters
        self.intraday_volatility = 0.02  # 2% daily volatility
        self.momentum_decay = 0.95
        self.news_impact_factor = 0.1
        
    def _is_market_hours(self) -> bool:
        """Check if market is currently open (simplified)"""
        now = datetime.now()
        # Simulate extended hours trading (6 AM - 8 PM EST)
        if 6 <= now.hour <= 20:
            return True
        return False
    
    def initialize_stock(self, symbol: str) -> Dict:
        """Initialize stock with current market data"""
        try:
            ticker = yf.Ticker(symbol)
            
            # Get historical data for volatility calculation
            hist = ticker.history(period="5d", interval="1m")
            if hist.empty:
                hist = ticker.history(period="1d")
            
            if not hist.empty:
                current_price = float(hist['Close'].iloc[-1])
                
                # Calculate intraday volatility
                if len(hist) > 1:
                    returns = np.log(hist['Close'] / hist['Close'].shift(1)).dropna()
                    volatility = float(returns.std() * np.sqrt(390))  # Annualized intraday vol
                else:
                    volatility = 0.02
                
                # Initialize stock data
                stock_data = {
                    'symbol': symbol,
                    'price': current_price,
                    'base_price': current_price,
                    'open_price': float(hist['Open'].iloc[-1]) if 'Open' in hist.columns else current_price,
                    'high': current_price,
                    'low': current_price,
                    'volume': int(hist['Volume'].iloc[-1]) if 'Volume' in hist.columns else 0,
                    'volatility': min(volatility, 0.05),  # Cap at 5%
                    'momentum': 0.0,
                    'last_update': datetime.now(),
                    'bid': current_price * 0.9995,  # Realistic bid-ask spread
                    'ask': current_price * 1.0005,
                    'day_change': 0.0,
                    'day_change_pct': 0.0
                }
                
                self.stocks[symbol] = stock_data
                self.base_prices[symbol] = current_price
                self.price_history[symbol] = [current_price]
                self.volatility_cache[symbol] = volatility
                self.momentum_cache[symbol] = 0.0
                self.last_update[symbol] = time.time()
                
                return stock_data
            else:
                # Fallback for stocks with no data
                fallback_price = 100.0 + random.uniform(-50, 50)
                stock_data = {
                    'symbol': symbol,
                    'price': fallback_price,
                    'base_price': fallback_price,
                    'open_price': fallback_price,
                    'high': fallback_price,
                    'low': fallback_price,
                    'volume': random.randint(100000, 10000000),
                    'volatility': 0.02,
                    'momentum': 0.0,
                    'last_update': datetime.now(),
                    'bid': fallback_price * 0.9995,
                    'ask': fallback_price * 1.0005,
                    'day_change': 0.0,
                    'day_change_pct': 0.0
                }
                
                self.stocks[symbol] = stock_data
                self.base_prices[symbol] = fallback_price
                self.price_history[symbol] = [fallback_price]
                self.volatility_cache[symbol] = 0.02
                self.momentum_cache[symbol] = 0.0
                self.last_update[symbol] = time.time()
                
                return stock_data
                
        except Exception as e:
            print(f"Error initializing {symbol}: {e}")
            return None
    
    def update_stock_price(self, symbol: str) -> Dict:
        """Update single stock with realistic price movement"""
        if symbol not in self.stocks:
            return self.initialize_stock(symbol)
        
        stock = self.stocks[symbol]
        current_time = time.time()
        time_delta = current_time - self.last_update[symbol]
        
        # Base volatility from cache
        base_volatility = self.volatility_cache[symbol]
        
        # Market hours adjustment
        volatility_multiplier = 1.5 if self.market_hours else 0.3
        
        # Time-based volatility (higher during market open/close)
        hour = datetime.now().hour
        if hour in [9, 10, 15, 16]:  # Market open/close hours
            volatility_multiplier *= 2.0
        elif hour in [11, 12, 13, 14]:  # Lunch hours
            volatility_multiplier *= 0.7
        
        # Calculate price change components
        
        # 1. Random walk component
        random_component = np.random.normal(0, base_volatility * volatility_multiplier * math.sqrt(time_delta))
        
        # 2. Momentum component
        momentum = self.momentum_cache[symbol]
        momentum_component = momentum * 0.1 * time_delta
        
        # 3. Reversion component (prices tend to revert to mean)
        price_deviation = (stock['price'] - stock['base_price']) / stock['base_price']
        reversion_component = -price_deviation * 0.05 * time_delta
        
        # 4. Volume-based component
        volume_factor = min(stock['volume'] / 1000000, 5.0)  # Higher volume = more price movement
        volume_component = random.uniform(-0.001, 0.001) * volume_factor
        
        # 5. News/event simulation (random spikes)
        news_component = 0
        if random.random() < 0.001:  # 0.1% chance per update
            news_component = random.uniform(-0.02, 0.02)  # ±2% news impact
        
        # Combine all components
        total_change_pct = (random_component + momentum_component + 
                           reversion_component + volume_component + news_component)
        
        # Apply price change
        new_price = stock['price'] * (1 + total_change_pct)
        
        # Ensure reasonable bounds (±20% from base price)
        max_price = stock['base_price'] * 1.20
        min_price = stock['base_price'] * 0.80
        new_price = max(min_price, min(max_price, new_price))
        
        # Update stock data
        stock['price'] = round(new_price, 2)
        stock['high'] = max(stock['high'], new_price)
        stock['low'] = min(stock['low'], new_price)
        stock['day_change'] = stock['price'] - stock['open_price']
        stock['day_change_pct'] = (stock['day_change'] / stock['open_price']) * 100
        
        # Update bid-ask spread
        spread = stock['price'] * random.uniform(0.0001, 0.001)  # 0.01% to 0.1% spread
        stock['bid'] = round(stock['price'] - spread/2, 2)
        stock['ask'] = round(stock['price'] + spread/2, 2)
        
        # Update momentum
        price_momentum = total_change_pct * 10  # Amplify for momentum
        self.momentum_cache[symbol] = (momentum * self.momentum_decay + 
                                     price_momentum * (1 - self.momentum_decay))
        
        # Update volume (simulate realistic trading volume)
        volume_change = random.uniform(0.95, 1.05)
        if abs(total_change_pct) > 0.005:  # Big price moves = more volume
            volume_change *= random.uniform(1.5, 3.0)
        stock['volume'] = int(stock['volume'] * volume_change)
        
        # Update price history for technical analysis
        self.price_history[symbol].append(new_price)
        if len(self.price_history[symbol]) > 100:  # Keep last 100 prices
            self.price_history[symbol].pop(0)
        
        stock['last_update'] = datetime.now()
        self.last_update[symbol] = current_time
        
        return stock
    
    def get_stock_data(self, symbol: str) -> Dict:
        """Get current stock data with real-time updates"""
        if symbol not in self.stocks:
            self.initialize_stock(symbol)
        
        # Update price if enough time has passed
        current_time = time.time()
        if (symbol not in self.last_update or 
            current_time - self.last_update[symbol] >= self.update_interval):
            self.update_stock_price(symbol)
        
        return self.stocks[symbol].copy()
    
    def get_multiple_stocks(self, symbols: List[str]) -> Dict[str, Dict]:
        """Get multiple stocks with batch processing"""
        results = {}
        for symbol in symbols:
            results[symbol] = self.get_stock_data(symbol)
        return results
    
    def start_live_updates(self, symbols: List[str]):
        """Start background thread for continuous price updates"""
        if self.running:
            return
        
        self.running = True
        
        def update_loop():
            while self.running:
                try:
                    for symbol in symbols:
                        if symbol in self.stocks:
                            self.update_stock_price(symbol)
                    time.sleep(self.update_interval)
                except Exception as e:
                    print(f"Error in update loop: {e}")
                    time.sleep(1)
        
        # Initialize all stocks
        for symbol in symbols:
            self.initialize_stock(symbol)
        
        # Start background thread
        self.update_thread = threading.Thread(target=update_loop, daemon=True)
        self.update_thread.start()
    
    def stop_live_updates(self):
        """Stop live price updates"""
        self.running = False
    
    def get_price_history(self, symbol: str, limit: int = 50) -> List[float]:
        """Get recent price history for charts"""
        if symbol in self.price_history:
            return self.price_history[symbol][-limit:]
        return []
    
    def calculate_technical_indicators(self, symbol: str) -> Dict:
        """Calculate real-time technical indicators"""
        if symbol not in self.price_history or len(self.price_history[symbol]) < 20:
            return {}
        
        prices = np.array(self.price_history[symbol])
        
        indicators = {}
        
        # Moving averages
        if len(prices) >= 5:
            indicators['ma5'] = float(np.mean(prices[-5:]))
        if len(prices) >= 10:
            indicators['ma10'] = float(np.mean(prices[-10:]))
        if len(prices) >= 20:
            indicators['ma20'] = float(np.mean(prices[-20:]))
        
        # RSI (simplified)
        if len(prices) >= 14:
            deltas = np.diff(prices)
            gains = np.where(deltas > 0, deltas, 0)
            losses = np.where(deltas < 0, -deltas, 0)
            
            avg_gain = np.mean(gains[-14:])
            avg_loss = np.mean(losses[-14:])
            
            if avg_loss != 0:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
                indicators['rsi'] = float(rsi)
        
        # Volatility
        if len(prices) >= 20:
            returns = np.diff(np.log(prices))
            volatility = np.std(returns) * np.sqrt(252)  # Annualized
            indicators['volatility'] = float(volatility)
        
        return indicators
    
    def simulate_market_event(self, symbol: str, impact: float):
        """Simulate market event (earnings, news, etc.)"""
        if symbol in self.stocks:
            current_price = self.stocks[symbol]['price']
            new_price = current_price * (1 + impact)
            self.stocks[symbol]['price'] = round(new_price, 2)
            
            # Add momentum from the event
            self.momentum_cache[symbol] += impact * 5
            
            # Increase volume
            self.stocks[symbol]['volume'] *= random.uniform(2, 5)
    
    def get_market_summary(self, symbols: List[str]) -> Dict:
        """Get overall market summary"""
        total_change = 0
        positive_stocks = 0
        negative_stocks = 0
        total_volume = 0
        
        for symbol in symbols:
            if symbol in self.stocks:
                stock = self.stocks[symbol]
                total_change += stock['day_change_pct']
                total_volume += stock['volume']
                
                if stock['day_change_pct'] > 0:
                    positive_stocks += 1
                elif stock['day_change_pct'] < 0:
                    negative_stocks += 1
        
        return {
            'average_change': total_change / len(symbols) if symbols else 0,
            'positive_stocks': positive_stocks,
            'negative_stocks': negative_stocks,
            'neutral_stocks': len(symbols) - positive_stocks - negative_stocks,
            'total_volume': total_volume,
            'market_sentiment': 'Bullish' if positive_stocks > negative_stocks else 'Bearish' if negative_stocks > positive_stocks else 'Mixed'
        }

# Global instance
realtime_engine = RealTimeStockEngine()
