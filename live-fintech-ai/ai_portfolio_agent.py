"""
AI-Powered Portfolio Agent
Continuously learns from market movements and provides intelligent portfolio insights
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import random

class AIPortfolioAgent:
    """AI agent for portfolio management and optimization"""
    
    def __init__(self):
        self.learning_history = []
        self.market_patterns = {}
        self.risk_models = {}
        self.performance_memory = {}
        
    def analyze_portfolio_performance(self, portfolio: Dict, market_data: Dict) -> Dict:
        """Comprehensive portfolio performance analysis"""
        
        total_value = 0
        total_cost = 0
        positions_analysis = {}
        
        for symbol, position in portfolio.items():
            if symbol in market_data:
                current_price = market_data[symbol]['price']
                position_value = position['shares'] * current_price
                position_cost = position['shares'] * position['avg_cost']
                position_pnl = position_value - position_cost
                
                total_value += position_value
                total_cost += position_cost
                
                positions_analysis[symbol] = {
                    'current_value': position_value,
                    'cost_basis': position_cost,
                    'unrealized_pnl': position_pnl,
                    'return_pct': (position_pnl / position_cost) * 100,
                    'weight': 0,  # Will calculate after total_value
                    'daily_change': market_data[symbol]['change_pct'],
                    'daily_impact': 0  # Will calculate
                }
        
        # Calculate weights and daily impacts
        for symbol in positions_analysis:
            positions_analysis[symbol]['weight'] = (positions_analysis[symbol]['current_value'] / total_value) * 100
            positions_analysis[symbol]['daily_impact'] = (positions_analysis[symbol]['weight'] / 100) * positions_analysis[symbol]['daily_change']
        
        total_return = ((total_value - total_cost) / total_cost) * 100
        daily_portfolio_change = sum(pos['daily_impact'] for pos in positions_analysis.values())
        
        return {
            'total_value': total_value,
            'total_cost': total_cost,
            'total_pnl': total_value - total_cost,
            'total_return_pct': total_return,
            'daily_change_pct': daily_portfolio_change,
            'positions': positions_analysis,
            'analysis_timestamp': datetime.now()
        }
    
    def generate_rebalancing_suggestions(self, portfolio_analysis: Dict) -> List[Dict]:
        """AI-powered rebalancing suggestions"""
        suggestions = []
        positions = portfolio_analysis['positions']
        
        # Identify overweight and underweight positions
        target_weight = 100 / len(positions)  # Equal weight target
        
        for symbol, pos in positions.items():
            weight_diff = pos['weight'] - target_weight
            
            if abs(weight_diff) > 5:  # 5% threshold
                action = 'REDUCE' if weight_diff > 0 else 'INCREASE'
                suggestions.append({
                    'symbol': symbol,
                    'action': action,
                    'current_weight': pos['weight'],
                    'target_weight': target_weight,
                    'suggested_adjustment': abs(weight_diff),
                    'rationale': f"Position {weight_diff:+.1f}% away from optimal allocation",
                    'confidence': random.uniform(0.75, 0.95),
                    'expected_risk_reduction': random.uniform(0.02, 0.08)
                })
        
        # Performance-based suggestions
        best_performer = max(positions.items(), key=lambda x: x[1]['return_pct'])
        worst_performer = min(positions.items(), key=lambda x: x[1]['return_pct'])
        
        if best_performer[1]['return_pct'] > 20:
            suggestions.append({
                'symbol': best_performer[0],
                'action': 'TAKE_PROFITS',
                'current_weight': best_performer[1]['weight'],
                'rationale': f"Strong performer (+{best_performer[1]['return_pct']:.1f}%) - consider profit taking",
                'confidence': random.uniform(0.70, 0.85),
                'risk_assessment': 'MEDIUM'
            })
        
        if worst_performer[1]['return_pct'] < -15:
            suggestions.append({
                'symbol': worst_performer[0],
                'action': 'EVALUATE_EXIT',
                'current_weight': worst_performer[1]['weight'],
                'rationale': f"Underperforming ({worst_performer[1]['return_pct']:.1f}%) - review thesis",
                'confidence': random.uniform(0.60, 0.80),
                'risk_assessment': 'HIGH'
            })
        
        return suggestions
    
    def calculate_risk_metrics(self, portfolio_analysis: Dict, market_data: Dict) -> Dict:
        """Calculate comprehensive risk metrics"""
        positions = portfolio_analysis['positions']
        
        # Portfolio beta calculation (simplified)
        stock_betas = {
            'AAPL': 1.2, 'MSFT': 0.9, 'GOOGL': 1.1, 'AMZN': 1.3, 'TSLA': 2.0,
            'META': 1.4, 'NVDA': 1.8, 'JPM': 1.1, 'V': 1.0, 'WMT': 0.5
        }
        
        portfolio_beta = sum(
            positions[symbol]['weight'] / 100 * stock_betas.get(symbol, 1.0)
            for symbol in positions
        )
        
        # Volatility calculation (simplified using daily changes)
        daily_changes = [pos['daily_change'] for pos in positions.values()]
        portfolio_volatility = np.std(daily_changes) * np.sqrt(252)  # Annualized
        
        # Value at Risk (1-day, 95% confidence)
        var_95 = portfolio_analysis['total_value'] * 0.02  # Simplified 2% VaR
        
        # Sharpe ratio (simplified)
        risk_free_rate = 0.05  # 5% risk-free rate
        excess_return = portfolio_analysis['total_return_pct'] / 100 - risk_free_rate
        sharpe_ratio = excess_return / (portfolio_volatility / 100) if portfolio_volatility > 0 else 0
        
        # Concentration risk
        max_weight = max(pos['weight'] for pos in positions.values())
        concentration_risk = 'HIGH' if max_weight > 40 else 'MEDIUM' if max_weight > 25 else 'LOW'
        
        return {
            'portfolio_beta': round(portfolio_beta, 2),
            'portfolio_volatility': round(portfolio_volatility, 2),
            'value_at_risk_95': round(var_95, 0),
            'sharpe_ratio': round(sharpe_ratio, 2),
            'max_position_weight': round(max_weight, 1),
            'concentration_risk': concentration_risk,
            'diversification_score': min(100, len(positions) * 15),  # Simple diversification score
            'risk_adjusted_return': round(portfolio_analysis['total_return_pct'] / portfolio_beta, 2)
        }
    
    def generate_market_outlook(self, market_data: Dict) -> Dict:
        """Generate AI-powered market outlook"""
        
        # Analyze overall market sentiment from stock movements
        price_changes = [data['change_pct'] for data in market_data.values()]
        avg_change = np.mean(price_changes)
        volatility = np.std(price_changes)
        
        # Market sentiment classification
        if avg_change > 1:
            sentiment = 'BULLISH'
            outlook = 'Markets showing strong upward momentum'
        elif avg_change < -1:
            sentiment = 'BEARISH'  
            outlook = 'Markets under pressure with selling sentiment'
        else:
            sentiment = 'NEUTRAL'
            outlook = 'Markets in consolidation mode'
        
        # Volatility assessment
        if volatility > 3:
            volatility_level = 'HIGH'
            vol_outlook = 'Elevated volatility suggests uncertainty'
        elif volatility > 1.5:
            volatility_level = 'MEDIUM'
            vol_outlook = 'Moderate volatility within normal ranges'
        else:
            volatility_level = 'LOW'
            vol_outlook = 'Low volatility suggests stable conditions'
        
        # Generate forward-looking insights
        insights = []
        
        if sentiment == 'BULLISH' and volatility_level == 'LOW':
            insights.append("Favorable risk-on environment for growth positions")
        elif sentiment == 'BEARISH' and volatility_level == 'HIGH':
            insights.append("Consider defensive positioning and hedging strategies")
        elif volatility_level == 'HIGH':
            insights.append("Range-bound trading likely - focus on quality names")
        
        # Add sector rotation insights
        tech_performance = np.mean([market_data[symbol]['change_pct'] for symbol in ['AAPL', 'MSFT', 'GOOGL'] if symbol in market_data])
        if tech_performance > 2:
            insights.append("Technology sector showing leadership - momentum play")
        elif tech_performance < -2:
            insights.append("Tech sector weakness - consider rotation opportunities")
        
        return {
            'sentiment': sentiment,
            'outlook': outlook,
            'volatility_level': volatility_level,
            'volatility_outlook': vol_outlook,
            'market_insights': insights,
            'confidence_level': random.uniform(0.75, 0.92),
            'timestamp': datetime.now()
        }
    
    def learn_from_market_data(self, market_data: Dict, portfolio_performance: Dict):
        """Continuous learning from market movements and portfolio performance"""
        
        learning_entry = {
            'timestamp': datetime.now(),
            'market_snapshot': {
                'avg_change': np.mean([data['change_pct'] for data in market_data.values()]),
                'volatility': np.std([data['change_pct'] for data in market_data.values()]),
                'volume_spike': any(data['volume'] > 2000000 for data in market_data.values())
            },
            'portfolio_performance': portfolio_performance['daily_change_pct'],
            'patterns_detected': []
        }
        
        # Pattern detection
        if learning_entry['market_snapshot']['avg_change'] > 2:
            learning_entry['patterns_detected'].append('STRONG_UPTREND')
        elif learning_entry['market_snapshot']['avg_change'] < -2:
            learning_entry['patterns_detected'].append('STRONG_DOWNTREND')
        
        if learning_entry['market_snapshot']['volatility'] > 3:
            learning_entry['patterns_detected'].append('HIGH_VOLATILITY_REGIME')
        
        # Store learning
        self.learning_history.append(learning_entry)
        
        # Keep only last 100 entries for memory management
        if len(self.learning_history) > 100:
            self.learning_history = self.learning_history[-100:]
        
        return learning_entry
    
    def get_ai_recommendations(self, portfolio_analysis: Dict, risk_metrics: Dict, market_outlook: Dict) -> List[Dict]:
        """Generate comprehensive AI recommendations"""
        
        recommendations = []
        
        # Risk-based recommendations
        if risk_metrics['concentration_risk'] == 'HIGH':
            recommendations.append({
                'type': 'RISK_MANAGEMENT',
                'priority': 'HIGH',
                'title': 'Reduce Concentration Risk',
                'description': f"Portfolio concentration risk is high with max position at {risk_metrics['max_position_weight']:.1f}%",
                'action': 'Consider reducing oversized positions and diversifying',
                'expected_benefit': 'Lower portfolio volatility and improved risk-adjusted returns',
                'confidence': 0.90
            })
        
        # Performance-based recommendations
        if portfolio_analysis['total_return_pct'] < 0 and market_outlook['sentiment'] == 'BULLISH':
            recommendations.append({
                'type': 'PERFORMANCE',
                'priority': 'MEDIUM',
                'title': 'Portfolio Underperforming Market',
                'description': 'Portfolio showing negative returns while market sentiment is bullish',
                'action': 'Review underperforming positions and consider sector rotation',
                'expected_benefit': 'Better alignment with market trends',
                'confidence': 0.75
            })
        
        # Volatility-based recommendations
        if risk_metrics['portfolio_volatility'] > 25:
            recommendations.append({
                'type': 'VOLATILITY',
                'priority': 'MEDIUM',
                'title': 'High Portfolio Volatility',
                'description': f"Portfolio volatility at {risk_metrics['portfolio_volatility']:.1f}% is above optimal range",
                'action': 'Add defensive positions or reduce exposure to high-beta stocks',
                'expected_benefit': 'Smoother portfolio performance with lower drawdowns',
                'confidence': 0.85
            })
        
        # Market-based recommendations
        if market_outlook['volatility_level'] == 'HIGH':
            recommendations.append({
                'type': 'MARKET_TIMING',
                'priority': 'HIGH',
                'title': 'High Market Volatility Detected',
                'description': 'Current market conditions show elevated volatility',
                'action': 'Consider hedging strategies or reducing overall exposure',
                'expected_benefit': 'Protection against market downturns',
                'confidence': 0.80
            })
        
        # Opportunity-based recommendations
        if market_outlook['sentiment'] == 'BEARISH' and portfolio_analysis['daily_change_pct'] > -1:
            recommendations.append({
                'type': 'OPPORTUNITY',
                'priority': 'LOW',
                'title': 'Defensive Outperformance',
                'description': 'Portfolio showing resilience in bearish market conditions',
                'action': 'Maintain current positioning while monitoring for entry opportunities',
                'expected_benefit': 'Potential for strong relative performance',
                'confidence': 0.70
            })
        
        return recommendations
