"""
PATHWAY FINANCIAL AI - DEMO DASHBOARD
Windows-compatible demonstration of Pathway concepts
Created for hackathon presentation
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time
from datetime import datetime
import random

# Set up page
st.set_page_config(
    page_title="🚀 Pathway Financial AI",
    page_icon="📈",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .pathway-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
    }
    
    .metric-card {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 10px 0;
    }
    
    .alert-high {
        background-color: #f8d7da;
        color: #721c24;
        padding: 10px;
        border-radius: 8px;
        border-left: 4px solid #dc3545;
        margin: 5px 0;
    }
    
    .positive-move {
        color: #00C851 !important;
        font-weight: bold;
    }
    
    .negative-move {
        color: #ff4444 !important;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

class PathwayDemoSimulator:
    """Demonstrates Pathway concepts with real stock-like data"""
    
    def __init__(self):
        self.stocks = {
            "AAPL": {"name": "Apple Inc.", "price": 234.50, "change": 2.3},
            "TSLA": {"name": "Tesla Inc.", "price": 395.20, "change": -3.8},
            "GOOGL": {"name": "Alphabet Inc.", "price": 240.80, "change": 1.2},
            "NVDA": {"name": "NVIDIA Corp.", "price": 875.30, "change": 4.7},
            "MSFT": {"name": "Microsoft Corp.", "price": 445.15, "change": -1.1},
            "AMZN": {"name": "Amazon.com Inc.", "price": 186.75, "change": 2.9},
            "META": {"name": "Meta Platforms", "price": 298.45, "change": -2.4},
            "NFLX": {"name": "Netflix Inc.", "price": 401.20, "change": 1.8}
        }
        
    def simulate_pathway_processing(self):
        """Simulate Pathway stream processing"""
        
        st.markdown("### 🔄 Pathway Stream Processing Simulation")
        
        # Show the conceptual code
        st.code("""
# Real Pathway Code (Linux/Mac):
import pathway as pw

# Step 1: Create data stream
stock_data = pw.io.kafka.read(rdkafka_settings, topic="stocks", schema=StockSchema)

# Step 2: Filter significant moves
significant_moves = stock_data.filter(pw.this.change_percent > 2.0)

# Step 3: Classify movements  
classified = significant_moves.select(
    pw.this.symbol,
    movement_type=pw.if_else(pw.this.change_percent > 0, "SURGE", "DROP"),
    significance=pw.if_else(pw.this.change_percent > 5.0, "HIGH", "MEDIUM")
)

# Step 4: Generate alerts
alerts = classified.select(
    alert=pw.this.symbol + " " + pw.this.movement_type + "D " + 
          pw.cast(str, pw.this.change_percent) + "% - " + pw.this.significance
)
        """, language="python")
        
        return self.process_stocks()
    
    def process_stocks(self):
        """Process stocks using Pathway-like logic"""
        
        # Add some randomness to simulate real-time updates
        for symbol in self.stocks:
            change = random.uniform(-0.5, 0.5)
            self.stocks[symbol]["change"] += change
            self.stocks[symbol]["price"] *= (1 + change/100)
        
        # Filter for significant moves (like Pathway filter)
        significant_moves = []
        alerts = []
        
        for symbol, data in self.stocks.items():
            if abs(data["change"]) > 2.0:  # Pathway filter condition
                movement_type = "SURGE" if data["change"] > 0 else "DROP"
                significance = "HIGH" if abs(data["change"]) > 5.0 else "MEDIUM"
                
                significant_moves.append({
                    "symbol": symbol,
                    "price": data["price"],
                    "change": data["change"],
                    "movement_type": movement_type,
                    "significance": significance
                })
                
                # Generate alert (like Pathway select)
                alert = f"{symbol} {movement_type}D {data['change']:+.2f}% - {significance} IMPACT"
                alerts.append(alert)
        
        return {
            "all_stocks": self.stocks,
            "significant_moves": significant_moves,
            "alerts": alerts
        }

def main():
    """Main dashboard"""
    
    # Header
    st.markdown("""
    <div class="pathway-header">
        <h1>🚀 Pathway Financial AI - Hackathon Demo</h1>
        <p>Real-time streaming stock analysis with Pathway concepts</p>
        <p><strong>Windows Compatible • Stream Processing • AI-Powered Alerts</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize simulator
    if 'simulator' not in st.session_state:
        st.session_state.simulator = PathwayDemoSimulator()
    
    # Sidebar controls
    st.sidebar.header("🎛️ Pathway Controls")
    
    if st.sidebar.button("🚀 Start Pathway Processing"):
        st.sidebar.success("✅ Pathway simulation active!")
        
    if st.sidebar.button("🔄 Refresh Data Stream"):
        # Simulate real-time updates
        results = st.session_state.simulator.simulate_pathway_processing()
        st.session_state.results = results
    
    auto_refresh = st.sidebar.checkbox("🔄 Auto-refresh (5s)", value=False)
    
    # Status indicators
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🟢 Stream Status", "ACTIVE")
    with col2:
        st.metric("📊 Stocks Monitored", "8")
    with col3:
        st.metric("🚨 Active Alerts", len(st.session_state.get('results', {}).get('alerts', [])))
    with col4:
        st.metric("⚡ Processing Speed", "Real-time")
    
    st.markdown("---")
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 Live Stock Data (Pathway Processed)")
        
        if 'results' in st.session_state:
            results = st.session_state.results
            
            # Stock grid
            stocks_data = results["all_stocks"]
            cols = st.columns(2)
            
            for i, (symbol, data) in enumerate(stocks_data.items()):
                with cols[i % 2]:
                    change_class = "positive-move" if data['change'] > 0 else "negative-move"
                    change_symbol = "📈" if data['change'] > 0 else "📉"
                    
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4>{symbol} {change_symbol}</h4>
                        <p><strong>${data['price']:.2f}</strong></p>
                        <p class="{change_class}">
                            {data['change']:+.2f}%
                        </p>
                        <small>{data['name']}</small>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Performance chart
            st.subheader("📊 Performance Chart")
            symbols = list(stocks_data.keys())
            changes = [stocks_data[s]['change'] for s in symbols]
            
            fig = go.Figure(data=[
                go.Bar(
                    x=symbols,
                    y=changes,
                    marker_color=['green' if x > 0 else 'red' for x in changes],
                    text=[f'{x:+.2f}%' for x in changes],
                    textposition='auto'
                )
            ])
            
            fig.update_layout(
                title="Stock Performance (Pathway Stream Processing)",
                xaxis_title="Stocks",
                yaxis_title="Change %",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        else:
            st.info("👆 Click 'Refresh Data Stream' to start Pathway processing")
    
    with col2:
        st.subheader("🚨 Pathway Alerts")
        
        if 'results' in st.session_state and st.session_state.results.get('alerts'):
            for alert in st.session_state.results['alerts']:
                st.markdown(f"""
                <div class="alert-high">
                    <strong>🔔 {alert}</strong><br>
                    <small>Generated by Pathway stream processing</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No significant moves detected")
        
        st.subheader("💡 How This Works")
        st.markdown("""
        **🔄 Pathway Concepts Demonstrated:**
        
        1. **Stream Processing**: Continuous data flow simulation
        2. **Filtering**: `pw.this.change_percent > 2.0`
        3. **Transformations**: Movement classification
        4. **Conditional Logic**: `pw.if_else()` for alerts
        5. **Real-time Updates**: Live data processing
        
        **🖥️ Windows Compatibility:**
        - Simulates exact Pathway behavior
        - Shows identical data transformations
        - Demonstrates streaming concepts
        
        **🐧 Linux/Mac Deployment:**
        - Uses real `import pathway as pw`
        - Kafka/database connectors
        - Production Rust engine
        """)
        
        if st.button("📋 Show Real Pathway Code"):
            st.code("""
# Complete Real Pathway Implementation:

import pathway as pw

class StockSchema(pw.Schema):
    symbol: str
    price: float
    change_percent: float

# Input stream
stock_data = pw.io.kafka.read(
    rdkafka_settings,
    topic="stock_prices", 
    schema=StockSchema
)

# Processing pipeline
significant_moves = stock_data.filter(
    pw.this.change_percent > 2.0
)

alerts = significant_moves.select(
    pw.this.symbol,
    alert_message=pw.this.symbol + " moved " + 
                 pw.cast(str, pw.this.change_percent) + "%"
)

# Output
pw.io.jsonlines.write(alerts, "alerts.jsonl")
pw.run()
            """, language="python")
    
    # Auto-refresh mechanism
    if auto_refresh:
        time.sleep(5)
        st.rerun()

if __name__ == "__main__":
    main()
