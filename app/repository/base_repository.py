from typing import Any, TypeVar, Generic
from app.config.db_connection import get_collection
from pydantic import BaseModel

# Generic type for any Pydantic model
T = TypeVar('T', bound=BaseModel)

class BaseRepository(Generic[T]):
    """Base repository that can work with any schema and collection name."""
    
    def __init__(self, schema_class: type[T]):
        """
        Initialize repository with a schema class.
        
        Args:
            schema_class: The Pydantic schema class with __collection_name__
        """
        self.schema_class = schema_class
        # Get collection name from schema (like Mongoose model)
        self.collection_name = getattr(schema_class, '__collection_name__', schema_class.__name__.lower())
    
    def _get_collection(self):
        """Get the collection when needed."""
        return get_collection(self.collection_name)
    
    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Create a new document in the database.
        
        Args:
            data: Document data to create
            
        Returns:
            dict: Created document with MongoDB _id
            
        Raises:
            Exception: If creation fails
        """
        try:
            collection = self._get_collection()
            if collection is None:
                raise Exception("Database collection not available")
            
            # Validate data using Pydantic schema
            schema_instance = self.schema_class(**data)
            
            # Convert to dict for MongoDB insertion
            document_dict = schema_instance.model_dump(exclude_none=True)
            
            # Remove _id if it exists (let MongoDB generate it)
            if "_id" in document_dict:
                del document_dict["_id"]
            
            # Insert into database
            result = collection.insert_one(document_dict)
            
            # Get the created document with _id
            created_document = collection.find_one({"_id": result.inserted_id})
            
            if created_document:
                # Convert ObjectId to string for JSON serialization
                created_document["_id"] = str(created_document["_id"])
                return created_document
            else:
                raise Exception("Failed to retrieve created document")
                
        except Exception as e:
            raise Exception(f"Failed to create document: {str(e)}")
    
    def get_by_id(self, document_id: str) -> dict[str, Any] | None:
        """
        Get a document by its MongoDB _id.
        
        Args:
            document_id (str): Document ID as string
            
        Returns:
            dict | None: Document data or None if not found
        """
        try:
            collection = self._get_collection()
            if collection is None:
                return None
            
            from bson import ObjectId
            # Convert string ID to ObjectId
            object_id = ObjectId(document_id)
            document = collection.find_one({"_id": object_id})
            
            if document:
                # Convert ObjectId to string for JSON serialization
                document["_id"] = str(document["_id"])
                return document
            return None
            
        except Exception as e:
            print(f"Error getting document by ID: {str(e)}")
            return None 