"""
Streamlit Dashboard for Live Fintech AI Assistant
Real-time dashboard showing stock prices, movements, and AI explanations
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import asyncio
import time
import json
from typing import Dict, List, Any

# Configure page
st.set_page_config(
    page_title="Live Fintech AI Assistant",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import our services
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from database.mongo_connector import DatabaseService

# Import appropriate services based on configuration
if Config.DATA_SOURCE_MODE == 'webscraping':
    from services.web_stock_service import WebScrapingStockService as StockService
    from services.web_news_service import WebScrapingNewsService as NewsService
else:
    from services.stock_service import StockService
    from services.news_service import NewsService

# Initialize services
@st.cache_resource
def init_services():
    """Initialize services with caching"""
    return {
        'stock': StockService(),
        'news': NewsService(),
        'db': DatabaseService()
    }

def main():
    """Main dashboard function"""
    st.title("📈 Live Fintech AI Assistant")
    st.markdown("*Real-time stock movements with AI-powered explanations*")
    
    # Initialize services
    services = init_services()
    
    # Sidebar controls
    with st.sidebar:
        st.header("⚙️ Controls")
        
        # Auto-refresh toggle
        auto_refresh = st.checkbox("Auto Refresh", value=True)
        
        # Refresh interval
        refresh_interval = st.slider("Refresh Interval (seconds)", 10, 120, 30)
        
        # Symbol selection
        selected_symbols = st.multiselect(
            "Select Symbols",
            Config.STOCK_SYMBOLS,
            default=Config.STOCK_SYMBOLS
        )
        
        # Time range for historical data
        hours_back = st.selectbox("Historical Data Range", [1, 2, 6, 12, 24], index=2)
        
        # Manual refresh button
        if st.button("🔄 Refresh Now"):
            st.rerun()
        
        # Configuration status
        st.subheader("📊 System Status")
        config_valid = Config.validate_config()
        
        if config_valid:
            st.success("✅ Configuration Valid")
        else:
            st.error("❌ Configuration Issues")
            st.info("Please check your .env file and API keys")
        
        # Database connection status
        if services['db'].client:
            st.success("✅ Database Connected")
        else:
            st.error("❌ Database Disconnected")
    
    # Main content area
    if not config_valid:
        st.error("🚨 Configuration Error")
        st.info("Please configure your API keys in the .env file before using the dashboard.")
        return
    
    # Current prices section
    st.header("💰 Current Stock Prices")
    
    col1, col2, col3 = st.columns(3)
    
    # Fetch current prices
    with st.spinner("Fetching current prices..."):
        current_prices = services['stock'].fetch_all_prices()
    
    if current_prices:
        for i, (symbol, price_data) in enumerate(current_prices.items()):
            if symbol in selected_symbols:
                with [col1, col2, col3][i % 3]:
                    # Price card with null-safe change_percent handling
                    try:
                        if hasattr(price_data, 'change_percent') and price_data.change_percent is not None:
                            change_color = "🟢" if price_data.change_percent >= 0 else "🔴"
                            delta_text = f"{price_data.change_percent:+.2f}%"
                        else:
                            change_color = "⚪"  # Neutral color for unknown change
                            delta_text = "N/A"
                    except (AttributeError, TypeError):
                        change_color = "⚪"  # Fallback for any attribute/type errors
                        delta_text = "N/A"
                    
                    st.metric(
                        label=f"{change_color} {symbol}",
                        value=f"${price_data.price:.2f}",
                        delta=delta_text
                    )
    else:
        st.warning("No price data available. Please check your API keys and connection.")
    
    # Recent movements section
    st.header("🚨 Recent Price Movements")
    
    # Detect movements
    movements = services['stock'].detect_price_movements(current_prices)
    
    if movements:
        for movement in movements:
            if movement.symbol in selected_symbols:
                # Movement alert
                movement_type_emoji = "📈" if movement.change_percent > 0 else "📉"
                alert_type = "success" if movement.change_percent > 0 else "error"
                
                st.markdown(f"""
                <div class="alert alert-{alert_type}">
                    {movement_type_emoji} <strong>{movement.symbol}</strong> moved {movement.change_percent:+.2f}% 
                    (${movement.previous_price:.2f} → ${movement.current_price:.2f})
                    <br><small>{movement.timestamp.strftime('%H:%M:%S')}</small>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No significant movements detected in the current monitoring period.")
    
    # AI Explanations section
    st.header("🤖 AI Explanations")
    
    # Fetch recent explanations from database
    recent_explanations = services['db'].get_recent_explanations(hours=hours_back)
    
    if recent_explanations:
        # Filter by selected symbols
        filtered_explanations = [
            exp for exp in recent_explanations 
            if exp['symbol'] in selected_symbols
        ]
        
        for explanation in filtered_explanations[:10]:  # Show latest 10
            with st.expander(
                f"🎯 {explanation['symbol']} - {explanation['explanation_type'].replace('_', ' ').title()}",
                expanded=False
            ):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(explanation['explanation'])
                    
                    # Show related news if available
                    if explanation.get('news_articles'):
                        st.subheader("📰 Related News")
                        for news in explanation['news_articles'][:3]:
                            st.markdown(f"- [{news['title']}]({news['url']}) - *{news['source']}*")
                
                with col2:
                    # Confidence score
                    confidence = explanation.get('confidence_score', 0) * 100
                    st.metric("Confidence", f"{confidence:.0f}%")
                    
                    # Price movement details
                    price_movement = explanation.get('price_movement', {})
                    if price_movement:
                        st.metric(
                            "Price Change",
                            f"{price_movement.get('change_percent', 0):+.2f}%"
                        )
                    
                    # Timestamp
                    timestamp = explanation.get('timestamp')
                    if timestamp:
                        if isinstance(timestamp, str):
                            timestamp = datetime.fromisoformat(timestamp)
                        st.caption(f"⏰ {timestamp.strftime('%H:%M:%S')}")
    else:
        st.info("No AI explanations available for the selected time range.")
    
    # News section
    st.header("📰 Latest Financial News")
    
    # Fetch recent news from database
    recent_news = services['db'].get_recent_news(hours=hours_back)
    
    if recent_news:
        # Filter by selected symbols
        filtered_news = [
            news for news in recent_news 
            if news['symbol'] in selected_symbols
        ]
        
        # Group news by symbol
        news_by_symbol = {}
        for news in filtered_news:
            symbol = news['symbol']
            if symbol not in news_by_symbol:
                news_by_symbol[symbol] = []
            news_by_symbol[symbol].append(news)
        
        # Display news in tabs
        if news_by_symbol:
            tabs = st.tabs(list(news_by_symbol.keys()))
            
            for tab, symbol in zip(tabs, news_by_symbol.keys()):
                with tab:
                    for news in news_by_symbol[symbol][:5]:  # Show 5 latest per symbol
                        col1, col2 = st.columns([4, 1])
                        
                        with col1:
                            st.markdown(f"**[{news['title']}]({news['url']})**")
                            if news.get('description'):
                                st.write(news['description'][:200] + "...")
                        
                        with col2:
                            st.caption(f"📅 {news['source']}")
                            published = news.get('published_at')
                            if published:
                                if isinstance(published, str):
                                    published = datetime.fromisoformat(published)
                                st.caption(f"⏰ {published.strftime('%H:%M')}")
                        
                        st.divider()
    else:
        st.info("No recent news available for the selected symbols.")
    
    # Statistics section
    st.header("📊 Movement Statistics")
    
    # Create statistics for each symbol
    stats_cols = st.columns(len(selected_symbols))
    
    for i, symbol in enumerate(selected_symbols):
        with stats_cols[i]:
            st.subheader(symbol)
            
            # Get statistics from database
            stats = services['db'].get_movement_statistics(symbol, days=7)
            
            if stats and stats.get('total_movements', 0) > 0:
                st.metric("Total Movements", stats.get('total_movements', 0))
                st.metric("Avg Change", f"{stats.get('avg_change_percent', 0):+.2f}%")
                st.metric("Max Change", f"{stats.get('max_change_percent', 0):+.2f}%")
                
                # Up/Down ratio
                up_moves = stats.get('up_movements', 0)
                down_moves = stats.get('down_movements', 0)
                total_moves = up_moves + down_moves
                
                if total_moves > 0:
                    up_ratio = (up_moves / total_moves) * 100
                    st.metric("Up Moves", f"{up_ratio:.0f}%")
            else:
                st.info("No movement data available")
    
    # Price history chart
    st.header("📈 Price History")
    
    # Fetch price history for selected symbols
    price_history_data = {}
    for symbol in selected_symbols:
        history = services['stock'].get_price_history(symbol, minutes=hours_back*60)
        if history:
            price_history_data[symbol] = history
    
    if price_history_data:
        # Create plotly chart
        fig = go.Figure()
        
        for symbol, history in price_history_data.items():
            if len(history) > 1:
                timestamps = [price.timestamp for price in history]
                prices = [price.price for price in history]
                
                fig.add_trace(go.Scatter(
                    x=timestamps,
                    y=prices,
                    mode='lines+markers',
                    name=symbol,
                    line=dict(width=2)
                ))
        
        fig.update_layout(
            title="Stock Price History",
            xaxis_title="Time",
            yaxis_title="Price ($)",
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No price history data available for chart.")
    
    # Auto-refresh functionality
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()

# Custom CSS for better styling
st.markdown("""
<style>
.alert {
    padding: 10px;
    margin: 5px 0;
    border-radius: 5px;
}
.alert-success {
    background-color: #d4edda;
    border: 1px solid #c3e6cb;
    color: #155724;
}
.alert-error {
    background-color: #f8d7da;
    border: 1px solid #f5c6cb;
    color: #721c24;
}
</style>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
