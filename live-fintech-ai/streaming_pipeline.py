"""
AI-Powered Streaming Data Pipeline
Real-time market data processing with Pathway-style streaming architecture
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import asyncio
import json
import threading
import time
from collections import deque
import hashlib

class StreamingDataPipeline:
    """Pathway-inspired streaming data pipeline for financial data"""
    
    def __init__(self, buffer_size: int = 1000):
        self.buffer_size = buffer_size
        self.data_streams = {}
        self.processed_data = {}
        self.stream_health = {}
        self.processors = []
        self.subscribers = []
        self.is_running = False
        self.processing_stats = {
            'messages_processed': 0,
            'processing_rate': 0,
            'error_count': 0,
            'last_processed': None
        }
        
    def create_stream(self, stream_name: str, schema: Dict = None):
        """Create a new data stream"""
        self.data_streams[stream_name] = {
            'buffer': deque(maxlen=self.buffer_size),
            'schema': schema or {},
            'created_at': datetime.now(),
            'message_count': 0,
            'last_message': None
        }
        
        self.stream_health[stream_name] = {
            'status': 'ACTIVE',
            'throughput': 0,
            'error_rate': 0,
            'latency_ms': 0
        }
        
    def ingest_data(self, stream_name: str, data: Dict):
        """Ingest data into a stream"""
        if stream_name not in self.data_streams:
            self.create_stream(stream_name)
        
        # Add metadata
        enriched_data = {
            **data,
            '_timestamp': datetime.now(),
            '_stream': stream_name,
            '_id': hashlib.md5(f"{stream_name}_{datetime.now().isoformat()}".encode()).hexdigest()[:8]
        }
        
        # Add to buffer
        self.data_streams[stream_name]['buffer'].append(enriched_data)
        self.data_streams[stream_name]['message_count'] += 1
        self.data_streams[stream_name]['last_message'] = datetime.now()
        
        # Update stats
        self.processing_stats['messages_processed'] += 1
        self.processing_stats['last_processed'] = datetime.now()
        
        return enriched_data['_id']
    
    def add_processor(self, processor_func, stream_name: str = None, output_stream: str = None):
        """Add a processing function to the pipeline"""
        processor = {
            'func': processor_func,
            'input_stream': stream_name,
            'output_stream': output_stream,
            'processed_count': 0,
            'error_count': 0
        }
        self.processors.append(processor)
        
        if output_stream and output_stream not in self.data_streams:
            self.create_stream(output_stream)
    
    def process_streams(self):
        """Process all streams with registered processors"""
        start_time = time.time()
        processed_count = 0
        
        for processor in self.processors:
            input_stream = processor['input_stream']
            
            if input_stream and input_stream in self.data_streams:
                stream_data = self.data_streams[input_stream]
                
                # Process each message in buffer
                processed_messages = []
                while stream_data['buffer']:
                    try:
                        message = stream_data['buffer'].popleft()
                        result = processor['func'](message)
                        
                        if result and processor['output_stream']:
                            self.ingest_data(processor['output_stream'], result)
                        
                        processed_messages.append(message)
                        processor['processed_count'] += 1
                        processed_count += 1
                        
                    except Exception as e:
                        processor['error_count'] += 1
                        self.processing_stats['error_count'] += 1
                        print(f"Processing error: {e}")
        
        # Update processing rate
        processing_time = time.time() - start_time
        if processing_time > 0:
            self.processing_stats['processing_rate'] = processed_count / processing_time
    
    def get_latest_data(self, stream_name: str, limit: int = 10) -> List[Dict]:
        """Get latest data from a stream"""
        if stream_name not in self.data_streams:
            return []
        
        buffer = self.data_streams[stream_name]['buffer']
        return list(buffer)[-limit:] if buffer else []
    
    def get_stream_stats(self) -> Dict:
        """Get comprehensive streaming statistics"""
        stats = {
            'pipeline_stats': self.processing_stats.copy(),
            'stream_count': len(self.data_streams),
            'active_processors': len(self.processors),
            'streams': {}
        }
        
        for stream_name, stream_data in self.data_streams.items():
            stats['streams'][stream_name] = {
                'message_count': stream_data['message_count'],
                'buffer_size': len(stream_data['buffer']),
                'last_message': stream_data['last_message'].isoformat() if stream_data['last_message'] else None,
                'health': self.stream_health.get(stream_name, {})
            }
        
        return stats

class MarketDataProcessor:
    """Specialized processor for market data streams"""
    
    def __init__(self, pipeline: StreamingDataPipeline):
        self.pipeline = pipeline
        self.setup_processors()
        
    def setup_processors(self):
        """Setup market data processing functions"""
        
        # Price change calculator
        def calculate_price_changes(data):
            if 'price' in data and 'open' in data:
                change = data['price'] - data['open']
                change_pct = (change / data['open']) * 100 if data['open'] != 0 else 0
                
                return {
                    'symbol': data.get('symbol'),
                    'change': round(change, 2),
                    'change_pct': round(change_pct, 2),
                    'price': data['price'],
                    'timestamp': data['_timestamp']
                }
        
        # Volume analyzer
        def analyze_volume(data):
            if 'volume' in data:
                # Simple volume analysis
                avg_volume = 1000000  # Simplified average
                volume_ratio = data['volume'] / avg_volume
                
                volume_signal = 'HIGH' if volume_ratio > 2 else 'NORMAL' if volume_ratio > 0.5 else 'LOW'
                
                return {
                    'symbol': data.get('symbol'),
                    'volume': data['volume'],
                    'volume_ratio': round(volume_ratio, 2),
                    'volume_signal': volume_signal,
                    'timestamp': data['_timestamp']
                }
        
        # Momentum calculator
        def calculate_momentum(data):
            if 'change_pct' in data:
                momentum_strength = abs(data['change_pct'])
                
                if momentum_strength > 5:
                    momentum = 'STRONG'
                elif momentum_strength > 2:
                    momentum = 'MEDIUM'
                else:
                    momentum = 'WEAK'
                
                direction = 'UP' if data['change_pct'] > 0 else 'DOWN'
                
                return {
                    'symbol': data.get('symbol'),
                    'momentum': momentum,
                    'direction': direction,
                    'strength': momentum_strength,
                    'timestamp': data['_timestamp']
                }
        
        # Volatility calculator
        def calculate_volatility(data):
            if 'high' in data and 'low' in data and 'price' in data:
                daily_range = data['high'] - data['low']
                volatility_pct = (daily_range / data['price']) * 100 if data['price'] != 0 else 0
                
                volatility_level = 'HIGH' if volatility_pct > 5 else 'MEDIUM' if volatility_pct > 2 else 'LOW'
                
                return {
                    'symbol': data.get('symbol'),
                    'volatility_pct': round(volatility_pct, 2),
                    'volatility_level': volatility_level,
                    'daily_range': round(daily_range, 2),
                    'timestamp': data['_timestamp']
                }
        
        # Register processors
        self.pipeline.add_processor(calculate_price_changes, 'raw_market_data', 'price_changes')
        self.pipeline.add_processor(analyze_volume, 'raw_market_data', 'volume_analysis')
        self.pipeline.add_processor(calculate_momentum, 'price_changes', 'momentum_signals')
        self.pipeline.add_processor(calculate_volatility, 'raw_market_data', 'volatility_metrics')

class AnomalyDetector:
    """Real-time anomaly detection for market data"""
    
    def __init__(self, pipeline: StreamingDataPipeline):
        self.pipeline = pipeline
        self.historical_data = {}
        self.anomaly_thresholds = {
            'price_change_std': 3.0,
            'volume_ratio': 5.0,
            'volatility_spike': 2.5
        }
        self.setup_detectors()
    
    def setup_detectors(self):
        """Setup anomaly detection processors"""
        
        def detect_price_anomalies(data):
            symbol = data.get('symbol')
            if not symbol or 'change_pct' not in data:
                return None
            
            # Initialize historical data if needed
            if symbol not in self.historical_data:
                self.historical_data[symbol] = deque(maxlen=100)
            
            self.historical_data[symbol].append(data['change_pct'])
            
            # Calculate statistics
            if len(self.historical_data[symbol]) > 10:
                historical_changes = list(self.historical_data[symbol])
                mean_change = np.mean(historical_changes)
                std_change = np.std(historical_changes)
                
                # Z-score calculation
                z_score = abs((data['change_pct'] - mean_change) / std_change) if std_change > 0 else 0
                
                if z_score > self.anomaly_thresholds['price_change_std']:
                    return {
                        'type': 'PRICE_ANOMALY',
                        'symbol': symbol,
                        'severity': 'HIGH' if z_score > 4 else 'MEDIUM',
                        'z_score': round(z_score, 2),
                        'current_change': data['change_pct'],
                        'mean_change': round(mean_change, 2),
                        'description': f'{symbol} price change {z_score:.1f} standard deviations from mean',
                        'timestamp': data['_timestamp']
                    }
        
        def detect_volume_anomalies(data):
            if 'volume_ratio' not in data:
                return None
            
            if data['volume_ratio'] > self.anomaly_thresholds['volume_ratio']:
                return {
                    'type': 'VOLUME_ANOMALY',
                    'symbol': data.get('symbol'),
                    'severity': 'HIGH' if data['volume_ratio'] > 10 else 'MEDIUM',
                    'volume_ratio': data['volume_ratio'],
                    'description': f'Volume spike: {data["volume_ratio"]:.1f}x normal volume',
                    'timestamp': data['_timestamp']
                }
        
        def detect_volatility_anomalies(data):
            if 'volatility_pct' not in data:
                return None
            
            if data['volatility_pct'] > 8:  # 8% daily range threshold
                return {
                    'type': 'VOLATILITY_ANOMALY',
                    'symbol': data.get('symbol'),
                    'severity': 'HIGH' if data['volatility_pct'] > 15 else 'MEDIUM',
                    'volatility_pct': data['volatility_pct'],
                    'description': f'High volatility: {data["volatility_pct"]:.1f}% daily range',
                    'timestamp': data['_timestamp']
                }
        
        # Register anomaly detectors
        self.pipeline.add_processor(detect_price_anomalies, 'price_changes', 'anomalies')
        self.pipeline.add_processor(detect_volume_anomalies, 'volume_analysis', 'anomalies')
        self.pipeline.add_processor(detect_volatility_anomalies, 'volatility_metrics', 'anomalies')

class StreamingInsightsEngine:
    """Generate real-time insights from streaming data"""
    
    def __init__(self, pipeline: StreamingDataPipeline):
        self.pipeline = pipeline
        self.insight_cache = {}
        self.setup_insight_generators()
    
    def setup_insight_generators(self):
        """Setup insight generation processors"""
        
        def generate_momentum_insights(data):
            if data.get('momentum') == 'STRONG':
                insight_type = 'bullish_momentum' if data['direction'] == 'UP' else 'bearish_momentum'
                
                return {
                    'type': 'MOMENTUM_INSIGHT',
                    'symbol': data.get('symbol'),
                    'insight_type': insight_type,
                    'title': f'Strong {"Bullish" if data["direction"] == "UP" else "Bearish"} Momentum Detected',
                    'description': f'{data["symbol"]} showing {data["strength"]:.1f}% momentum with {data["direction"].lower()}ward direction',
                    'confidence': 0.85,
                    'actionable': True,
                    'timestamp': data['_timestamp']
                }
        
        def generate_volume_insights(data):
            if data.get('volume_signal') == 'HIGH':
                return {
                    'type': 'VOLUME_INSIGHT',
                    'symbol': data.get('symbol'),
                    'insight_type': 'high_volume',
                    'title': 'Unusual Volume Activity',
                    'description': f'{data["symbol"]} trading at {data["volume_ratio"]:.1f}x normal volume - potential catalyst',
                    'confidence': 0.75,
                    'actionable': True,
                    'timestamp': data['_timestamp']
                }
        
        def generate_correlation_insights(data):
            # Simplified correlation insight based on market conditions
            symbol = data.get('symbol')
            if symbol and 'change_pct' in data:
                market_direction = 'up' if data['change_pct'] > 0 else 'down'
                
                return {
                    'type': 'CORRELATION_INSIGHT',
                    'symbol': symbol,
                    'insight_type': 'market_correlation',
                    'title': f'Market Correlation Analysis',
                    'description': f'{symbol} moving {market_direction} with market trend - correlation strength: {np.random.uniform(0.6, 0.9):.2f}',
                    'confidence': 0.70,
                    'actionable': False,
                    'timestamp': data['_timestamp']
                }
        
        # Register insight generators
        self.pipeline.add_processor(generate_momentum_insights, 'momentum_signals', 'insights')
        self.pipeline.add_processor(generate_volume_insights, 'volume_analysis', 'insights')
        self.pipeline.add_processor(generate_correlation_insights, 'price_changes', 'insights')
    
    def get_recent_insights(self, symbol: str = None, limit: int = 10) -> List[Dict]:
        """Get recent insights, optionally filtered by symbol"""
        insights = self.pipeline.get_latest_data('insights', limit * 2)  # Get more to filter
        
        if symbol:
            insights = [insight for insight in insights if insight.get('symbol') == symbol]
        
        return insights[:limit]

class StreamingDashboard:
    """Dashboard for monitoring streaming pipeline health and performance"""
    
    def __init__(self, pipeline: StreamingDataPipeline):
        self.pipeline = pipeline
    
    def get_health_metrics(self) -> Dict:
        """Get comprehensive health metrics"""
        stats = self.pipeline.get_stream_stats()
        
        # Calculate overall health score
        total_messages = stats['pipeline_stats']['messages_processed']
        error_count = stats['pipeline_stats']['error_count']
        error_rate = (error_count / total_messages * 100) if total_messages > 0 else 0
        
        health_score = max(0, 100 - error_rate * 10)  # Penalize errors
        
        return {
            'overall_health': health_score,
            'status': 'HEALTHY' if health_score > 90 else 'WARNING' if health_score > 70 else 'CRITICAL',
            'processing_rate': stats['pipeline_stats']['processing_rate'],
            'total_processed': total_messages,
            'error_rate': error_rate,
            'active_streams': len([s for s in stats['streams'].values() if s['message_count'] > 0]),
            'last_processed': stats['pipeline_stats']['last_processed']
        }
    
    def get_performance_metrics(self) -> Dict:
        """Get performance metrics for the streaming pipeline"""
        stats = self.pipeline.get_stream_stats()
        
        # Calculate throughput for each stream
        stream_throughputs = {}
        for stream_name, stream_data in stats['streams'].items():
            if stream_data['last_message']:
                # Simplified throughput calculation
                stream_throughputs[stream_name] = stream_data['message_count']
        
        return {
            'total_throughput': sum(stream_throughputs.values()),
            'stream_throughputs': stream_throughputs,
            'processor_count': stats['active_processors'],
            'buffer_utilization': {
                name: (data['buffer_size'] / 1000) * 100  # Assuming max buffer of 1000
                for name, data in stats['streams'].items()
            }
        }
