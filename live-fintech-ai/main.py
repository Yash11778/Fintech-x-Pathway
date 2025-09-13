"""
Main Entry Point for Live Fintech AI Assistant
Orchestrates the entire system and provides CLI interface
"""

import asyncio
import argparse
import sys
import signal
import os
from datetime import datetime
from typing import Optional

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from data_pipeline.pipeline import FinTechPipeline
from services.stock_service import StockService
from services.news_service import NewsService
from services.llm_service import LLMService
from database.mongo_connector import DatabaseService

class FinTechAISystem:
    """Main system orchestrator for Live Fintech AI Assistant"""
    
    def __init__(self):
        self.pipeline = None
        self.is_running = False
        
    async def start_system(self, mode: str = "full"):
        """
        Start the Live Fintech AI system
        
        Args:
            mode: System mode - 'full', 'pipeline', 'dashboard', 'test'
        """
        print("🚀 Starting Live Fintech AI Assistant...")
        print(f"   Mode: {mode}")
        print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Symbols: {', '.join(Config.STOCK_SYMBOLS)}")
        
        # Validate configuration
        if not Config.validate_config():
            print("\n❌ System startup failed due to configuration errors.")
            print("Please check your .env file and ensure all required API keys are set.")
            return False
        
        try:
            if mode == "full":
                await self._start_full_system()
            elif mode == "pipeline":
                await self._start_pipeline_only()
            elif mode == "pathway":
                await self._start_pathway_pipeline()
            elif mode == "fast-pathway":
                await self._start_fast_pathway_pipeline()
            elif mode == "dashboard":
                self._start_dashboard_only()
            elif mode == "fast-dashboard":
                self._start_fast_dashboard()
            elif mode == "beautiful-dashboard" or mode == "beautiful":
                self._start_beautiful_dashboard()
            elif mode == "test":
                await self._run_tests()
            else:
                print(f"❌ Unknown mode: {mode}")
                return False
                
        except KeyboardInterrupt:
            print("\n🛑 System interrupted by user")
        except Exception as e:
            print(f"\n❌ System error: {e}")
            return False
        finally:
            await self._shutdown()
        
        return True
    
    async def _start_full_system(self):
        """Start both pipeline and dashboard"""
        print("\n🔄 Starting full system (pipeline + dashboard)...")
        
        # Start pipeline in background
        self.pipeline = FinTechPipeline()
        pipeline_task = asyncio.create_task(self.pipeline.start_pipeline())
        
        # Start dashboard (this will block)
        print("\n📊 Starting dashboard...")
        print("🌐 Dashboard will be available at: http://localhost:8501")
        print("💡 To stop the system, press Ctrl+C")
        
        # Run both concurrently
        try:
            await asyncio.gather(
                pipeline_task,
                self._start_dashboard_async()
            )
        except asyncio.CancelledError:
            print("🛑 Full system cancelled")
    
    async def _start_pipeline_only(self):
        """Start only the data pipeline"""
        print("\n🔄 Starting pipeline only...")
        
        self.pipeline = FinTechPipeline()
        await self.pipeline.start_pipeline()
    
    async def _start_pathway_pipeline(self):
        """Start the Pathway-based pipeline"""
        print("\n🚀 Starting Pathway-based pipeline...")
        
        # Import pathway pipeline
        from data_pipeline.pipeline import run_pathway_pipeline
        
        # Run pathway pipeline (this is async)
        await run_pathway_pipeline()
    
    async def _start_fast_pathway_pipeline(self):
        """Start the Fast Pathway-based pipeline"""
        print("\n⚡ Starting Fast Pathway-based pipeline...")
        
        # Import fast pathway pipeline
        from services.pathway_processor import run_fast_pathway_pipeline
        
        # Run fast pathway pipeline
        await run_fast_pathway_pipeline()
    
    def _start_dashboard_only(self):
        """Start only the Streamlit dashboard"""
        print("\n📊 Starting dashboard only...")
        print("🌐 Dashboard will be available at: http://localhost:8501")
        
        import subprocess
        import sys
        
        # Run streamlit
        dashboard_path = os.path.join(os.path.dirname(__file__), 'frontend', 'dashboard.py')
        
        try:
            subprocess.run([
                sys.executable, '-m', 'streamlit', 'run', dashboard_path,
                '--server.port', str(Config.STREAMLIT_PORT),
                '--server.headless', 'true'
            ])
        except KeyboardInterrupt:
            print("\n🛑 Dashboard stopped")
    
    def _start_fast_dashboard(self):
        """Start the fast optimized dashboard"""
        print("\n⚡ Starting Fast Dashboard...")
        print("🚀 Ultra-fast dashboard will be available at: http://localhost:8501")
        
        import subprocess
        import sys
        
        # Run fast streamlit dashboard
        dashboard_path = os.path.join(os.path.dirname(__file__), 'frontend', 'fast_dashboard.py')
        
        try:
            subprocess.run([
                sys.executable, '-m', 'streamlit', 'run', dashboard_path,
                '--server.port', str(Config.STREAMLIT_PORT),
                '--server.headless', 'true',
                '--server.runOnSave', 'true'
            ])
        except KeyboardInterrupt:
            print("\n🛑 Fast Dashboard stopped")
    
    def _start_beautiful_dashboard(self):
        """Start the beautiful enhanced dashboard"""
        print("\n✨ Starting Beautiful Dashboard...")
        print("💎 Enhanced dashboard with news section will be available at: http://localhost:8501")
        print("🔥 Features: Ultra-fast updates, comprehensive news, AI insights, beautiful UI")
        
        import subprocess
        import sys
        
        # Run beautiful streamlit dashboard
        dashboard_path = os.path.join(os.path.dirname(__file__), 'frontend', 'beautiful_dashboard.py')
        
        try:
            subprocess.run([
                sys.executable, '-m', 'streamlit', 'run', dashboard_path,
                '--server.port', str(Config.STREAMLIT_PORT),
                '--server.headless', 'true',
                '--server.runOnSave', 'true'
            ])
        except KeyboardInterrupt:
            print("\n🛑 Beautiful Dashboard stopped")
    
    async def _start_dashboard_async(self):
        """Start dashboard asynchronously"""
        import subprocess
        import sys
        
        dashboard_path = os.path.join(os.path.dirname(__file__), 'frontend', 'dashboard.py')
        
        process = await asyncio.create_subprocess_exec(
            sys.executable, '-m', 'streamlit', 'run', dashboard_path,
            '--server.port', str(Config.STREAMLIT_PORT),
            '--server.headless', 'true'
        )
        
        await process.wait()
    
    async def _run_tests(self):
        """Run system tests"""
        print("\n🧪 Running system tests...")
        
        # Test configuration
        print("\n1️⃣ Testing configuration...")
        config_valid = Config.validate_config()
        if config_valid:
            print("✅ Configuration test passed")
        else:
            print("❌ Configuration test failed")
            return
        
        # Test database connection
        print("\n2️⃣ Testing database connection...")
        db_service = DatabaseService()
        if db_service.client:
            print("✅ Database connection test passed")
            db_service.close()
        else:
            print("❌ Database connection test failed")
            return
        
        # Test stock service
        print("\n3️⃣ Testing stock service...")
        try:
            # Import appropriate service based on configuration
            if Config.DATA_SOURCE_MODE == 'webscraping':
                from services.web_stock_service import WebScrapingStockService as StockService
                print("   Using web scraping mode...")
            else:
                from services.stock_service import StockService
                print("   Using API mode...")
            
            stock_service = StockService()
            price = stock_service.fetch_current_price("AAPL")
            if price:
                print(f"✅ Stock service test passed (AAPL: ${price.price:.2f})")
            else:
                print("❌ Stock service test failed")
        except Exception as e:
            print(f"❌ Stock service test failed: {e}")
        
        # Test news service
        print("\n4️⃣ Testing news service...")
        try:
            # Import appropriate service based on configuration
            if Config.DATA_SOURCE_MODE == 'webscraping':
                from services.web_news_service import WebScrapingNewsService as NewsService
                print("   Using web scraping mode...")
            else:
                from services.news_service import NewsService
                print("   Using API mode...")
            
            news_service = NewsService()
            news = news_service.fetch_news_for_symbol("AAPL", hours_back=1)
            print(f"✅ News service test passed ({len(news)} articles found)")
        except Exception as e:
            print(f"❌ News service test failed: {e}")
        
        # Test LLM service
        print("\n5️⃣ Testing LLM service...")
        try:
            from services.stock_service import PriceMovement
            from services.news_service import NewsArticle
            
            llm_service = LLMService()
            
            # Create mock data
            mock_movement = PriceMovement(
                symbol="TEST",
                current_price=100.0,
                previous_price=95.0,
                change_percent=5.26,
                timestamp=datetime.now(),
                movement_type="significant_up"
            )
            
            mock_news = [NewsArticle(
                title="Test News",
                description="Test description",
                url="https://example.com",
                published_at=datetime.now(),
                source="Test Source"
            )]
            
            explanation = llm_service.generate_movement_explanation(mock_movement, mock_news)
            print(f"✅ LLM service test passed (confidence: {explanation.confidence_score:.2f})")
            
        except Exception as e:
            print(f"❌ LLM service test failed: {e}")
        
        print("\n🎉 System tests completed!")
    
    async def _shutdown(self):
        """Shutdown the system gracefully"""
        print("\n🔄 Shutting down system...")
        
        if self.pipeline:
            self.pipeline.stop_pipeline()
        
        print("✅ System shutdown complete")

def setup_signal_handlers(system: FinTechAISystem):
    """Setup signal handlers for graceful shutdown (Windows compatible)"""
    def signal_handler(signum, frame):
        print(f"\n🛑 Received signal {signum}")
        try:
            # For Windows compatibility, handle shutdown directly
            system.is_running = False
            if hasattr(system, 'pipeline') and system.pipeline:
                system.pipeline.stop_pipeline()
        except Exception as e:
            print(f"Error during shutdown: {e}")
        finally:
            sys.exit(0)
    
    try:
        # Only set up signal handlers if we're in the main thread
        signal.signal(signal.SIGINT, signal_handler)
        if hasattr(signal, 'SIGTERM'):  # SIGTERM may not be available on Windows
            signal.signal(signal.SIGTERM, signal_handler)
        print("✅ Signal handlers setup successfully")
    except ValueError as e:
        print(f"⚠️ Signal handling not available (running in thread): {e}")
        # Continue without signal handlers in multi-threaded environments

def create_cli_parser():
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description="Live Fintech AI Assistant - Real-time stock movement explanations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                          # Start beautiful dashboard (✨ NEW DEFAULT!)
  python main.py --mode beautiful         # Start beautiful dashboard with enhanced news UI
  python main.py --mode fast-dashboard    # Start ultra-fast dashboard (⚡ FAST)
  python main.py --mode fast-pathway      # Start ULTRA-FAST Pathway pipeline (⚡ RECOMMENDED)
  python main.py --mode full              # Start full system (pipeline + dashboard)
  python main.py --mode pipeline          # Start only the data pipeline (legacy async)
  python main.py --mode pathway           # Start only the Pathway-based pipeline
  python main.py --mode dashboard         # Start only the dashboard  
  python main.py --mode test              # Run system tests
  python main.py --setup                  # Setup wizard for configuration
        """
    )
    
    parser.add_argument(
        '--mode',
        choices=['full', 'pipeline', 'pathway', 'dashboard', 'fast-dashboard', 'beautiful-dashboard', 'beautiful', 'fast-pathway', 'test'],
        default='beautiful-dashboard',
        help='System operation mode (default: beautiful-dashboard)'
    )
    
    parser.add_argument(
        '--setup',
        action='store_true',
        help='Run setup wizard for initial configuration'
    )
    
    parser.add_argument(
        '--config-check',
        action='store_true',
        help='Check configuration and exit'
    )
    
    return parser

def run_setup_wizard():
    """Run interactive setup wizard"""
    print("🧙 Live Fintech AI Assistant Setup Wizard")
    print("=" * 50)
    
    # Check if .env file exists
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    
    if os.path.exists(env_file):
        print("📁 Found existing .env file")
        overwrite = input("Do you want to overwrite it? (y/N): ")
        if overwrite.lower() != 'y':
            print("Setup cancelled")
            return
    
    print("\n� Choose your setup mode:")
    print("1. 🕷️  Web Scraping Mode (Recommended for hackathons)")
    print("   - No API keys needed for stock/news data")
    print("   - Only requires OpenAI API key")
    print("   - Scrapes Yahoo Finance, Google Finance, etc.")
    print()
    print("2. 🔑 API Mode (More reliable but requires multiple API keys)")
    print("   - Uses AlphaVantage API for stock data")
    print("   - Uses NewsAPI for news data")
    print("   - Requires 3 API keys total")
    print()
    
    while True:
        choice = input("Enter your choice (1 or 2): ").strip()
        if choice in ['1', '2']:
            break
        print("Please enter 1 or 2")
    
    if choice == '1':
        # Web scraping mode
        print("\n📝 Web Scraping Mode Setup:")
        print("You only need an OpenAI API key for AI explanations.")
        print("Stock prices and news will be scraped from free sources.")
        
        openai_key = input("\nOpenAI API Key: ").strip()
        mongodb_uri = input("MongoDB URI (press Enter for localhost): ").strip()
        
        if not mongodb_uri:
            mongodb_uri = "mongodb://localhost:27017/"
        
        env_content = f"""# Live Fintech AI Assistant - Web Scraping Mode
DATA_SOURCE_MODE=webscraping
OPENAI_API_KEY={openai_key}
MONGODB_URI={mongodb_uri}
"""
        
        print("\n✅ Web scraping mode configured!")
        print("   - Stock data: Yahoo Finance (web scraping)")
        print("   - News data: Multiple sources (web scraping)")
        print("   - AI explanations: OpenAI API")
        
    else:
        # API mode
        print("\n📝 API Mode Setup:")
        print("You need API keys from AlphaVantage, NewsAPI, and OpenAI.")
        
        alpha_vantage_key = input("\nAlphaVantage API Key: ").strip()
        newsapi_key = input("NewsAPI Key: ").strip()
        openai_key = input("OpenAI API Key: ").strip()
        mongodb_uri = input("MongoDB URI (press Enter for localhost): ").strip()
        
        if not mongodb_uri:
            mongodb_uri = "mongodb://localhost:27017/"
        
        env_content = f"""# Live Fintech AI Assistant - API Mode
DATA_SOURCE_MODE=api
ALPHA_VANTAGE_API_KEY={alpha_vantage_key}
NEWSAPI_KEY={newsapi_key}
OPENAI_API_KEY={openai_key}
MONGODB_URI={mongodb_uri}
"""
        
        print("\n✅ API mode configured!")
        print("   - Stock data: AlphaVantage API")
        print("   - News data: NewsAPI")
        print("   - AI explanations: OpenAI API")
    
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print(f"\n💾 Configuration saved to {env_file}")
    print("🚀 You can now run the system with: python main.py")

async def main():
    """Main function"""
    parser = create_cli_parser()
    args = parser.parse_args()
    
    # Handle special commands
    if args.setup:
        run_setup_wizard()
        return
    
    if args.config_check:
        print("🔍 Checking configuration...")
        if Config.validate_config():
            print("✅ Configuration is valid")
            return
        else:
            print("❌ Configuration has errors")
            print("💡 Run 'python main.py --setup' to configure API keys")
            sys.exit(1)
    
    # Create and start system
    system = FinTechAISystem()
    setup_signal_handlers(system)
    
    success = await system.start_system(args.mode)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 System interrupted")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
