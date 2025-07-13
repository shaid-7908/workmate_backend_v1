from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import logging
from app.config.env_config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConnection:
    """MongoDB database connection manager."""
    
    def __init__(self):
        self.client: MongoClient[dict[str, object]] | None = None
        self.database: Database[dict[str, object]] | None = None
        self.config: Config = Config()
    
    def connect(self) -> bool:
        """
        Establish connection to MongoDB.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Create MongoDB client
            self.client = MongoClient(
                self.config.MONGODB_URL,
                serverSelectionTimeoutMS=5000
            )
            
            # Test the connection
            self.client.admin.command('ping')
            logger.info("MongoDB connected")
            
            # Get the database
            self.database = self.client[self.config.MONGODB_DB_NAME]
            logger.info(f"Connected to database: {self.config.MONGODB_DB_NAME}")
            
            return True
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"MongoDB connection error: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error connecting to MongoDB: {e}")
            return False
    
    def disconnect(self) -> None:
        """Close the MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB disconnected")
    
    def get_database(self) -> Database[dict[str, object]] | None:
        """
        Get the database instance.
        
        Returns:
            Database: MongoDB database instance or None if not connected
        """
        return self.database
    
    def get_collection(self, collection_name: str):
        """
        Get a collection from the database.
        
        Args:
            collection_name (str): Name of the collection
            
        Returns:
            Collection: MongoDB collection instance or None if not connected
        """
        database = self.get_database()
        if database is not None:
            return database[collection_name]
        return None

# Global database connection instance
db_connection = DatabaseConnection()

def connect_database() -> bool:
    """
    Connect to the database using the global connection instance.
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    return db_connection.connect()

def disconnect_database() -> None:
    """Disconnect the global database connection."""
    db_connection.disconnect()

def get_database() -> Database[dict[str, object]] | None:
    """
    Get the database instance from the global connection.
    
    Returns:
        Database: MongoDB database instance or None if not connected
    """
    return db_connection.get_database()

def get_collection(collection_name: str):
    """
    Get a collection from the global database connection.
    
    Args:
        collection_name (str): Name of the collection
        
    Returns:
        Collection: MongoDB collection instance or None if not connected
    """
    return db_connection.get_collection(collection_name)
