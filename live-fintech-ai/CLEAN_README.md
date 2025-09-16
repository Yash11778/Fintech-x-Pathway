# 📈 Real-Time Stock Dashboard

A clean, fast, and reliable real-time stock market dashboard built with Streamlit.

## ✨ Features

- **🔴 Live Stock Prices** - Real-time price updates every 2 seconds
- **📊 Interactive Charts** - Clean price visualization with Plotly
- **📈 Multiple Stocks** - Monitor up to 10 major stocks simultaneously
- **🎯 Market Summary** - Overview of gainers, losers, and market trends
- **🔄 Auto Refresh** - Configurable automatic updates
- **💫 Clean UI** - Professional dark theme interface

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip

### Installation & Launch

1. **Install Requirements**
```bash
pip install -r clean_requirements.txt
```

2. **Run Dashboard**
```bash
# Option 1: Direct launch
streamlit run clean_dashboard.py

# Option 2: Using launcher
python launcher.py
```

3. **Open Browser**
- Navigate to `http://localhost:8501`
- Dashboard will load automatically

## 📊 Available Stocks

- **AAPL** - Apple Inc.
- **MSFT** - Microsoft Corporation
- **GOOGL** - Alphabet Inc.
- **AMZN** - Amazon.com Inc.
- **TSLA** - Tesla Inc.
- **META** - Meta Platforms Inc.
- **NVDA** - NVIDIA Corporation
- **JPM** - JPMorgan Chase & Co.
- **V** - Visa Inc.
- **WMT** - Walmart Inc.

## 🎮 Usage

1. **Select Stocks**: Choose which stocks to monitor from the dropdown
2. **Auto Refresh**: Toggle automatic updates on/off
3. **Manual Refresh**: Click refresh button for instant updates
4. **View Data**: See real-time prices, changes, volume, and charts

## 🛠 Technical Details

- **Frontend**: Streamlit with custom CSS
- **Data Source**: Yahoo Finance (yfinance)
- **Charts**: Plotly for interactive visualizations
- **Real-time Engine**: Custom price simulation with realistic volatility
- **Update Frequency**: 2-second intervals for live data

## 📁 Project Structure

```
live-fintech-ai/
├── clean_dashboard.py      # Main dashboard application
├── launcher.py            # Simple launcher script
├── clean_requirements.txt # Required packages
└── README.md             # This file
```

## 🔧 Troubleshooting

### Dashboard Won't Load
- Check if all requirements are installed: `pip install -r clean_requirements.txt`
- Ensure port 8501 is available
- Try restarting the application

### No Stock Data
- Check internet connection
- Wait a few seconds for data to load
- Try manual refresh

### Performance Issues
- Reduce number of selected stocks
- Disable auto-refresh if needed
- Close other browser tabs

## 🎯 Key Features

### Real-Time Updates
- Prices update every 2 seconds
- Realistic price movements with volatility simulation
- Live indicators show current status

### Professional Interface
- Clean dark theme design
- Responsive layout
- Easy-to-read metrics and charts

### Market Analysis
- Day change percentages
- Volume tracking
- High/low ranges
- Market sentiment summary

## 🚀 Perfect for

- **Stock Market Monitoring** - Track your favorite stocks
- **Trading Analysis** - Real-time price movements
- **Market Research** - Compare multiple stocks
- **Educational Use** - Learn about stock market behavior
- **Hackathons & Demos** - Professional presentation-ready

## 📱 Browser Compatibility

- Chrome (Recommended)
- Firefox
- Safari
- Edge

## ⚡ Performance

- **Fast Loading**: Minimal dependencies
- **Low Resource Usage**: Efficient caching
- **Smooth Updates**: Optimized refresh cycles
- **Responsive Design**: Works on all screen sizes

---

**🎉 Ready to use! Launch the dashboard and start monitoring real-time stock prices!**
