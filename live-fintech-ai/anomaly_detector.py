"""
AI-Powered Market Anomaly Detection System
Real-time detection and analysis of market anomalies with machine learning
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from collections import deque
import random
from sklearn.ensemble import IsolationForest
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class MarketAnomalyDetector:
    """Advanced anomaly detection system for financial markets"""
    
    def __init__(self, lookback_period: int = 100):
        self.lookback_period = lookback_period
        self.historical_data = {}
        self.anomaly_models = {}
        self.detection_history = deque(maxlen=1000)
        self.thresholds = {
            'price_volatility': 3.0,
            'volume_spike': 5.0,
            'correlation_break': 0.3,
            'momentum_divergence': 2.5
        }
        self.initialize_models()
    
    def initialize_models(self):
        """Initialize machine learning models for anomaly detection"""
        self.anomaly_models = {
            'isolation_forest': IsolationForest(contamination=0.1, random_state=42),
            'clustering': DBSCAN(eps=0.5, min_samples=5),
            'statistical': 'z_score'  # Statistical method identifier
        }
    
    def add_market_data(self, symbol: str, data: Dict):
        """Add new market data for anomaly detection"""
        if symbol not in self.historical_data:
            self.historical_data[symbol] = deque(maxlen=self.lookbook_period)
        
        # Enrich data with timestamp
        enriched_data = {
            **data,
            'timestamp': datetime.now(),
            'processed': False
        }
        
        self.historical_data[symbol].append(enriched_data)
    
    def detect_price_anomalies(self, symbol: str, current_data: Dict) -> List[Dict]:
        """Detect price-based anomalies"""
        anomalies = []
        
        if symbol not in self.historical_data or len(self.historical_data[symbol]) < 20:
            return anomalies
        
        historical_prices = [d['price'] for d in self.historical_data[symbol] if 'price' in d]
        historical_changes = [d.get('change_pct', 0) for d in self.historical_data[symbol]]
        
        if len(historical_prices) < 10:
            return anomalies
        
        # Statistical anomaly detection
        current_price = current_data.get('price', 0)
        current_change = current_data.get('change_pct', 0)
        
        # Z-score based detection
        price_mean = np.mean(historical_prices)
        price_std = np.std(historical_prices)
        change_mean = np.mean(historical_changes)
        change_std = np.std(historical_changes)
        
        if price_std > 0:
            price_z_score = abs((current_price - price_mean) / price_std)
            if price_z_score > self.thresholds['price_volatility']:
                anomalies.append({
                    'type': 'PRICE_STATISTICAL_ANOMALY',
                    'symbol': symbol,
                    'severity': 'HIGH' if price_z_score > 4 else 'MEDIUM',
                    'z_score': round(price_z_score, 2),
                    'current_price': current_price,
                    'historical_mean': round(price_mean, 2),
                    'description': f'Price {price_z_score:.1f} standard deviations from historical mean',
                    'confidence': min(0.95, 0.5 + (price_z_score / 10)),
                    'timestamp': datetime.now(),
                    'model_used': 'statistical_z_score'
                })
        
        if change_std > 0:
            change_z_score = abs((current_change - change_mean) / change_std)
            if change_z_score > self.thresholds['price_volatility']:
                anomalies.append({
                    'type': 'PRICE_CHANGE_ANOMALY',
                    'symbol': symbol,
                    'severity': 'HIGH' if change_z_score > 4 else 'MEDIUM',
                    'z_score': round(change_z_score, 2),
                    'current_change': current_change,
                    'historical_mean': round(change_mean, 2),
                    'description': f'Price change {change_z_score:.1f} standard deviations from normal',
                    'confidence': min(0.95, 0.5 + (change_z_score / 10)),
                    'timestamp': datetime.now(),
                    'model_used': 'statistical_z_score'
                })
        
        # Gap detection
        if len(historical_prices) > 1:
            previous_close = historical_prices[-1]
            gap_pct = abs((current_price - previous_close) / previous_close) * 100
            
            if gap_pct > 5:  # 5% gap threshold
                anomalies.append({
                    'type': 'PRICE_GAP_ANOMALY',
                    'symbol': symbol,
                    'severity': 'HIGH' if gap_pct > 10 else 'MEDIUM',
                    'gap_percent': round(gap_pct, 2),
                    'current_price': current_price,
                    'previous_close': previous_close,
                    'description': f'Price gap of {gap_pct:.1f}% detected',
                    'confidence': 0.90,
                    'timestamp': datetime.now(),
                    'model_used': 'gap_detection'
                })
        
        return anomalies
    
    def detect_volume_anomalies(self, symbol: str, current_data: Dict) -> List[Dict]:
        """Detect volume-based anomalies"""
        anomalies = []
        
        if symbol not in self.historical_data or len(self.historical_data[symbol]) < 10:
            return anomalies
        
        historical_volumes = [d.get('volume', 0) for d in self.historical_data[symbol] if d.get('volume', 0) > 0]
        current_volume = current_data.get('volume', 0)
        
        if len(historical_volumes) < 5 or current_volume == 0:
            return anomalies
        
        # Volume spike detection
        avg_volume = np.mean(historical_volumes)
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
        
        if volume_ratio > self.thresholds['volume_spike']:
            anomalies.append({
                'type': 'VOLUME_SPIKE_ANOMALY',
                'symbol': symbol,
                'severity': 'HIGH' if volume_ratio > 10 else 'MEDIUM',
                'volume_ratio': round(volume_ratio, 2),
                'current_volume': current_volume,
                'average_volume': int(avg_volume),
                'description': f'Volume spike: {volume_ratio:.1f}x average volume',
                'confidence': min(0.95, 0.6 + (volume_ratio / 20)),
                'timestamp': datetime.now(),
                'model_used': 'volume_ratio_analysis'
            })
        
        # Volume drought detection
        elif volume_ratio < 0.2:  # Less than 20% of average
            anomalies.append({
                'type': 'VOLUME_DROUGHT_ANOMALY',
                'symbol': symbol,
                'severity': 'MEDIUM',
                'volume_ratio': round(volume_ratio, 2),
                'current_volume': current_volume,
                'average_volume': int(avg_volume),
                'description': f'Unusually low volume: {volume_ratio:.1%} of average',
                'confidence': 0.75,
                'timestamp': datetime.now(),
                'model_used': 'volume_ratio_analysis'
            })
        
        return anomalies
    
    def detect_pattern_anomalies(self, symbol: str, current_data: Dict) -> List[Dict]:
        """Detect pattern-based anomalies using machine learning"""
        anomalies = []
        
        if symbol not in self.historical_data or len(self.historical_data[symbol]) < 50:
            return anomalies
        
        # Prepare feature matrix
        try:
            features = []
            for data_point in list(self.historical_data[symbol])[-50:]:  # Last 50 points
                if all(key in data_point for key in ['price', 'volume', 'change_pct']):
                    features.append([
                        data_point['price'],
                        data_point['volume'],
                        data_point['change_pct'],
                        data_point.get('high', data_point['price']),
                        data_point.get('low', data_point['price'])
                    ])
            
            if len(features) < 20:
                return anomalies
            
            features_array = np.array(features)
            
            # Normalize features
            scaler = StandardScaler()
            features_normalized = scaler.fit_transform(features_array)
            
            # Isolation Forest detection
            iso_forest = IsolationForest(contamination=0.1, random_state=42)
            iso_forest.fit(features_normalized)
            
            # Predict on current data
            current_features = np.array([[
                current_data.get('price', 0),
                current_data.get('volume', 0),
                current_data.get('change_pct', 0),
                current_data.get('high', current_data.get('price', 0)),
                current_data.get('low', current_data.get('price', 0))
            ]])
            
            current_normalized = scaler.transform(current_features)
            anomaly_score = iso_forest.decision_function(current_normalized)[0]
            is_anomaly = iso_forest.predict(current_normalized)[0] == -1
            
            if is_anomaly:
                anomalies.append({
                    'type': 'ML_PATTERN_ANOMALY',
                    'symbol': symbol,
                    'severity': 'HIGH' if anomaly_score < -0.5 else 'MEDIUM',
                    'anomaly_score': round(anomaly_score, 3),
                    'description': f'Machine learning model detected unusual pattern (score: {anomaly_score:.3f})',
                    'confidence': min(0.90, 0.5 + abs(anomaly_score)),
                    'timestamp': datetime.now(),
                    'model_used': 'isolation_forest'
                })
        
        except Exception as e:
            # Fallback to simpler pattern detection
            anomalies.extend(self._simple_pattern_detection(symbol, current_data))
        
        return anomalies
    
    def _simple_pattern_detection(self, symbol: str, current_data: Dict) -> List[Dict]:
        """Simple pattern-based anomaly detection as fallback"""
        anomalies = []
        
        # Detect unusual price-volume relationship
        current_price_change = abs(current_data.get('change_pct', 0))
        current_volume = current_data.get('volume', 0)
        
        historical_data = list(self.historical_data[symbol])[-20:]  # Last 20 points
        avg_volume = np.mean([d.get('volume', 0) for d in historical_data if d.get('volume', 0) > 0])
        
        # High price movement with low volume (divergence)
        if current_price_change > 3 and current_volume < avg_volume * 0.5:
            anomalies.append({
                'type': 'PRICE_VOLUME_DIVERGENCE',
                'symbol': symbol,
                'severity': 'MEDIUM',
                'price_change': current_price_change,
                'volume_ratio': round(current_volume / avg_volume, 2) if avg_volume > 0 else 0,
                'description': f'High price movement ({current_price_change:.1f}%) with unusually low volume',
                'confidence': 0.75,
                'timestamp': datetime.now(),
                'model_used': 'pattern_analysis'
            })
        
        return anomalies
    
    def detect_correlation_anomalies(self, symbols: List[str], market_data: Dict) -> List[Dict]:
        """Detect anomalies in correlation patterns between stocks"""
        anomalies = []
        
        if len(symbols) < 2:
            return anomalies
        
        # Calculate current correlations (simplified)
        price_changes = {}
        for symbol in symbols:
            if symbol in market_data and 'change_pct' in market_data[symbol]:
                price_changes[symbol] = market_data[symbol]['change_pct']
        
        if len(price_changes) < 2:
            return anomalies
        
        # Detect stocks moving opposite to market
        market_direction = np.mean(list(price_changes.values()))
        
        for symbol, change in price_changes.items():
            # Check for strong divergence from market
            if abs(change - market_direction) > 5:  # 5% divergence threshold
                anomalies.append({
                    'type': 'CORRELATION_DIVERGENCE',
                    'symbol': symbol,
                    'severity': 'MEDIUM',
                    'stock_change': change,
                    'market_average': round(market_direction, 2),
                    'divergence': round(abs(change - market_direction), 2),
                    'description': f'{symbol} diverging from market trend by {abs(change - market_direction):.1f}%',
                    'confidence': 0.70,
                    'timestamp': datetime.now(),
                    'model_used': 'correlation_analysis'
                })
        
        return anomalies
    
    def detect_time_series_anomalies(self, symbol: str, current_data: Dict) -> List[Dict]:
        """Detect time-series based anomalies"""
        anomalies = []
        
        if symbol not in self.historical_data or len(self.historical_data[symbol]) < 30:
            return anomalies
        
        historical_data = list(self.historical_data[symbol])
        
        # Create time series features
        prices = [d.get('price', 0) for d in historical_data[-20:]]  # Last 20 prices
        
        if len(prices) < 10:
            return anomalies
        
        # Simple trend analysis
        recent_trend = np.polyfit(range(len(prices)), prices, 1)[0]  # Linear trend
        current_price = current_data.get('price', 0)
        
        # Predict next price based on trend
        predicted_price = prices[-1] + recent_trend
        price_deviation = abs(current_price - predicted_price) / predicted_price * 100 if predicted_price > 0 else 0
        
        if price_deviation > 3:  # 3% deviation from trend
            anomalies.append({
                'type': 'TREND_DEVIATION_ANOMALY',
                'symbol': symbol,
                'severity': 'MEDIUM' if price_deviation > 5 else 'LOW',
                'predicted_price': round(predicted_price, 2),
                'actual_price': current_price,
                'deviation_pct': round(price_deviation, 2),
                'description': f'Price deviates {price_deviation:.1f}% from expected trend',
                'confidence': min(0.85, 0.5 + (price_deviation / 20)),
                'timestamp': datetime.now(),
                'model_used': 'trend_analysis'
            })
        
        return anomalies
    
    def comprehensive_anomaly_scan(self, symbol: str, current_data: Dict, market_data: Dict = None) -> Dict:
        """Perform comprehensive anomaly detection"""
        all_anomalies = []
        
        # Run all detection methods
        all_anomalies.extend(self.detect_price_anomalies(symbol, current_data))
        all_anomalies.extend(self.detect_volume_anomalies(symbol, current_data))
        all_anomalies.extend(self.detect_pattern_anomalies(symbol, current_data))
        all_anomalies.extend(self.detect_time_series_anomalies(symbol, current_data))
        
        # Add correlation anomalies if market data provided
        if market_data and len(market_data) > 1:
            correlation_anomalies = self.detect_correlation_anomalies(list(market_data.keys()), market_data)
            symbol_correlation_anomalies = [a for a in correlation_anomalies if a.get('symbol') == symbol]
            all_anomalies.extend(symbol_correlation_anomalies)
        
        # Prioritize and deduplicate anomalies
        high_severity = [a for a in all_anomalies if a.get('severity') == 'HIGH']
        medium_severity = [a for a in all_anomalies if a.get('severity') == 'MEDIUM']
        low_severity = [a for a in all_anomalies if a.get('severity') == 'LOW']
        
        # Store in detection history
        detection_record = {
            'symbol': symbol,
            'timestamp': datetime.now(),
            'anomalies_detected': len(all_anomalies),
            'high_severity_count': len(high_severity),
            'data_processed': current_data
        }
        self.detection_history.append(detection_record)
        
        return {
            'symbol': symbol,
            'total_anomalies': len(all_anomalies),
            'high_severity': high_severity,
            'medium_severity': medium_severity,
            'low_severity': low_severity,
            'all_anomalies': all_anomalies,
            'risk_score': self._calculate_risk_score(all_anomalies),
            'detection_summary': {
                'models_used': list(set([a.get('model_used', 'unknown') for a in all_anomalies])),
                'highest_confidence': max([a.get('confidence', 0) for a in all_anomalies], default=0),
                'detection_timestamp': datetime.now()
            }
        }
    
    def _calculate_risk_score(self, anomalies: List[Dict]) -> float:
        """Calculate overall risk score based on detected anomalies"""
        if not anomalies:
            return 0.0
        
        score = 0.0
        severity_weights = {'HIGH': 1.0, 'MEDIUM': 0.6, 'LOW': 0.3}
        
        for anomaly in anomalies:
            severity = anomaly.get('severity', 'LOW')
            confidence = anomaly.get('confidence', 0.5)
            score += severity_weights.get(severity, 0.3) * confidence
        
        # Normalize to 0-100 scale
        return min(100, score * 20)
    
    def get_detection_statistics(self) -> Dict:
        """Get statistics about anomaly detection performance"""
        if not self.detection_history:
            return {'message': 'No detection history available'}
        
        total_detections = len(self.detection_history)
        total_anomalies = sum(record['anomalies_detected'] for record in self.detection_history)
        total_high_severity = sum(record['high_severity_count'] for record in self.detection_history)
        
        recent_detections = [r for r in self.detection_history if r['timestamp'] > datetime.now() - timedelta(hours=1)]
        
        return {
            'total_scans': total_detections,
            'total_anomalies_found': total_anomalies,
            'high_severity_anomalies': total_high_severity,
            'detection_rate': round(total_anomalies / total_detections, 2) if total_detections > 0 else 0,
            'recent_activity': {
                'last_hour_scans': len(recent_detections),
                'last_hour_anomalies': sum(r['anomalies_detected'] for r in recent_detections)
            },
            'model_performance': {
                'models_active': len(self.anomaly_models),
                'thresholds': self.thresholds,
                'historical_data_points': sum(len(data) for data in self.historical_data.values())
            }
        }
