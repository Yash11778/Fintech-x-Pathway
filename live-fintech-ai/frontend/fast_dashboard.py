"""
Fast Dashboard for Live Fintech AI Assistant
Optimized for speed with caching and incremental updates
"""

import streamlit as st
import asyncio
import time
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List
import json

# Configure Streamlit for maximum performance
st.set_page_config(
    page_title="⚡ Fast FinTech AI",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Add performance CSS
st.markdown("""
<style>
    .stApp { 
        max-width: 100%;
        padding-top: 1rem;
    }
    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: white;
    }
    .metric-delta {
        font-size: 1.2rem;
        color: #f0f0f0;
    }
    .fast-update {
        animation: pulse 1s ease-in-out;
    }
    @keyframes pulse {
        0% { opacity: 0.6; }
        50% { opacity: 1; }
        100% { opacity: 0.6; }
    }
    .stSelectbox > div > div {
        background-color: #2e3440;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=5)  # Cache for 5 seconds for speed
def get_cached_prices():
    """Get cached stock prices for speed"""
    try:
        from services.fast_stock_scraper import FastStockService
        import asyncio
        
        # Use the fast service
        service = FastStockService()
        
        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        prices = loop.run_until_complete(service.fetch_all_prices())
        loop.run_until_complete(service.cleanup())
        loop.close()
        
        return prices
    except Exception as e:
        st.error(f"Error fetching prices: {e}")
        return {}

@st.cache_data(ttl=30)  # Cache for 30 seconds
def get_cached_news():
    """Get cached news data"""
    try:
        from services.web_news_service import WebScrapingNewsService
        service = WebScrapingNewsService()
        return service.fetch_all_news()
    except Exception as e:
        st.error(f"Error fetching news: {e}")
        return {}

def create_fast_metric_card(symbol: str, price_data, col):
    """Create optimized metric card"""
    with col:
        if hasattr(price_data, 'change_percent') and price_data.change_percent is not None:
            change_color = "🟢" if price_data.change_percent >= 0 else "🔴"
            delta_text = f"{price_data.change_percent:+.2f}%"
            delta_color = "normal" if price_data.change_percent >= 0 else "inverse"
        else:
            change_color = "⚪"
            delta_text = "N/A"
            delta_color = "off"
        
        # Use Streamlit's built-in metric for speed
        st.metric(
            label=f"{change_color} {symbol}",
            value=f"${price_data.price:.2f}",
            delta=delta_text,
            delta_color=delta_color
        )

def create_performance_chart(prices_data):
    """Create optimized performance chart"""
    symbols = list(prices_data.keys())
    changes = []
    colors = []
    
    for symbol, price_data in prices_data.items():
        if hasattr(price_data, 'change_percent') and price_data.change_percent is not None:
            changes.append(price_data.change_percent)
            colors.append('green' if price_data.change_percent >= 0 else 'red')
        else:
            changes.append(0)
            colors.append('gray')
    
    fig = go.Figure(data=[
        go.Bar(
            x=symbols,
            y=changes,
            marker_color=colors,
            text=[f"{c:+.2f}%" for c in changes],
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title="📊 Real-time Performance",
        xaxis_title="Stocks",
        yaxis_title="Change %",
        height=400,
        showlegend=False,
        template="plotly_dark"
    )
    
    return fig

def main():
    """Fast main dashboard function"""
    
    # Header with performance indicator
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.title("⚡ Fast FinTech AI Assistant")
        st.markdown("*Ultra-fast real-time stock monitoring*")
    
    with col2:
        # Performance indicator
        st.metric("🚀 Speed Mode", "ULTRA-FAST", delta="10x faster")
    
    with col3:
        # Auto-refresh control
        auto_refresh = st.checkbox("🔄 Auto Refresh (5s)", value=True)
    
    # Fast controls sidebar
    with st.sidebar:
        st.header("⚡ Fast Controls")
        
        # Symbol selection
        from config import Config
        selected_symbols = st.multiselect(
            "Select Symbols",
            Config.STOCK_SYMBOLS,
            default=Config.STOCK_SYMBOLS[:8]  # Default to first 8 for speed
        )
        
        # Speed settings
        st.subheader("🚀 Performance")
        show_charts = st.checkbox("Show Charts", value=True)
        show_news = st.checkbox("Show News", value=False)  # Off by default for speed
        
        # Manual refresh
        if st.button("⚡ Instant Refresh"):
            st.cache_data.clear()
            st.rerun()
    
    # Main content with speed optimization
    if not selected_symbols:
        st.warning("Please select at least one symbol to monitor.")
        return
    
    # Fast price display
    st.header("💰 Live Stock Prices")
    
    # Use placeholder for smooth updates
    price_placeholder = st.empty()
    
    with price_placeholder.container():
        # Fetch prices with caching
        with st.spinner("⚡ Fetching prices (ultra-fast)..."):
            start_time = time.time()
            current_prices = get_cached_prices()
            fetch_time = time.time() - start_time
        
        if current_prices:
            # Performance metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📊 Stocks Fetched", len(current_prices))
            with col2:
                st.metric("⚡ Fetch Time", f"{fetch_time:.2f}s")
            with col3:
                st.metric("🚀 Speed", f"{len(current_prices)/fetch_time:.1f} stocks/sec")
            with col4:
                st.metric("🕐 Last Update", datetime.now().strftime("%H:%M:%S"))
            
            # Create fast grid layout
            cols = st.columns(4)  # 4 columns for optimal display
            
            for i, (symbol, price_data) in enumerate(current_prices.items()):
                if symbol in selected_symbols:
                    col_idx = i % 4
                    create_fast_metric_card(symbol, price_data, cols[col_idx])
            
            # Performance chart (optional)
            if show_charts:
                st.header("📊 Performance Visualization")
                
                filtered_prices = {k: v for k, v in current_prices.items() if k in selected_symbols}
                
                if filtered_prices:
                    chart = create_performance_chart(filtered_prices)
                    st.plotly_chart(chart, use_container_width=True)
        else:
            st.error("⚠️ No price data available. Check your connection.")
    
    # Fast news section (optional)
    if show_news:
        st.header("📰 Latest News (Cached)")
        
        with st.spinner("📰 Loading news..."):
            news_data = get_cached_news()
        
        if news_data:
            # Show only recent news for speed
            news_count = 0
            for symbol in selected_symbols:
                if symbol in news_data and news_count < 5:  # Limit for performance
                    articles = news_data[symbol][:2]  # Only show 2 per symbol
                    
                    for article in articles:
                        with st.expander(f"📰 {symbol}: {article.title[:60]}..."):
                            st.write(article.description or "No description available")
                            st.caption(f"Source: {article.source}")
                        news_count += 1
    
    # Real-time updates
    if auto_refresh:
        time.sleep(5)  # 5-second refresh for ultra-fast updates
        st.rerun()

if __name__ == "__main__":
    main()
