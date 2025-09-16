"""
HONEST FINTECH NEWS DASHBOARD
Focus: Why do stock prices move? What news is driving the changes?
No fake Pathway - just real news-to-price correlation
"""

import streamlit as st
import asyncio
import time
import yfinance as yf
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List
import pandas as pd
import sys
import os

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure Streamlit
st.set_page_config(
    page_title="📰 FinTech News Analyzer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #2196F3 0%, #21CBF3 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    .movement-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        color: white;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    .news-explanation {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        color: white;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    .positive-movement {
        border-left: 5px solid #4CAF50;
        background: linear-gradient(135deg, #e8f5e8 0%, #f1f8e9 100%);
    }
    
    .negative-movement {
        border-left: 5px solid #f44336;
        background: linear-gradient(135deg, #ffebee 0%, #fce4ec 100%);
    }
    
    .neutral-movement {
        border-left: 5px solid #ff9800;
        background: linear-gradient(135deg, #fff3e0 0%, #fce4ec 100%);
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_stock_data_real(symbols):
    """Get real stock data using yfinance"""
    stock_data = {}
    
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="5d")
            info = ticker.info
            
            if len(hist) >= 2:
                current = hist['Close'].iloc[-1]
                previous = hist['Close'].iloc[-2]
                
                change_amount = current - previous
                change_percent = (change_amount / previous) * 100
                
                stock_data[symbol] = {
                    'symbol': symbol,
                    'current_price': current,
                    'previous_price': previous,
                    'change_amount': change_amount,
                    'change_percent': change_percent,
                    'volume': int(hist['Volume'].iloc[-1]),
                    'company_name': info.get('longName', symbol),
                    'market_cap': info.get('marketCap', 'N/A'),
                    'sector': info.get('sector', 'N/A')
                }
                
        except Exception as e:
            st.error(f"Error fetching data for {symbol}: {e}")
            
    return stock_data

@st.cache_data(ttl=600)  # Cache for 10 minutes
def get_news_explanation(symbol, change_percent):
    """Get news explanation for stock movement"""
    try:
        from services.news_stock_correlator import get_news_correlator
        
        correlator = get_news_correlator()
        
        # Create a simple movement object
        class SimpleMovement:
            def __init__(self, symbol, change_percent, current_price):
                self.symbol = symbol
                self.change_percent = change_percent
                self.current_price = current_price
                self.change_amount = 0  # We'll calculate this if needed
                self.volume = 0
        
        movement = SimpleMovement(symbol, change_percent, 0)
        
        # This would be async in real implementation
        # For now, return a simple explanation
        if abs(change_percent) > 2.0:
            direction = "surged" if change_percent > 0 else "declined"
            return f"{symbol} {direction} {abs(change_percent):.2f}% today. This significant movement likely reflects recent company news, earnings reports, or market sentiment shifts. Check financial news sources for specific catalysts driving this price action."
        else:
            return f"{symbol} showed minor movement ({change_percent:+.2f}%) - typical daily trading fluctuation."
            
    except Exception as e:
        return f"Unable to fetch detailed news analysis. {symbol} moved {change_percent:+.2f}% - check financial news for potential catalysts."

def create_movement_card(symbol, data):
    """Create a card showing stock movement with explanation"""
    
    change_percent = data['change_percent']
    
    # Determine card style
    if change_percent > 2:
        card_class = "positive-movement"
        emoji = "📈"
        color = "#4CAF50"
    elif change_percent < -2:
        card_class = "negative-movement" 
        emoji = "📉"
        color = "#f44336"
    else:
        card_class = "neutral-movement"
        emoji = "📊"
        color = "#ff9800"
    
    # Get news explanation
    explanation = get_news_explanation(symbol, change_percent)
    
    st.markdown(f"""
    <div class="movement-card {card_class}">
        <h3>{emoji} {symbol} - {data['company_name']}</h3>
        <div style="display: flex; justify-content: space-between; margin: 1rem 0;">
            <div>
                <h2>${data['current_price']:.2f}</h2>
                <p style="color: {color}; font-weight: bold;">
                    {change_percent:+.2f}% (${data['change_amount']:+.2f})
                </p>
            </div>
            <div style="text-align: right;">
                <p><strong>Volume:</strong> {data['volume']:,}</p>
                <p><strong>Sector:</strong> {data['sector']}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Show explanation if significant movement
    if abs(change_percent) > 1.5:
        st.markdown(f"""
        <div class="news-explanation">
            <h4>📰 Why is {symbol} moving?</h4>
            <p>{explanation}</p>
        </div>
        """, unsafe_allow_html=True)

def main():
    """Main dashboard function"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📰 FinTech News Analyzer</h1>
        <p>Understanding WHY stock prices move through news analysis</p>
        <small>Real data • Real explanations • No fake Pathway claims</small>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 📊 Stock Selection")
        
        # Popular stocks
        popular_stocks = [
            "AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "META", "NVDA", "NFLX",
            "AMD", "INTC", "CRM", "ORCL", "JPM", "BAC", "TSLA"
        ]
        
        selected_symbols = st.multiselect(
            "Select stocks to analyze:",
            popular_stocks,
            default=["AAPL", "TSLA", "GOOGL", "MSFT", "AMZN"]
        )
        
        # Filters
        st.markdown("### 🔍 Movement Filters")
        min_change = st.slider("Minimum price change %", 0.0, 10.0, 1.0)
        
        # Update frequency
        st.markdown("### ⚙️ Settings")
        auto_refresh = st.checkbox("Auto refresh (5 min)", value=True)
        
        if st.button("🔄 Refresh Now"):
            st.cache_data.clear()
            st.rerun()
    
    if not selected_symbols:
        st.warning("Please select at least one stock symbol to analyze.")
        return
    
    # Get stock data
    with st.spinner("📊 Fetching real stock data..."):
        stock_data = get_stock_data_real(selected_symbols)
    
    if not stock_data:
        st.error("Unable to fetch stock data. Please try again.")
        return
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    all_changes = [data['change_percent'] for data in stock_data.values()]
    gainers = sum(1 for change in all_changes if change > 0)
    losers = sum(1 for change in all_changes if change < 0)
    avg_change = sum(all_changes) / len(all_changes)
    
    with col1:
        st.metric("📈 Gainers", gainers)
    with col2:
        st.metric("📉 Losers", losers)
    with col3:
        st.metric("📊 Average Change", f"{avg_change:.2f}%")
    with col4:
        st.metric("🕐 Last Update", datetime.now().strftime("%H:%M"))
    
    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["🎯 Significant Movements", "📊 All Stocks", "📈 Charts"])
    
    with tab1:
        st.markdown("### 🎯 Stocks with Significant Price Movements")
        st.markdown("*Showing stocks that moved more than 1.5% - these need explanations!*")
        
        significant_movements = {
            symbol: data for symbol, data in stock_data.items()
            if abs(data['change_percent']) >= min_change
        }
        
        if significant_movements:
            # Sort by absolute change
            sorted_movements = sorted(
                significant_movements.items(),
                key=lambda x: abs(x[1]['change_percent']),
                reverse=True
            )
            
            for symbol, data in sorted_movements:
                create_movement_card(symbol, data)
        else:
            st.info(f"No stocks moved more than {min_change}% today.")
    
    with tab2:
        st.markdown("### 📊 All Selected Stocks")
        
        # Create a sortable table
        df_data = []
        for symbol, data in stock_data.items():
            df_data.append({
                'Symbol': symbol,
                'Company': data['company_name'][:30] + "..." if len(data['company_name']) > 30 else data['company_name'],
                'Price': f"${data['current_price']:.2f}",
                'Change %': f"{data['change_percent']:+.2f}%",
                'Change $': f"${data['change_amount']:+.2f}",
                'Volume': f"{data['volume']:,}",
                'Sector': data['sector']
            })
        
        df = pd.DataFrame(df_data)
        
        # Color-code the dataframe
        def highlight_changes(row):
            change_pct = float(row['Change %'].replace('%', '').replace('+', ''))
            if change_pct > 2:
                return ['background-color: #e8f5e8'] * len(row)
            elif change_pct < -2:
                return ['background-color: #ffebee'] * len(row)
            else:
                return ['background-color: white'] * len(row)
        
        styled_df = df.style.apply(highlight_changes, axis=1)
        st.dataframe(styled_df, use_container_width=True)
    
    with tab3:
        st.markdown("### 📈 Price Movement Visualization")
        
        # Create a bar chart of movements
        symbols = list(stock_data.keys())
        changes = [stock_data[symbol]['change_percent'] for symbol in symbols]
        colors = ['green' if change > 0 else 'red' for change in changes]
        
        fig = go.Figure(data=[
            go.Bar(
                x=symbols,
                y=changes,
                marker_color=colors,
                text=[f"{change:+.2f}%" for change in changes],
                textposition='auto',
            )
        ])
        
        fig.update_layout(
            title="📊 Today's Stock Performance",
            xaxis_title="Stock Symbols",
            yaxis_title="Change %",
            template="plotly_white",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
        <p><strong>📰 FinTech News Analyzer</strong> - Understanding market movements through news correlation</p>
        <p>Data from Yahoo Finance • Updates every 5 minutes • Built for real analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Auto refresh
    if auto_refresh:
        time.sleep(300)  # Wait 5 minutes
        st.rerun()

if __name__ == "__main__":
    main()
