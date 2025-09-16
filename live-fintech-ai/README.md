# � Live Fintech AI™ - Real-Time Trading Co-Pilot

> **AI-Powered Streaming Intelligence Platform for Financial Markets**  
> Continuously learns from market movements with real-time anomaly detection and portfolio insights

![Live AI](https://img.shields.io/badge/Live%20AI-Powered-brightgreen?style=for-the-badge) ![Streaming](https://img.shields.io/badge/Streaming%20Data-Real--Time-blue?style=for-the-badge) ![Pathway](https://img.shields.io/badge/Pathway-Powered-orange?style=for-the-badge)

---

## 🎯 What is Live Fintech AI™?

**Live Fintech AI™** is a sophisticated AI-powered fintech solution that provides real-time market analysis, anomaly detection, and portfolio management through continuous streaming data processing. Built for the **Live Fintech AI Challenge**, it combines cutting-edge AI with real-time data streams to deliver intelligent trading insights.

## � Key Features

- **Robust Web Scraping**: Multi-source price extraction (Yahoo Finance, Google Finance, MarketWatch, Investing.com)
- **Financial News Aggregation**: Real-time news from Reuters, Yahoo Finance, MarketWatch, CNN Business, Bloomberg
- **AI-Powered Analysis**: Get intelligent explanations for significant movements
- **Interactive Dashboard**: Modern Streamlit interface with live updates and charts
- **Anti-Blocking Technology**: User-agent rotation and intelligent request handling
- **Smart Error Recovery**: Automatic fallbacks ensure 90%+ uptime reliability
- **Historical Data**: Track and visualize price trends over time
- **Production-Ready Architecture**: Comprehensive error handling and loggingh AI Assistant

A real-time financial analysis system that tracks stock movements, correlates them with breaking news, and provides AI-powered explanations. Built for hackathons and live trading environments.

![Python](https://img.shields.io/badge/python-v3.9+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-hackathon--ready-brightgreen.svg)

## 🚀 Features

- **�️ Web Scraping Mode**: No API keys needed! Scrapes Yahoo Finance, Google Finance, etc.
- **�📊 Live Stock Tracking**: Real-time price monitoring for AAPL, TSLA, MSFT
- **🤖 AI Explanations**: OpenAI-powered analysis of price movements
- **📰 News Correlation**: Automatic matching of stock moves with breaking news
- **🔄 Stream Processing**: Pathway-based real-time data pipeline
- **📈 Interactive Dashboard**: Beautiful Streamlit interface
- **💾 Historical Storage**: MongoDB for storing movements and explanations
- **⚡ Real-time Alerts**: Instant notifications for significant movements (>2%)
- **🔑 Dual Mode**: Choose between web scraping (hackathon-friendly) or API mode

## 🏗️ Architecture

```
live-fintech-ai/
├── data_pipeline/          # Pathway stream processing
│   ├── __init__.py
│   └── pipeline.py         # Main data pipeline
├── services/               # API integrations
│   ├── __init__.py
│   ├── stock_service.py    # AlphaVantage API
│   ├── news_service.py     # NewsAPI integration
│   └── llm_service.py      # OpenAI API
├── database/               # Data persistence
│   ├── __init__.py
│   └── mongo_connector.py  # MongoDB operations
├── frontend/               # Web interface
│   └── dashboard.py        # Streamlit dashboard
├── config.py               # Configuration management
├── main.py                 # System orchestrator
├── requirements.txt        # Python dependencies
└── .env.template           # Environment variables template
```

## 🛠️ Quick Setup (WSL Ubuntu)

### 1. Prerequisites

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.9+ and pip
sudo apt install python3 python3-pip python3-venv -y

# Install MongoDB (optional, for local development)
sudo apt install mongodb -y
sudo systemctl start mongodb
sudo systemctl enable mongodb
```

### 2. Clone and Setup

```bash
# Clone the project
git clone <repository-url>
cd live-fintech-ai

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure the System

```bash
# Run interactive setup wizard
python main.py --setup
```

**🕷️ Web Scraping Mode (Recommended for Hackathons)**
- Only requires **OpenAI API key**
- Stock data scraped from Yahoo Finance, Google Finance
- News scraped from multiple financial sources
- **No registration needed** for stock/news APIs

**🔑 API Mode (More Reliable)**
- Requires 3 API keys: AlphaVantage, NewsAPI, OpenAI
- More reliable and faster data
- Better for production use

**API Keys (if needed):**
- **OpenAI**: Get key at [platform.openai.com](https://platform.openai.com/api-keys) (Required for both modes)
- **AlphaVantage**: Get free key at [alphavantage.co](https://www.alphavantage.co/support/#api-key) (API mode only)
- **NewsAPI**: Get free key at [newsapi.org](https://newsapi.org/register) (API mode only)

### 4. Start the System

```bash
# Full system (pipeline + dashboard)
python main.py

# Or individual components
python main.py --mode pipeline    # Data pipeline only
python main.py --mode dashboard   # Dashboard only
python main.py --mode test        # Run tests
```

### 5. Access Dashboard

Open your browser and go to: **http://localhost:8501**

## 📱 Dashboard Features

### Real-time Overview
- **Current Prices**: Live stock prices with change indicators
- **Movement Alerts**: Instant notifications for significant changes
- **AI Explanations**: Natural language analysis of price movements
- **News Feed**: Breaking financial news correlated with movements

### Interactive Controls
- **Symbol Selection**: Choose which stocks to monitor
- **Time Range**: Adjust historical data view (1-24 hours)
- **Auto Refresh**: Configurable refresh intervals (10-120 seconds)
- **Manual Refresh**: On-demand data updates

### Analytics
- **Movement Statistics**: Historical analysis of price changes
- **Confidence Scores**: AI explanation reliability metrics
- **News Correlation**: Links between price moves and news events
- **Price History Charts**: Interactive time series visualization

## 🔧 Configuration Options

### Environment Variables (.env)

```bash
# Required API Keys
ALPHA_VANTAGE_API_KEY=your_key_here
NEWSAPI_KEY=your_key_here
OPENAI_API_KEY=your_key_here

# Database (optional)
MONGODB_URI=mongodb://localhost:27017/

# System Settings (optional)
PRICE_MOVEMENT_THRESHOLD_PERCENT=2.0
NEWS_MATCHING_WINDOW_MINUTES=5
REFRESH_INTERVAL_SECONDS=30
```

### Stock Symbols

Edit `config.py` to modify tracked symbols:

```python
STOCK_SYMBOLS = ['AAPL', 'TSLA', 'MSFT', 'GOOGL', 'AMZN']
```

## 🔍 How It Works

### 1. Data Collection
- **Stock Prices**: Fetched every 30 seconds from AlphaVantage
- **News Articles**: Retrieved from NewsAPI with financial focus
- **Price History**: Stored locally for movement detection

### 2. Movement Detection
- Compares current price with 5-minute historical average
- Triggers alerts for changes exceeding 2% threshold
- Categorizes movements as "significant_up" or "significant_down"

### 3. News Correlation
- Searches for news articles within 5-minute window of price movement
- Matches articles by symbol and company name
- Filters by financial news sources (Reuters, Bloomberg, etc.)

### 4. AI Analysis
- OpenAI GPT-3.5/4 generates explanations for movements
- Considers available news context and market patterns
- Provides confidence scores based on available information
- Identifies unusual movements without clear news catalysts

### 5. Storage & Visualization
- MongoDB stores all movements, news, and explanations
- Streamlit dashboard provides real-time visualization
- Historical analysis and statistics tracking

## 🧪 Testing

```bash
# Run all system tests
python main.py --mode test

# Check configuration
python main.py --config-check

# Test individual services
cd services
python stock_service.py      # Test stock API
python news_service.py       # Test news API
python llm_service.py        # Test OpenAI API

cd ../database
python mongo_connector.py    # Test database
```

## 📊 Data Sources & Usage

### 🕷️ Web Scraping Mode (Default)
- **Stock Prices**: Yahoo Finance, Google Finance, MarketWatch
- **News**: Multiple financial news sources (Yahoo Finance, CNN Business, etc.)
- **Rate Limits**: Natural delays (1-3 seconds between requests)
- **Reliability**: Generally good, but may occasionally fail due to website changes
- **Cost**: Free (only OpenAI API costs for explanations)

### 🔑 API Mode (Optional)
**AlphaVantage (Free Tier)**
- **Limit**: 5 API requests per minute, 500 per day
- **Usage**: ~180 requests/hour for 3 symbols
- **Upgrade**: Premium plans available for higher limits

**NewsAPI (Free Tier)**
- **Limit**: 1,000 requests per day
- **Usage**: ~50 requests/hour for news fetching
- **Upgrade**: Paid plans for production use

**OpenAI (Pay-per-use) - Required for both modes**
- **Model**: GPT-3.5-turbo (default) or GPT-4
- **Cost**: ~$0.002 per explanation (GPT-3.5)
- **Usage**: Only triggered on significant movements

## 🎯 Why Web Scraping Mode?

**Perfect for Hackathons Because:**
- ✅ **No API Registration**: Start coding immediately
- ✅ **No Rate Limits**: Works reliably during demos
- ✅ **No Costs**: Only pay for OpenAI (explanations)
- ✅ **Real Data**: Gets actual live stock prices and news
- ✅ **Multiple Sources**: Falls back to different websites if one fails

**Data Sources Used:**
- **Stock Prices**: Yahoo Finance → MarketWatch → Google Finance (fallback chain)
- **Financial News**: Yahoo Finance News, CNN Business, MarketWatch
- **Company Mapping**: Smart keyword matching (Apple, AAPL, iPhone for AAPL)

## 🚨 Troubleshooting

### Common Issues

**1. Configuration Errors**
```bash
❌ Missing required API key: OPENAI_API_KEY
```
**Solution**: Run `python main.py --setup` and choose web scraping mode

**2. Database Connection**
```bash
❌ Failed to connect to MongoDB
```
**Solution**: Install and start MongoDB:
```bash
sudo systemctl start mongodb
```

**3. Web Scraping Failures**
```bash
❌ Could not find price for AAPL on Yahoo Finance
```
**Solution**: The system automatically tries multiple sources. Occasional failures are normal.

**4. Import Errors**
```bash
ModuleNotFoundError: No module named 'beautifulsoup4'
```
**Solution**: Install web scraping dependencies:
```bash
pip install beautifulsoup4 lxml html5lib requests
```

### Debug Mode

```bash
# Enable verbose logging
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python -m pdb main.py --mode test
```

## 🎯 Hackathon Demo Tips

### Quick Demo Script (5 minutes)

1. **Show Live Dashboard** (1 min)
   - Open http://localhost:8501
   - Point out real-time prices and auto-refresh

2. **Trigger Movement Detection** (2 min)
   - Wait for natural movement or simulate with test data
   - Show AI explanation generation

3. **Explain Architecture** (1 min)
   - Show modular code structure
   - Highlight stream processing with Pathway

4. **Show Historical Analysis** (1 min)
   - Navigate to statistics section
   - Display price history charts

### Demo Data Generation

```bash
# Generate test movements for demo
python -c "
from services.stock_service import StockService, PriceMovement
from datetime import datetime
import time

service = StockService()

# Simulate price movements
mock_movement = PriceMovement(
    symbol='DEMO',
    current_price=150.0,
    previous_price=145.0,
    change_percent=3.45,
    timestamp=datetime.now(),
    movement_type='significant_up'
)

print('Demo movement created!')
"
```

## 📈 Future Enhancements

### Immediate (Hackathon Extensions)
- [ ] Portfolio-based alerts and tracking
- [ ] Sanctions list compliance checking
- [ ] WhatsApp/Telegram notifications
- [ ] Multi-timeframe analysis (1min, 5min, 15min)

### Medium-term
- [ ] Technical indicator integration (RSI, MA, MACD)
- [ ] Sentiment analysis of news articles
- [ ] Social media monitoring (Twitter, Reddit)
- [ ] Custom alerting rules engine

### Long-term
- [ ] Machine learning prediction models
- [ ] Options and derivatives tracking
- [ ] International market coverage
- [ ] Real-time collaboration features

## 🤝 Contributing

This is a hackathon project! Feel free to:

1. **Fork the repository**
2. **Add new features** (see Future Enhancements)
3. **Fix bugs** or improve performance
4. **Submit pull requests**

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt
pip install black flake8 mypy pytest

# Code formatting
black .

# Linting
flake8 .

# Type checking
mypy .

# Testing
pytest
```

## 📄 License

MIT License - feel free to use this project for hackathons, learning, or commercial purposes.

## 🙏 Acknowledgments

- **Pathway** for stream processing capabilities
- **AlphaVantage** for stock market data
- **NewsAPI** for real-time news feeds
- **OpenAI** for AI-powered explanations
- **Streamlit** for rapid dashboard development

## 📞 Support

For hackathon support or questions:

- Check the **Troubleshooting** section above
- Run `python main.py --mode test` to diagnose issues
- Create GitHub issues for bugs or feature requests

---

**Built with ❤️ for hackathons and live trading analysis**

*Happy coding! 🚀*
