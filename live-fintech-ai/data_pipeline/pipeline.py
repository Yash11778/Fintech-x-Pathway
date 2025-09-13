"""
Stream-based Data Pipeline for Live Fintech AI Assistant
Handles real-time stream processing for stock movements and news correlation
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import asdict
import json

from config import Config
from services.llm_service import LLMService
from database.mongo_connector import DatabaseService

# Import appropriate services based on configuration
if Config.DATA_SOURCE_MODE == 'webscraping':
    from services.web_stock_service import WebScrapingStockService as StockService, PriceMovement
    from services.web_news_service import WebScrapingNewsService as NewsService
else:
    from services.stock_service import StockService, PriceMovement
    from services.news_service import NewsService

class FinTechPipeline:
    """Main pipeline for processing financial data streams"""
    
    def __init__(self):
        self.stock_service = StockService()
        self.news_service = NewsService()
        self.llm_service = LLMService()
        self.db_service = DatabaseService()
        self.is_running = False
        
        # Pipeline state
        self.last_news_fetch = {}  # Track last news fetch time per symbol
        self.processing_queue = []
        
    async def start_pipeline(self):
        """Start the real-time processing pipeline"""
        print("🚀 Starting Live Fintech AI Pipeline...")
        
        # Validate configuration
        if not Config.validate_config():
            print("❌ Configuration validation failed. Please check your API keys.")
            return
        
        # Test database connection
        if not self.db_service.client:
            print("❌ Database connection failed. Please check MongoDB connection.")
            return
        
        self.is_running = True
        
        try:
            # Initial news fetch for all symbols
            await self._initial_news_fetch()
            
            # Start the main processing loop
            await self._run_processing_loop()
            
        except KeyboardInterrupt:
            print("\n🛑 Pipeline stopped by user")
        except Exception as e:
            print(f"❌ Pipeline error: {e}")
        finally:
            self.is_running = False
            self.db_service.close()
    
    async def _initial_news_fetch(self):
        """Fetch initial news for all symbols"""
        print("📰 Fetching initial news data...")
        
        try:
            all_news = self.news_service.fetch_all_news(hours_back=2)
            
            for symbol, articles in all_news.items():
                if articles:
                    # Store news in database
                    self.db_service.store_news_articles(articles)
                    self.last_news_fetch[symbol] = datetime.now()
                    
            print(f"✅ Initial news fetch completed for {len(all_news)} symbols")
            
        except Exception as e:
            print(f"❌ Error in initial news fetch: {e}")
    
    async def _run_processing_loop(self):
        """Main processing loop for the pipeline"""
        print("🔄 Starting main processing loop...")
        
        loop_count = 0
        
        while self.is_running:
            try:
                loop_start_time = time.time()
                loop_count += 1
                
                print(f"\n📊 Processing cycle {loop_count} - {datetime.now().strftime('%H:%M:%S')}")
                
                # Step 1: Fetch current stock prices
                current_prices = self.stock_service.fetch_all_prices()
                
                if not current_prices:
                    print("⚠️ No price data fetched, skipping cycle")
                    await asyncio.sleep(Config.REFRESH_INTERVAL_SECONDS)
                    continue
                
                # Step 2: Detect price movements
                movements = self.stock_service.detect_price_movements(current_prices)
                
                # Step 3: Process each significant movement
                if movements:
                    await self._process_movements(movements)
                else:
                    print("📈 No significant movements detected")
                
                # Step 4: Periodic news refresh (every 10 minutes)
                await self._periodic_news_refresh()
                
                # Step 5: Database cleanup (every 100 cycles)
                if loop_count % 100 == 0:
                    self.db_service.cleanup_old_data(days_to_keep=7)
                
                # Calculate sleep time to maintain consistent intervals
                processing_time = time.time() - loop_start_time
                sleep_time = max(0, Config.REFRESH_INTERVAL_SECONDS - processing_time)
                
                if sleep_time > 0:
                    print(f"⏱️ Cycle completed in {processing_time:.1f}s, sleeping for {sleep_time:.1f}s")
                    await asyncio.sleep(sleep_time)
                else:
                    print(f"⚠️ Cycle took {processing_time:.1f}s (longer than {Config.REFRESH_INTERVAL_SECONDS}s interval)")
                
            except Exception as e:
                print(f"❌ Error in processing loop: {e}")
                await asyncio.sleep(5)  # Short sleep before retrying
    
    async def _process_movements(self, movements: List[PriceMovement]):
        """Process detected price movements"""
        print(f"🚨 Processing {len(movements)} significant movements")
        
        for movement in movements:
            try:
                await self._process_single_movement(movement)
                
                # Add small delay between movements to avoid overwhelming APIs
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"❌ Error processing movement for {movement.symbol}: {e}")
    
    async def _process_single_movement(self, movement: PriceMovement):
        """Process a single price movement"""
        print(f"📊 Processing {movement.symbol} movement: {movement.change_percent:+.2f}%")
        
        # Step 1: Store the movement in database
        movement_id = self.db_service.store_price_movement(movement)
        
        # Step 2: Find relevant news articles
        relevant_news = self.news_service.find_relevant_news(
            movement.symbol,
            movement.timestamp,
            window_minutes=Config.NEWS_MATCHING_WINDOW_MINUTES
        )
        
        # Step 3: If no recent news found, fetch fresh news
        if not relevant_news:
            print(f"🔍 No cached news for {movement.symbol}, fetching fresh news...")
            fresh_news = self.news_service.fetch_news_for_symbol(movement.symbol, hours_back=1)
            
            if fresh_news:
                # Store fresh news and use for analysis
                self.db_service.store_news_articles(fresh_news)
                relevant_news = self.news_service.find_relevant_news(
                    movement.symbol,
                    movement.timestamp,
                    window_minutes=Config.NEWS_MATCHING_WINDOW_MINUTES
                )
        
        print(f"📰 Found {len(relevant_news)} relevant news articles for {movement.symbol}")
        
        # Step 4: Generate AI explanation
        explanation = self.llm_service.generate_movement_explanation(movement, relevant_news)
        
        # Step 5: Store the explanation
        explanation_id = self.db_service.store_explanation(explanation)
        
        print(f"🤖 Generated explanation for {movement.symbol}: {explanation.explanation[:50]}...")
        print(f"   Confidence: {explanation.confidence_score:.2f} | Type: {explanation.explanation_type}")
    
    async def _periodic_news_refresh(self):
        """Periodically refresh news data for all symbols"""
        current_time = datetime.now()
        
        for symbol in Config.STOCK_SYMBOLS:
            last_fetch = self.last_news_fetch.get(symbol, datetime.min)
            
            # Refresh news every 10 minutes per symbol
            if (current_time - last_fetch).total_seconds() > 600:  # 10 minutes
                try:
                    print(f"🔄 Refreshing news for {symbol}")
                    articles = self.news_service.fetch_news_for_symbol(symbol, hours_back=1)
                    
                    if articles:
                        self.db_service.store_news_articles(articles)
                    
                    self.last_news_fetch[symbol] = current_time
                    
                    # Add delay to respect API limits
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    print(f"❌ Error refreshing news for {symbol}: {e}")
    
    def stop_pipeline(self):
        """Stop the pipeline gracefully"""
        print("🛑 Stopping pipeline...")
        self.is_running = False
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get current pipeline status"""
        return {
            "is_running": self.is_running,
            "symbols_tracked": Config.STOCK_SYMBOLS,
            "last_news_fetch": {
                symbol: fetch_time.isoformat() if fetch_time != datetime.min else None
                for symbol, fetch_time in self.last_news_fetch.items()
            },
            "database_connected": self.db_service.client is not None,
            "processing_queue_size": len(self.processing_queue)
        }
    
    def get_recent_activity(self, hours: int = 1) -> Dict[str, Any]:
        """Get recent pipeline activity"""
        try:
            recent_movements = self.db_service.get_recent_movements(hours=hours)
            recent_explanations = self.db_service.get_recent_explanations(hours=hours)
            recent_news = self.db_service.get_recent_news(hours=hours)
            
            return {
                "movements_count": len(recent_movements),
                "explanations_count": len(recent_explanations),
                "news_count": len(recent_news),
                "recent_movements": recent_movements[:5],  # Latest 5 movements
                "recent_explanations": recent_explanations[:5],  # Latest 5 explanations
            }
            
        except Exception as e:
            print(f"❌ Error getting recent activity: {e}")
            return {}

# Real-time stream processor (Pathway-inspired)
class PathwayInspiredProcessor:
    """Real-time financial data processor inspired by Pathway concepts"""
    
    def __init__(self):
        self.stock_service = StockService()
        self.news_service = NewsService()
        self.llm_service = LLMService()
        self.db_service = DatabaseService()
        self.is_running = False
        
    def fetch_price_stream(self):
        """Fetch current stock prices as a stream-like data structure"""
        try:
            prices = self.stock_service.fetch_all_prices()
            
            # Convert to stream-like format
            price_stream = []
            for symbol, price_obj in prices.items():
                price_stream.append({
                    'symbol': symbol,
                    'price': price_obj.price,
                    'change_percent': price_obj.change_percent or 0.0,
                    'timestamp': price_obj.timestamp,
                    'volume': price_obj.volume or 0
                })
            
            return price_stream
        except Exception as e:
            print(f"❌ Error fetching price stream: {e}")
            return []
    
    def fetch_news_stream(self):
        """Fetch news data as a stream-like data structure"""
        try:
            all_news = self.news_service.fetch_all_news()
            
            # Convert to stream-like format
            news_stream = []
            for symbol, articles in all_news.items():
                for article in articles:
                    news_stream.append({
                        'symbol': symbol,
                        'title': article.title,
                        'description': article.description or '',
                        'url': article.url,
                        'source': article.source,
                        'timestamp': article.published_at,
                        'sentiment_score': getattr(article, 'sentiment_score', 0.0)
                    })
            
            return news_stream
        except Exception as e:
            print(f"❌ Error fetching news stream: {e}")
            return []
    
    def detect_significant_movements(self, price_stream):
        """Detect significant price movements from the price stream"""
        significant_movements = []
        
        for price_data in price_stream:
            if abs(price_data['change_percent']) >= Config.PRICE_MOVEMENT_THRESHOLD_PERCENT:
                significant_movements.append(price_data)
        
        return significant_movements
    
    def correlate_with_news(self, movements, news_stream):
        """Correlate price movements with news within time window"""
        correlation_window = Config.NEWS_MATCHING_WINDOW_MINUTES * 60  # Convert to seconds
        correlated_data = []
        
        for movement in movements:
            # Find related news for this symbol
            related_news = []
            for news in news_stream:
                if (news['symbol'] == movement['symbol'] and 
                    abs((movement['timestamp'] - news['timestamp']).total_seconds()) <= correlation_window):
                    related_news.append(news)
            
            # Create correlated record
            correlated_record = movement.copy()
            correlated_record['related_news'] = related_news
            correlated_data.append(correlated_record)
        
        return correlated_data
    
    def generate_explanations(self, correlated_data):
        """Generate AI explanations for correlated movements and news"""
        explained_data = []
        
        for record in correlated_data:
            try:
                # Create mock objects for the LLM service
                class MockMovement:
                    def __init__(self, data):
                        self.symbol = data['symbol']
                        self.current_price = data['price']
                        self.previous_price = data['price'] * (1 - data['change_percent'] / 100)  # Calculate previous price
                        self.change_percent = data['change_percent']
                        self.timestamp = data['timestamp']
                        self.movement_type = "significant_up" if data['change_percent'] > 0 else "significant_down"
                
                class MockNews:
                    def __init__(self, news_data):
                        self.title = news_data['title']
                        self.description = news_data['description']
                        self.url = news_data['url']
                        self.source = news_data['source']
                        self.published_at = news_data['timestamp']
                
                movement = MockMovement(record)
                news = [MockNews(news) for news in record['related_news']]
                
                explanation = self.llm_service.generate_movement_explanation(movement, news)
                
                record['explanation'] = explanation.explanation
                record['confidence_score'] = explanation.confidence_score
                explained_data.append(record)
                
            except Exception as e:
                print(f"❌ Error generating explanation for {record['symbol']}: {e}")
                record['explanation'] = f"Error generating explanation: {str(e)}"
                record['confidence_score'] = 0.0
                explained_data.append(record)
        
        return explained_data
    
    def store_processed_data(self, explained_data):
        """Store processed data to database"""
        for record in explained_data:
            try:
                # Store movement data
                movement_data = {
                    'symbol': record['symbol'],
                    'current_price': record['price'],
                    'change_percent': record['change_percent'],
                    'timestamp': record['timestamp'],
                    'movement_type': "significant_up" if record['change_percent'] > 0 else "significant_down"
                }
                
                # Store explanation data
                explanation_data = {
                    'symbol': record['symbol'],
                    'explanation': record['explanation'],
                    'timestamp': record['timestamp'],
                    'explanation_type': 'stream_processed',
                    'confidence_score': record.get('confidence_score', 0.8)
                }
                
                # Store in database
                self.db_service.store_price_movement_data(movement_data)
                self.db_service.store_explanation_data(explanation_data)
                
                print(f"💾 Stored data for {record['symbol']}: {record['change_percent']:+.2f}%")
                
            except Exception as e:
                print(f"❌ Error storing data for {record['symbol']}: {e}")
    
    def run_processing_cycle(self):
        """Run a single processing cycle"""
        print(f"📊 Running processing cycle - {datetime.now().strftime('%H:%M:%S')}")
        
        # Step 1: Fetch price stream
        price_stream = self.fetch_price_stream()
        if not price_stream:
            print("⚠️ No price data available")
            return
        
        # Step 2: Detect significant movements
        movements = self.detect_significant_movements(price_stream)
        if not movements:
            print("� No significant movements detected")
            return
        
        print(f"🚨 Found {len(movements)} significant movements")
        
        # Step 3: Fetch news stream
        news_stream = self.fetch_news_stream()
        
        # Step 4: Correlate with news
        correlated_data = self.correlate_with_news(movements, news_stream)
        
        # Step 5: Generate AI explanations
        explained_data = self.generate_explanations(correlated_data)
        
        # Step 6: Store processed data
        self.store_processed_data(explained_data)
        
        print(f"✅ Processing cycle complete - processed {len(explained_data)} movements")
    
    async def start_stream_processing(self):
        """Start the stream processing loop"""
        print("🚀 Starting stream processing...")
        self.is_running = True
        
        cycle_count = 0
        
        while self.is_running:
            try:
                cycle_count += 1
                print(f"\n🔄 Cycle {cycle_count}")
                
                # Run processing cycle
                self.run_processing_cycle()
                
                # Wait for next cycle
                await asyncio.sleep(Config.REFRESH_INTERVAL_SECONDS)
                
            except Exception as e:
                print(f"❌ Error in processing cycle: {e}")
                await asyncio.sleep(5)  # Short sleep before retrying
    
    def stop_processing(self):
        """Stop the stream processing"""
        print("🛑 Stopping stream processing...")
        self.is_running = False

# Factory functions for creating pipeline instances
def create_fintech_pipeline() -> FinTechPipeline:
    """Create and configure a new FinTech pipeline instance (legacy async version)"""
    return FinTechPipeline()

def create_stream_processor() -> PathwayInspiredProcessor:
    """Create and configure a new stream processor"""
    return PathwayInspiredProcessor()

# Main execution functions
async def run_legacy_pipeline():
    """Run the legacy async pipeline"""
    pipeline = create_fintech_pipeline()
    
    try:
        await pipeline.start_pipeline()
    except KeyboardInterrupt:
        print("\n🛑 Pipeline interrupted by user")
    finally:
        pipeline.stop_pipeline()

async def run_pathway_pipeline():
    """Run the stream processing pipeline"""
    print("🚀 Starting Stream-based FinTech AI Pipeline...")
    
    # Validate configuration
    if not Config.validate_config():
        print("❌ Configuration validation failed. Please check your API keys.")
        return
    
    try:
        # Create stream processor
        processor = create_stream_processor()
        
        print("✅ Stream processor created successfully!")
        print("📊 Processing real-time financial data streams...")
        print("   - Stock prices updating every {} seconds".format(Config.REFRESH_INTERVAL_SECONDS))
        print("   - AI explanations generated for significant movements")
        print("\n🔄 Pipeline is running... Press Ctrl+C to stop")
        
        # Run the stream processing
        await processor.start_stream_processing()
        
    except KeyboardInterrupt:
        print("\n🛑 Stream pipeline interrupted by user")
    except Exception as e:
        print(f"❌ Stream pipeline error: {e}")
        raise

def run_hybrid_pipeline():
    """Run both legacy and Pathway pipelines in parallel"""
    import threading
    
    print("🚀 Starting Hybrid FinTech AI Pipeline (Legacy + Pathway)...")
    
    # Function to run legacy pipeline in thread
    def run_legacy_thread():
        asyncio.run(run_legacy_pipeline())
    
    # Start legacy pipeline in background thread
    legacy_thread = threading.Thread(target=run_legacy_thread, daemon=True)
    legacy_thread.start()
    
    # Run Pathway pipeline in main thread
    run_pathway_pipeline()

if __name__ == "__main__":
    import sys
    
    # Check command line arguments for pipeline type
    pipeline_type = sys.argv[1] if len(sys.argv) > 1 else "pathway"
    
    if pipeline_type == "legacy":
        asyncio.run(run_legacy_pipeline())
    elif pipeline_type == "hybrid":
        run_hybrid_pipeline()
    else:  # Default to pathway
        run_pathway_pipeline()
