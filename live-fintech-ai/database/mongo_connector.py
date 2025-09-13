"""
Database Service for Live Fintech AI Assistant
Handles MongoDB operations for storing price movements, news, and explanations
"""

from pymongo import MongoClient, DESCENDING
from pymongo.errors import ConnectionFailure, OperationFailure
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from dataclasses import asdict
import json
from config import Config
from services.stock_service import StockPrice, PriceMovement
from services.news_service import NewsArticle
from services.llm_service import AIExplanation

class DatabaseService:
    """Service for MongoDB database operations"""
    
    def __init__(self):
        self.client = None
        self.db = None
        self.connect()
        
    def connect(self) -> bool:
        """
        Connect to MongoDB database
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.client = MongoClient(Config.MONGODB_URI, serverSelectionTimeoutMS=5000)
            
            # Test the connection
            self.client.admin.command('ismaster')
            
            self.db = self.client[Config.DB_NAME]
            
            # Create indexes for better performance
            self._create_indexes()
            
            print("✅ Connected to MongoDB successfully")
            return True
            
        except ConnectionFailure as e:
            print(f"❌ Failed to connect to MongoDB: {e}")
            return False
        except Exception as e:
            print(f"❌ Database connection error: {e}")
            return False
    
    def _create_indexes(self):
        """Create database indexes for better query performance"""
        try:
            # Price movements collection indexes
            price_movements = self.db[Config.COLLECTION_PRICE_MOVEMENTS]
            price_movements.create_index([("symbol", 1), ("timestamp", -1)])
            price_movements.create_index([("timestamp", -1)])
            
            # News collection indexes
            news_collection = self.db[Config.COLLECTION_NEWS]
            news_collection.create_index([("symbol", 1), ("published_at", -1)])
            news_collection.create_index([("published_at", -1)])
            
            # Explanations collection indexes
            explanations = self.db[Config.COLLECTION_EXPLANATIONS]
            explanations.create_index([("symbol", 1), ("timestamp", -1)])
            explanations.create_index([("timestamp", -1)])
            
            print("✅ Database indexes created")
            
        except Exception as e:
            print(f"⚠️ Warning: Could not create indexes: {e}")
    
    def store_price_movement(self, movement: PriceMovement) -> Optional[str]:
        """
        Store a price movement in the database
        
        Args:
            movement: PriceMovement object to store
            
        Returns:
            Document ID if successful, None otherwise
        """
        try:
            collection = self.db[Config.COLLECTION_PRICE_MOVEMENTS]
            
            doc = {
                "symbol": movement.symbol,
                "current_price": movement.current_price,
                "previous_price": movement.previous_price,
                "change_percent": movement.change_percent,
                "timestamp": movement.timestamp,
                "movement_type": movement.movement_type
            }
            
            result = collection.insert_one(doc)
            print(f"✅ Stored price movement for {movement.symbol}")
            return str(result.inserted_id)
            
        except Exception as e:
            print(f"❌ Error storing price movement: {e}")
            return None
    
    def store_news_articles(self, articles: List[NewsArticle]) -> List[str]:
        """
        Store news articles in the database
        
        Args:
            articles: List of NewsArticle objects to store
            
        Returns:
            List of document IDs
        """
        if not articles:
            return []
            
        try:
            collection = self.db[Config.COLLECTION_NEWS]
            
            docs = []
            for article in articles:
                doc = {
                    "title": article.title,
                    "description": article.description,
                    "url": article.url,
                    "published_at": article.published_at,
                    "source": article.source,
                    "symbol": article.symbol
                }
                docs.append(doc)
            
            result = collection.insert_many(docs)
            print(f"✅ Stored {len(articles)} news articles")
            return [str(id) for id in result.inserted_ids]
            
        except Exception as e:
            print(f"❌ Error storing news articles: {e}")
            return []
    
    def store_explanation(self, explanation: AIExplanation) -> Optional[str]:
        """
        Store an AI explanation in the database
        
        Args:
            explanation: AIExplanation object to store
            
        Returns:
            Document ID if successful, None otherwise
        """
        try:
            collection = self.db[Config.COLLECTION_EXPLANATIONS]
            
            # Convert news articles to simple dicts
            news_data = []
            for article in explanation.news_articles:
                news_data.append({
                    "title": article.title,
                    "url": article.url,
                    "source": article.source,
                    "published_at": article.published_at
                })
            
            doc = {
                "symbol": explanation.symbol,
                "explanation": explanation.explanation,
                "confidence_score": explanation.confidence_score,
                "timestamp": explanation.timestamp,
                "explanation_type": explanation.explanation_type,
                "price_movement": {
                    "current_price": explanation.price_movement.current_price,
                    "previous_price": explanation.price_movement.previous_price,
                    "change_percent": explanation.price_movement.change_percent,
                    "movement_type": explanation.price_movement.movement_type
                },
                "news_articles": news_data
            }
            
            result = collection.insert_one(doc)
            print(f"✅ Stored explanation for {explanation.symbol}")
            return str(result.inserted_id)
            
        except Exception as e:
            print(f"❌ Error storing explanation: {e}")
            return None
    
    def get_recent_movements(self, symbol: Optional[str] = None, hours: int = 24) -> List[Dict]:
        """
        Get recent price movements from the database
        
        Args:
            symbol: Stock symbol to filter by (optional)
            hours: Number of hours to look back
            
        Returns:
            List of price movement documents
        """
        try:
            collection = self.db[Config.COLLECTION_PRICE_MOVEMENTS]
            
            # Build query
            query = {"timestamp": {"$gte": datetime.now() - timedelta(hours=hours)}}
            if symbol:
                query["symbol"] = symbol
            
            cursor = collection.find(query).sort("timestamp", DESCENDING).limit(100)
            
            return list(cursor)
            
        except Exception as e:
            print(f"❌ Error fetching recent movements: {e}")
            return []
    
    def get_recent_explanations(self, symbol: Optional[str] = None, hours: int = 24) -> List[Dict]:
        """
        Get recent AI explanations from the database
        
        Args:
            symbol: Stock symbol to filter by (optional)
            hours: Number of hours to look back
            
        Returns:
            List of explanation documents
        """
        try:
            collection = self.db[Config.COLLECTION_EXPLANATIONS]
            
            # Build query
            query = {"timestamp": {"$gte": datetime.now() - timedelta(hours=hours)}}
            if symbol:
                query["symbol"] = symbol
            
            cursor = collection.find(query).sort("timestamp", DESCENDING).limit(50)
            
            return list(cursor)
            
        except Exception as e:
            print(f"❌ Error fetching recent explanations: {e}")
            return []
    
    def get_recent_news(self, symbol: Optional[str] = None, hours: int = 24) -> List[Dict]:
        """
        Get recent news articles from the database
        
        Args:
            symbol: Stock symbol to filter by (optional)
            hours: Number of hours to look back
            
        Returns:
            List of news article documents
        """
        try:
            collection = self.db[Config.COLLECTION_NEWS]
            
            # Build query
            query = {"published_at": {"$gte": datetime.now() - timedelta(hours=hours)}}
            if symbol:
                query["symbol"] = symbol
            
            cursor = collection.find(query).sort("published_at", DESCENDING).limit(100)
            
            return list(cursor)
            
        except Exception as e:
            print(f"❌ Error fetching recent news: {e}")
            return []
    
    def get_movement_statistics(self, symbol: str, days: int = 7) -> Dict[str, Any]:
        """
        Get movement statistics for a symbol
        
        Args:
            symbol: Stock symbol
            days: Number of days to analyze
            
        Returns:
            Dictionary with movement statistics
        """
        try:
            collection = self.db[Config.COLLECTION_PRICE_MOVEMENTS]
            
            # Build aggregation pipeline
            start_date = datetime.now() - timedelta(days=days)
            
            pipeline = [
                {
                    "$match": {
                        "symbol": symbol,
                        "timestamp": {"$gte": start_date}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total_movements": {"$sum": 1},
                        "avg_change_percent": {"$avg": "$change_percent"},
                        "max_change_percent": {"$max": "$change_percent"},
                        "min_change_percent": {"$min": "$change_percent"},
                        "up_movements": {
                            "$sum": {
                                "$cond": [{"$gt": ["$change_percent", 0]}, 1, 0]
                            }
                        },
                        "down_movements": {
                            "$sum": {
                                "$cond": [{"$lt": ["$change_percent", 0]}, 1, 0]
                            }
                        }
                    }
                }
            ]
            
            result = list(collection.aggregate(pipeline))
            
            if result:
                stats = result[0]
                del stats["_id"]
                return stats
            else:
                return {
                    "total_movements": 0,
                    "avg_change_percent": 0,
                    "max_change_percent": 0,
                    "min_change_percent": 0,
                    "up_movements": 0,
                    "down_movements": 0
                }
                
        except Exception as e:
            print(f"❌ Error calculating movement statistics: {e}")
            return {}
    
    def cleanup_old_data(self, days_to_keep: int = 30):
        """
        Clean up old data from the database
        
        Args:
            days_to_keep: Number of days of data to retain
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            # Clean up old price movements
            movements_result = self.db[Config.COLLECTION_PRICE_MOVEMENTS].delete_many(
                {"timestamp": {"$lt": cutoff_date}}
            )
            
            # Clean up old news
            news_result = self.db[Config.COLLECTION_NEWS].delete_many(
                {"published_at": {"$lt": cutoff_date}}
            )
            
            # Clean up old explanations
            explanations_result = self.db[Config.COLLECTION_EXPLANATIONS].delete_many(
                {"timestamp": {"$lt": cutoff_date}}
            )
            
            print(f"✅ Cleaned up old data:")
            print(f"   - {movements_result.deleted_count} price movements")
            print(f"   - {news_result.deleted_count} news articles")
            print(f"   - {explanations_result.deleted_count} explanations")
            
        except Exception as e:
            print(f"❌ Error cleaning up old data: {e}")
    
    def store_price_movement_data(self, movement_data: Dict) -> Optional[str]:
        """
        Store price movement data from Pathway pipeline
        
        Args:
            movement_data: Dictionary containing movement data
            
        Returns:
            Document ID if successful, None otherwise
        """
        try:
            collection = self.db[Config.COLLECTION_PRICE_MOVEMENTS]
            result = collection.insert_one(movement_data)
            return str(result.inserted_id)
        except Exception as e:
            print(f"❌ Error storing movement data: {e}")
            return None
    
    def store_explanation_data(self, explanation_data: Dict) -> Optional[str]:
        """
        Store explanation data from Pathway pipeline
        
        Args:
            explanation_data: Dictionary containing explanation data
            
        Returns:
            Document ID if successful, None otherwise
        """
        try:
            collection = self.db[Config.COLLECTION_EXPLANATIONS]
            result = collection.insert_one(explanation_data)
            return str(result.inserted_id)
        except Exception as e:
            print(f"❌ Error storing explanation data: {e}")
            return None
    
    def close(self):
        """Close the database connection"""
        if self.client:
            self.client.close()
            print("✅ Database connection closed")

# Test function
def test_database_service():
    """Test the database service functionality"""
    print("🧪 Testing Database Service...")
    
    db = DatabaseService()
    
    if not db.client:
        print("❌ Database connection failed, skipping tests")
        return
    
    # Test storing a mock price movement
    from services.stock_service import PriceMovement
    mock_movement = PriceMovement(
        symbol="TEST",
        current_price=100.0,
        previous_price=95.0,
        change_percent=5.26,
        timestamp=datetime.now(),
        movement_type="significant_up"
    )
    
    print("\n💾 Testing price movement storage:")
    movement_id = db.store_price_movement(mock_movement)
    if movement_id:
        print(f"✅ Stored movement with ID: {movement_id}")
    
    # Test fetching recent movements
    print("\n📊 Testing data retrieval:")
    recent_movements = db.get_recent_movements(hours=1)
    print(f"✅ Retrieved {len(recent_movements)} recent movements")
    
    # Test statistics
    print("\n📈 Testing statistics:")
    stats = db.get_movement_statistics("TEST", days=1)
    print(f"✅ Retrieved statistics: {stats}")
    
    db.close()

if __name__ == "__main__":
    test_database_service()
