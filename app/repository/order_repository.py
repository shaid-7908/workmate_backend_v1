from bson import ObjectId
from typing import TypedDict
from app.config.db_connection import get_collection
from app.model.order_schema import OrderSchema
from datetime import datetime

# Type for MongoDB document with string _id
class OrderDocument(TypedDict, total=False):
    _id: str
    order_id: int
    order_number: int
    name: str
    created_at: str
    processed_at: str | None
    updated_at: str
    financial_status: str
    fulfillment_status: str | None
    currency: str
    subtotal_price: float
    total_price: float
    total_tax: float
    total_discounts: float
    line_items: list[dict[str, object]]
    customer: dict[str, object]
    billing_address: dict[str, object] | None
    shipping_address: dict[str, object] | None
    tags: list[str]
    source_name: str | None
    email: str | None

class OrderRepository:
    """Repository for order operations."""
    
    def __init__(self):
        # Get collection name from schema (like Mongoose model)
        self.collection_name: str = OrderSchema.__collection_name__
    
    def _get_collection(self):
        """Get the collection when needed."""
        return get_collection(self.collection_name)
    
    def create_order(self, order_data: dict[str, object]) -> dict[str, object]:
        """
        Create a new order in the database.
        
        Args:
            order_data: Order data to create
            
        Returns:
            dict: Created order with MongoDB _id
            
        Raises:
            Exception: If order creation fails
        """
        try:
            collection = self._get_collection()
            if collection is None:
                raise Exception("Database collection not available")
            
            # Validate order data using Pydantic schema
            # type: ignore[reportArgumentType] - data is already validated
            order_schema = OrderSchema(**order_data)
            
            # Convert to dict for MongoDB insertion
            order_dict = order_schema.model_dump(exclude_none=True)
            
            # Remove _id if it exists (let MongoDB generate it)
            if "_id" in order_dict:
                del order_dict["_id"]
            
            # Insert into database
            result = collection.insert_one(order_dict)
            
            # Get the created order with _id
            created_order = collection.find_one({"_id": result.inserted_id})
            
            if created_order:
                # Convert ObjectId to string for JSON serialization
                created_order["_id"] = str(created_order["_id"])
                return created_order
            else:
                raise Exception("Failed to retrieve created order")
                
        except Exception as e:
            raise Exception(f"Failed to create order: {str(e)}")
    
    def create_order_with_schema(self, order: OrderSchema) -> dict[str, object]:
        """
        Create a new order using OrderSchema instance.
        
        Args:
            order: OrderSchema instance with validated data
            
        Returns:
            dict: Created order with MongoDB _id
            
        Raises:
            Exception: If order creation fails
        """
        try:
            collection = self._get_collection()
            if collection is None:
                raise Exception("Database collection not available")
            
            # Convert schema to dict for MongoDB insertion
            order_dict = order.model_dump(exclude_none=True)
            
            # Remove _id if it exists (let MongoDB generate it)
            if "_id" in order_dict:
                del order_dict["_id"]
            
            # Insert into database
            result = collection.insert_one(order_dict)
            
            # Get the created order with _id
            created_order = collection.find_one({"_id": result.inserted_id})
            
            if created_order:
                # Convert ObjectId to string for JSON serialization
                created_order["_id"] = str(created_order["_id"])
                return created_order
            else:
                raise Exception("Failed to retrieve created order")
                
        except Exception as e:
            raise Exception(f"Failed to create order: {str(e)}")
    
    def get_order_by_id(self, order_id: str) -> dict[str, object] | None:
        """
        Get an order by its MongoDB _id.
        
        Args:
            order_id: Order ID as string
            
        Returns:
            dict | None: Order data or None if not found
        """
        try:
            collection = self._get_collection()
            if collection is None:
                return None
            
            # Convert string ID to ObjectId
            object_id = ObjectId(order_id)
            order = collection.find_one({"_id": object_id})
            
            if order:
                # Convert ObjectId to string for JSON serialization
                order["_id"] = str(order["_id"])
                return order
            return None
            
        except Exception as e:
            print(f"Error getting order by ID: {str(e)}")
            return None
    
    def get_order_by_shopify_id(self, shopify_order_id: int) -> dict[str, object] | None:
        """
        Get an order by its Shopify order ID.
        
        Args:
            shopify_order_id: Shopify order ID as integer
            
        Returns:
            dict | None: Order data or None if not found
        """
        try:
            collection = self._get_collection()
            if collection is None:
                return None
            
            order = collection.find_one({"order_id": shopify_order_id})
            
            if order:
                # Convert ObjectId to string for JSON serialization
                order["_id"] = str(order["_id"])
                return order
            return None
            
        except Exception as e:
            print(f"Error getting order by Shopify ID: {str(e)}")
            return None
    
    def get_orders_by_customer_id(self, customer_id: int) -> list[dict[str, object]]:
        """
        Get all orders for a specific customer.
        
        Args:
            customer_id: Customer ID as integer
            
        Returns:
            list[dict]: List of orders for the customer
        """
        try:
            collection = self._get_collection()
            if collection is None:
                return []
            
            orders = list(collection.find({"customer.customer_id": customer_id}))
            
            # Convert ObjectIds to strings for JSON serialization
            for order in orders:
                order["_id"] = str(order["_id"])
            
            return orders
            
        except Exception as e:
            print(f"Error getting orders by customer ID: {str(e)}")
            return []
    
    def get_orders_by_status(self, status: str) -> list[dict[str, object]]:
        """
        Get all orders with a specific status.
        
        Args:
            status: Order status (pending, paid, shipped, delivered, cancelled)
            
        Returns:
            list[dict]: List of orders with the specified status
        """
        try:
            collection = self._get_collection()
            if collection is None:
                return []
            
            orders = list(collection.find({"financial_status": status}))
            
            # Convert ObjectIds to strings for JSON serialization
            for order in orders:
                order["_id"] = str(order["_id"])
            
            return orders
            
        except Exception as e:
            print(f"Error getting orders by status: {str(e)}")
            return []
    
    def update_order_status(self, order_id: str, new_status: str) -> dict[str, object] | None:
        """
        Update the status of an order.
        
        Args:
            order_id: Order ID as string
            new_status: New status to set
            
        Returns:
            dict | None: Updated order data or None if not found
        """
        try:
            collection = self._get_collection()
            if collection is None:
                return None
            
            # Convert string ID to ObjectId
            object_id = ObjectId(order_id)
            
            # Update the order status
            result = collection.update_one(
                {"_id": object_id},
                {"$set": {"financial_status": new_status, "updated_at": datetime.now()}}
            )
            
            if result.modified_count > 0:
                # Get the updated order
                updated_order = collection.find_one({"_id": object_id})
                if updated_order:
                    # Convert ObjectId to string for JSON serialization
                    updated_order["_id"] = str(updated_order["_id"])
                    return updated_order
            
            return None
            
        except Exception as e:
            print(f"Error updating order status: {str(e)}")
            return None
    
    def get_all_orders(self, limit: int = 100, skip: int = 0) -> list[dict[str, object]]:
        """
        Get all orders with pagination.
        
        Args:
            limit: Maximum number of orders to return
            skip: Number of orders to skip
            
        Returns:
            list[dict]: List of orders
        """
        try:
            collection = self._get_collection()
            if collection is None:
                return []
            
            orders = list(collection.find().skip(skip).limit(limit).sort("created_at", -1))
            
            # Convert ObjectIds to strings for JSON serialization
            for order in orders:
                order["_id"] = str(order["_id"])
            
            return orders
            
        except Exception as e:
            print(f"Error getting all orders: {str(e)}")
            return [] 

    def get_total_units_sold_per_product(self) -> list[dict[str, object]]:
        """
        Get total units sold per product by aggregating all order line items.
        
        Returns:
            list[dict]: List with product_id, total_quantity_sold, and total_orders
        """
        try:
            collection = self._get_collection()
            if collection is None:
                return []
            
            # MongoDB aggregation pipeline to sum quantities by product_id
            pipeline = [
                # Unwind the line_items array to process each item separately
                {"$unwind": "$line_items"},
                
                # Group by product_id and sum quantities
                {
                    "$group": {
                        "_id": "$line_items.product_id",
                        "total_quantity_sold": {"$sum": "$line_items.quantity"},
                        "total_orders": {"$sum": 1},
                        "total_revenue": {"$sum": {"$multiply": ["$line_items.quantity", {"$toDouble": "$total_price"}]}}
                    }
                },
                
                # Sort by total quantity sold in descending order
                {"$sort": {"total_quantity_sold": -1}},
                
                # Rename _id field to product_id for clarity
                {
                    "$project": {
                        "product_id": "$_id",
                        "total_quantity_sold": 1,
                        "total_orders": 1,
                        "total_revenue": 1,
                        "_id": 0
                    }
                }
            ]
            
            # Execute aggregation
            result = list(collection.aggregate(pipeline))
            return result
            
        except Exception as e:
            print(f"Error getting total units sold per product: {str(e)}")
            return [] 