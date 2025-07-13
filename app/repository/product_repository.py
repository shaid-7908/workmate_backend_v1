from bson import ObjectId
from typing import TypedDict,Any
from app.config.db_connection import get_collection
from app.model.product_schema import ProductSchema
from app.types.product_types import ProductCreateSchema

# Type for MongoDB document with string _id
class MongoDocument(TypedDict, total=False):
    _id: str
    productId: int
    title: str
    variants: list[dict[str, object]]
    vendor: str
    tags: list[str]
    createdAt: str
    updatedAt: str

class ProductRepository:
    """Repository for product operations."""
    
    def __init__(self):
        # Get collection name from schema (like Mongoose model)
        self.collection_name: str = ProductSchema.__collection_name__
    
    def _get_collection(self):
        """Get the collection when needed."""
        return get_collection(self.collection_name)
    
    def create_product(self, product_data: ProductCreateSchema) -> dict[str, object]:
        """
        Create a new product in the database.
        
        Args:
            product_data (ProductCreateSchema): Product data to create
            
        Returns:
            dict: Created product with MongoDB _id
            
        Raises:
            Exception: If product creation fails
        """
        try:
            collection = self._get_collection()
            if collection is None:
                raise Exception("Database collection not available")
            
            # Convert ProductCreateSchema to dict for ProductSchema
            product_dict = product_data.model_dump()
            
            # Validate product data using Pydantic schema
            # type: ignore[reportArgumentType] - data is already validated by ProductCreateSchema
            product_schema = ProductSchema(**product_dict)
            
            # Convert to dict for MongoDB insertion
            product_dict = product_schema.model_dump(exclude_none=True)
            
            # Remove _id if it exists (let MongoDB generate it)
            if "_id" in product_dict:
                del product_dict["_id"]
            
            # Insert into database
            result = collection.insert_one(product_dict)
            
            # Get the created product with _id
            created_product = collection.find_one({"_id": result.inserted_id})
            
            if created_product:
                # Convert ObjectId to string for JSON serialization
                created_product["_id"] = str(created_product["_id"])
                return created_product
            else:
                raise Exception("Failed to retrieve created product")
                
        except Exception as e:
            raise Exception(f"Failed to create product: {str(e)}")
    
    def create_product_with_schema(self, product: ProductSchema) -> dict[str, object]:
        """
        Create a new product using ProductSchema instance.
        
        Args:
            product (ProductSchema): Product schema instance
            
        Returns:
            dict: Created product with MongoDB _id
            
        Raises:
            Exception: If product creation fails
        """
        try:
            collection = self._get_collection()
            if collection is None:
                raise Exception("Database collection not available")
            
            # Convert schema to dict for MongoDB insertion
            product_dict = product.model_dump(exclude_none=True)
            
            # Remove _id if it exists (let MongoDB generate it)
            if "_id" in product_dict:
                del product_dict["_id"]
            
            # Insert into database
            result = collection.insert_one(product_dict)
            
            # Get the created product with _id
            created_product = collection.find_one({"_id": result.inserted_id})
            
            if created_product:
                # Convert ObjectId to string for JSON serialization
                created_product["_id"] = str(created_product["_id"])
                return created_product
            else:
                raise Exception("Failed to retrieve created product")
                
        except Exception as e:
            raise Exception(f"Failed to create product: {str(e)}")
    
    def get_product_by_id(self, product_id: str) -> dict[str, object] | None:
        """
        Get a product by its MongoDB _id.
        
        Args:
            product_id (str): Product ID as string
            
        Returns:
            dict | None: Product data or None if not found
        """
        try:
            collection = self._get_collection()
            if collection is None:
                return None
            
            # Convert string ID to ObjectId
            object_id = ObjectId(product_id)
            product = collection.find_one({"_id": object_id})
            
            if product:
                # Convert ObjectId to string for JSON serialization
                product["_id"] = str(product["_id"])
                return product
            return None
            
        except Exception as e:
            print(f"Error getting product by ID: {str(e)}")
            return None
    
    def get_products_by_store(self, store_id: str) -> list[dict[str, object]]:
        """
        Get all products for a specific store.
        
        Args:
            store_id (str): Store ID as string
            
        Returns:
            list[dict]: List of products for the store
        """
        try:
            collection = self._get_collection()
            if collection is None:
                return []
            
            # Convert string ID to ObjectId
            object_id = ObjectId(store_id)
            products = list(collection.find({"storeId": object_id}))
            
            # Convert ObjectIds to strings for JSON serialization
            for product in products:
                product["_id"] = str(product["_id"])
                if "storeId" in product:
                    product["storeId"] = str(product["storeId"])
            
            return products
            
        except Exception as e:
            print(f"Error getting products by store: {str(e)}")
            return []
