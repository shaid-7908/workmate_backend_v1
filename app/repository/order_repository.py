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

    def get_total_units_sold_per_product(self,limit: int = 100) -> list[dict[str, object]]:
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
                {"$limit": limit},
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

    def get_total_revenue_per_product(self) -> list[dict[str, object]]:
        """
        Get total revenue per product by proportionally distributing order totals.
        Revenue is calculated by distributing each order's subtotal based on line item quantities.
        
        Returns:
            list[dict]: List with product_id, total_revenue, total_quantity_sold, and average_price
        """
        try:
            collection = self._get_collection()
            if collection is None:
                return []
            
            # MongoDB aggregation pipeline to calculate revenue per product
            pipeline = [
                # Add total order quantity before unwinding
                {
                    "$addFields": {
                        "order_total_quantity": {
                            "$sum": "$line_items.quantity"
                        }
                    }
                },
                
                # Unwind the line_items array to process each item separately
                {"$unwind": "$line_items"},
                
                # Calculate proportional revenue for each line item
                {
                    "$addFields": {
                        "line_item_revenue": {
                            "$cond": {
                                "if": {"$gt": ["$order_total_quantity", 0]},
                                "then": {
                                    "$multiply": [
                                        {"$toDouble": "$subtotal_price"},
                                        {"$divide": ["$line_items.quantity", "$order_total_quantity"]}
                                    ]
                                },
                                "else": 0
                            }
                        }
                    }
                },
                
                # Group by product_id to sum revenue and quantities
                {
                    "$group": {
                        "_id": "$line_items.product_id",
                        "total_revenue": {"$sum": "$line_item_revenue"},
                        "total_quantity_sold": {"$sum": "$line_items.quantity"},
                        "total_orders": {"$sum": 1}
                    }
                },
                
                # Calculate average price per unit across all orders
                {
                    "$addFields": {
                        "average_price_per_unit": {
                            "$cond": {
                                "if": {"$gt": ["$total_quantity_sold", 0]},
                                "then": {"$divide": ["$total_revenue", "$total_quantity_sold"]},
                                "else": 0
                            }
                        }
                    }
                },
                
                # Sort by total revenue in descending order
                {"$sort": {"total_revenue": -1}},
                
                # Rename _id field to product_id for clarity and round values
                {
                    "$project": {
                        "product_id": "$_id",
                        "total_revenue": {"$round": ["$total_revenue", 2]},
                        "total_quantity_sold": 1,
                        "total_orders": 1,
                        "average_price_per_unit": {"$round": ["$average_price_per_unit", 2]},
                        "_id": 0
                    }
                }
            ]
            
            # Execute aggregation
            result = list(collection.aggregate(pipeline))
            
            return result
            
        except Exception as e:
            print(f"Error getting total revenue per product: {str(e)}")
            return []

    def get_sales_by_week(self, year: int = None) -> list[dict[str, object]]:
        """
        Get sales data grouped by week.
        
        Args:
            year: Filter by specific year (optional)
            
        Returns:
            list[dict]: List with week number, year, total_sales, order_count, and date range
        """
        try:
            collection = self._get_collection()
            if collection is None:
                return []
            
            # Build match stage for year filter
            match_stage = {}
            if year:
                match_stage = {
                    "created_at": {
                        "$gte": datetime(year, 1, 1),
                        "$lt": datetime(year + 1, 1, 1)
                    }
                }
            
            # MongoDB aggregation pipeline to group by week
            pipeline = [
                {"$match": match_stage},
                
                # Add week and year fields
                {
                    "$addFields": {
                        "week": {"$week": "$created_at"},
                        "year": {"$year": "$created_at"},
                        "yearWeek": {
                            "$concat": [
                                {"$toString": {"$year": "$created_at"}},
                                "-W",
                                {
                                    "$cond": {
                                        "if": {"$lt": [{"$week": "$created_at"}, 10]},
                                        "then": {"$concat": ["0", {"$toString": {"$week": "$created_at"}}]},
                                        "else": {"$toString": {"$week": "$created_at"}}
                                    }
                                }
                            ]
                        }
                    }
                },
                
                # Group by year and week
                {
                    "$group": {
                        "_id": {
                            "year": "$year",
                            "week": "$week",
                            "yearWeek": "$yearWeek"
                        },
                        "total_sales": {"$sum": {"$toDouble": "$total_price"}},
                        "total_revenue": {"$sum": {"$toDouble": "$subtotal_price"}},
                        "total_tax": {"$sum": {"$toDouble": "$total_tax"}},
                        "total_discounts": {"$sum": {"$toDouble": "$total_discounts"}},
                        "order_count": {"$sum": 1},
                        "week_start": {"$min": "$created_at"},
                        "week_end": {"$max": "$created_at"}
                    }
                },
                
                # Sort by year and week
                {"$sort": {"_id.year": 1, "_id.week": 1}},
                
                # Format output
                {
                    "$project": {
                        "year": "$_id.year",
                        "week": "$_id.week",
                        "year_week": "$_id.yearWeek",
                        "total_sales": {"$round": ["$total_sales", 2]},
                        "total_revenue": {"$round": ["$total_revenue", 2]},
                        "total_tax": {"$round": ["$total_tax", 2]},
                        "total_discounts": {"$round": ["$total_discounts", 2]},
                        "order_count": 1,
                        "week_start": {"$dateToString": {"format": "%Y-%m-%d", "date": "$week_start"}},
                        "week_end": {"$dateToString": {"format": "%Y-%m-%d", "date": "$week_end"}},
                        "_id": 0
                    }
                }
            ]
            
            # Execute aggregation
            result = list(collection.aggregate(pipeline))
            
            return result
            
        except Exception as e:
            print(f"Error getting sales by week: {str(e)}")
            return []

    def get_sales_by_month(self, year: int = None) -> list[dict[str, object]]:
        """
        Get sales data grouped by month.
        
        Args:
            year: Filter by specific year (optional)
            
        Returns:
            list[dict]: List with month, year, total_sales, order_count, and month name
        """
        try:
            collection = self._get_collection()
            if collection is None:
                return []
            
            # Build match stage for year filter
            match_stage = {}
            if year:
                match_stage = {
                    "created_at": {
                        "$gte": datetime(year, 1, 1),
                        "$lt": datetime(year + 1, 1, 1)
                    }
                }
            
            # MongoDB aggregation pipeline to group by month
            pipeline = [
                {"$match": match_stage},
                
                # Add month and year fields
                {
                    "$addFields": {
                        "month": {"$month": "$created_at"},
                        "year": {"$year": "$created_at"},
                        "yearMonth": {
                            "$concat": [
                                {"$toString": {"$year": "$created_at"}},
                                "-",
                                {
                                    "$cond": {
                                        "if": {"$lt": [{"$month": "$created_at"}, 10]},
                                        "then": {"$concat": ["0", {"$toString": {"$month": "$created_at"}}]},
                                        "else": {"$toString": {"$month": "$created_at"}}
                                    }
                                }
                            ]
                        }
                    }
                },
                
                # Group by year and month
                {
                    "$group": {
                        "_id": {
                            "year": "$year",
                            "month": "$month",
                            "yearMonth": "$yearMonth"
                        },
                        "total_sales": {"$sum": {"$toDouble": "$total_price"}},
                        "total_revenue": {"$sum": {"$toDouble": "$subtotal_price"}},
                        "total_tax": {"$sum": {"$toDouble": "$total_tax"}},
                        "total_discounts": {"$sum": {"$toDouble": "$total_discounts"}},
                        "order_count": {"$sum": 1},
                        "month_start": {"$min": "$created_at"},
                        "month_end": {"$max": "$created_at"}
                    }
                },
                
                # Sort by year and month
                {"$sort": {"_id.year": 1, "_id.month": 1}},
                
                # Format output with month names
                {
                    "$project": {
                        "year": "$_id.year",
                        "month": "$_id.month",
                        "year_month": "$_id.yearMonth",
                        "month_name": {
                            "$switch": {
                                "branches": [
                                    {"case": {"$eq": ["$_id.month", 1]}, "then": "January"},
                                    {"case": {"$eq": ["$_id.month", 2]}, "then": "February"},
                                    {"case": {"$eq": ["$_id.month", 3]}, "then": "March"},
                                    {"case": {"$eq": ["$_id.month", 4]}, "then": "April"},
                                    {"case": {"$eq": ["$_id.month", 5]}, "then": "May"},
                                    {"case": {"$eq": ["$_id.month", 6]}, "then": "June"},
                                    {"case": {"$eq": ["$_id.month", 7]}, "then": "July"},
                                    {"case": {"$eq": ["$_id.month", 8]}, "then": "August"},
                                    {"case": {"$eq": ["$_id.month", 9]}, "then": "September"},
                                    {"case": {"$eq": ["$_id.month", 10]}, "then": "October"},
                                    {"case": {"$eq": ["$_id.month", 11]}, "then": "November"},
                                    {"case": {"$eq": ["$_id.month", 12]}, "then": "December"}
                                ],
                                "default": "Unknown"
                            }
                        },
                        "total_sales": {"$round": ["$total_sales", 2]},
                        "total_revenue": {"$round": ["$total_revenue", 2]},
                        "total_tax": {"$round": ["$total_tax", 2]},
                        "total_discounts": {"$round": ["$total_discounts", 2]},
                        "order_count": 1,
                        "month_start": {"$dateToString": {"format": "%Y-%m-%d", "date": "$month_start"}},
                        "month_end": {"$dateToString": {"format": "%Y-%m-%d", "date": "$month_end"}},
                        "_id": 0
                    }
                }
            ]
            
            # Execute aggregation
            result = list(collection.aggregate(pipeline))
            
            return result
            
        except Exception as e:
            print(f"Error getting sales by month: {str(e)}")
            return []

    def get_sales_by_day_of_week(self, year: int = None) -> list[dict[str, object]]:
        """
        Get sales data grouped by day of the week.
        
        Args:
            year: Filter by specific year (optional)
            
        Returns:
            list[dict]: List with day of week, total_sales, order_count, and day name
        """
        try:
            collection = self._get_collection()
            if collection is None:
                return []
            
            # Build match stage for year filter
            match_stage = {}
            if year:
                match_stage = {
                    "created_at": {
                        "$gte": datetime(year, 1, 1),
                        "$lt": datetime(year + 1, 1, 1)
                    }
                }
            
            # MongoDB aggregation pipeline to group by day of week
            pipeline = [
                {"$match": match_stage},
                
                # Add day of week field (1=Sunday, 2=Monday, ... 7=Saturday)
                {
                    "$addFields": {
                        "dayOfWeek": {"$dayOfWeek": "$created_at"},
                        "year": {"$year": "$created_at"}
                    }
                },
                
                # Group by day of week
                {
                    "$group": {
                        "_id": "$dayOfWeek",
                        "total_sales": {"$sum": {"$toDouble": "$total_price"}},
                        "total_revenue": {"$sum": {"$toDouble": "$subtotal_price"}},
                        "total_tax": {"$sum": {"$toDouble": "$total_tax"}},
                        "total_discounts": {"$sum": {"$toDouble": "$total_discounts"}},
                        "order_count": {"$sum": 1}
                    }
                },
                
                # Sort by day of week
                {"$sort": {"_id": 1}},
                
                # Format output with day names
                {
                    "$project": {
                        "day_of_week": "$_id",
                        "day_name": {
                            "$switch": {
                                "branches": [
                                    {"case": {"$eq": ["$_id", 1]}, "then": "Sunday"},
                                    {"case": {"$eq": ["$_id", 2]}, "then": "Monday"},
                                    {"case": {"$eq": ["$_id", 3]}, "then": "Tuesday"},
                                    {"case": {"$eq": ["$_id", 4]}, "then": "Wednesday"},
                                    {"case": {"$eq": ["$_id", 5]}, "then": "Thursday"},
                                    {"case": {"$eq": ["$_id", 6]}, "then": "Friday"},
                                    {"case": {"$eq": ["$_id", 7]}, "then": "Saturday"}
                                ],
                                "default": "Unknown"
                            }
                        },
                        "total_sales": {"$round": ["$total_sales", 2]},
                        "total_revenue": {"$round": ["$total_revenue", 2]},
                        "total_tax": {"$round": ["$total_tax", 2]},
                        "total_discounts": {"$round": ["$total_discounts", 2]},
                        "order_count": 1,
                        "_id": 0
                    }
                }
            ]
            
            # Execute aggregation
            result = list(collection.aggregate(pipeline))
            
            return result
            
        except Exception as e:
            print(f"Error getting sales by day of week: {str(e)}")
            return []

    def get_sales_by_hour(self, year: int = None) -> list[dict[str, object]]:
        """
        Get sales data grouped by hour of the day.
        
        Args:
            year: Filter by specific year (optional)
            
        Returns:
            list[dict]: List with hour, total_sales, order_count, and time period
        """
        try:
            collection = self._get_collection()
            if collection is None:
                return []
            
            # Build match stage for year filter
            match_stage = {}
            if year:
                match_stage = {
                    "created_at": {
                        "$gte": datetime(year, 1, 1),
                        "$lt": datetime(year + 1, 1, 1)
                    }
                }
            
            # MongoDB aggregation pipeline to group by hour
            pipeline = [
                {"$match": match_stage},
                
                # Add hour field
                {
                    "$addFields": {
                        "hour": {"$hour": "$created_at"},
                        "year": {"$year": "$created_at"}
                    }
                },
                
                # Group by hour
                {
                    "$group": {
                        "_id": "$hour",
                        "total_sales": {"$sum": {"$toDouble": "$total_price"}},
                        "total_revenue": {"$sum": {"$toDouble": "$subtotal_price"}},
                        "total_tax": {"$sum": {"$toDouble": "$total_tax"}},
                        "total_discounts": {"$sum": {"$toDouble": "$total_discounts"}},
                        "order_count": {"$sum": 1}
                    }
                },
                
                # Sort by hour
                {"$sort": {"_id": 1}},
                
                # Format output with time periods
                {
                    "$project": {
                        "hour": "$_id",
                        "time_period": {
                            "$switch": {
                                "branches": [
                                    {"case": {"$and": [{"$gte": ["$_id", 0]}, {"$lt": ["$_id", 6]}]}, "then": "Late Night (12-6 AM)"},
                                    {"case": {"$and": [{"$gte": ["$_id", 6]}, {"$lt": ["$_id", 12]}]}, "then": "Morning (6 AM-12 PM)"},
                                    {"case": {"$and": [{"$gte": ["$_id", 12]}, {"$lt": ["$_id", 18]}]}, "then": "Afternoon (12-6 PM)"},
                                    {"case": {"$and": [{"$gte": ["$_id", 18]}, {"$lt": ["$_id", 24]}]}, "then": "Evening (6 PM-12 AM)"}
                                ],
                                "default": "Unknown"
                            }
                        },
                        "formatted_time": {
                            "$concat": [
                                {
                                    "$cond": {
                                        "if": {"$eq": ["$_id", 0]},
                                        "then": "12:00 AM",
                                        "else": {
                                            "$cond": {
                                                "if": {"$lt": ["$_id", 12]},
                                                "then": {"$concat": [{"$toString": "$_id"}, ":00 AM"]},
                                                "else": {
                                                    "$cond": {
                                                        "if": {"$eq": ["$_id", 12]},
                                                        "then": "12:00 PM",
                                                        "else": {"$concat": [{"$toString": {"$subtract": ["$_id", 12]}}, ":00 PM"]}
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            ]
                        },
                        "total_sales": {"$round": ["$total_sales", 2]},
                        "total_revenue": {"$round": ["$total_revenue", 2]},
                        "total_tax": {"$round": ["$total_tax", 2]},
                        "total_discounts": {"$round": ["$total_discounts", 2]},
                        "order_count": 1,
                        "_id": 0
                    }
                }
            ]
            
            # Execute aggregation
            result = list(collection.aggregate(pipeline))
            
            return result
            
        except Exception as e:
            print(f"Error getting sales by hour: {str(e)}")
            return []

    def get_most_popular_product_combos(self, min_combo_size: int = 2, limit: int = 20) -> list[dict[str, object]]:
        """
        Get most popular product combinations from orders.
        
        Args:
            min_combo_size: Minimum number of products in combination (default: 2)
            limit: Maximum number of combinations to return (default: 20)
            
        Returns:
            list[dict]: List with product combinations, frequency, and total revenue
        """
        try:
            collection = self._get_collection()
            if collection is None:
                return []
            
            # MongoDB aggregation pipeline to find product combinations
            pipeline = [
                # Filter orders that have at least min_combo_size products
                {
                    "$match": {
                        "line_items": {"$size": {"$gte": min_combo_size}}
                    }
                },
                
                # Create product combinations for each order
                {
                    "$addFields": {
                        "product_ids": {
                            "$map": {
                                "input": "$line_items",
                                "as": "item",
                                "in": "$$item.product_id"
                            }
                        },
                        "order_total": {"$toDouble": "$total_price"}
                    }
                },
                
                # Sort product IDs to ensure consistent combination representation
                {
                    "$addFields": {
                        "sorted_product_ids": {
                            "$sortArray": {
                                "input": "$product_ids",
                                "sortBy": 1
                            }
                        }
                    }
                },
                
                # Group by product combination
                {
                    "$group": {
                        "_id": "$sorted_product_ids",
                        "frequency": {"$sum": 1},
                        "total_revenue": {"$sum": "$order_total"},
                        "average_order_value": {"$avg": "$order_total"},
                        "orders": {"$push": "$order_id"}
                    }
                },
                
                # Filter combinations with at least the minimum size
                {
                    "$match": {
                        "_id": {"$size": {"$gte": min_combo_size}}
                    }
                },
                
                # Sort by frequency (most popular first)
                {"$sort": {"frequency": -1}},
                
                # Limit results
                {"$limit": limit},
                
                # Format output
                {
                    "$project": {
                        "product_combination": "$_id",
                        "combo_size": {"$size": "$_id"},
                        "frequency": 1,
                        "total_revenue": {"$round": ["$total_revenue", 2]},
                        "average_order_value": {"$round": ["$average_order_value", 2]},
                        "sample_orders": {"$slice": ["$orders", 3]},  # Show first 3 order IDs as examples
                        "_id": 0
                    }
                }
            ]
            
            # Execute aggregation
            result = list(collection.aggregate(pipeline))
            
            return result
            
        except Exception as e:
            print(f"Error getting most popular product combos: {str(e)}")
            return [] 

    def get_total_orders(self) -> dict[str, object]:
        """
        Get the total number of orders in the database.
        
        Returns:
            dict: Total order count and additional statistics
        """
        try:
            collection = self._get_collection()
            if collection is None:
                return {"total_orders": 0}
            
            # MongoDB aggregation pipeline to get comprehensive order statistics
            pipeline = [
                {
                    "$group": {
                        "_id": None,
                        "total_orders": {"$sum": 1},
                        "total_revenue": {"$sum": {"$toDouble": "$total_price"}},
                        "total_subtotal": {"$sum": {"$toDouble": "$subtotal_price"}},
                        "total_tax": {"$sum": {"$toDouble": "$total_tax"}},
                        "total_discounts": {"$sum": {"$toDouble": "$total_discounts"}},
                        "earliest_order": {"$min": "$created_at"},
                        "latest_order": {"$max": "$created_at"}
                    }
                },
                {
                    "$project": {
                        "total_orders": 1,
                        "total_revenue": {"$round": ["$total_revenue", 2]},
                        "total_subtotal": {"$round": ["$total_subtotal", 2]},
                        "total_tax": {"$round": ["$total_tax", 2]},
                        "total_discounts": {"$round": ["$total_discounts", 2]},
                        "earliest_order": {"$dateToString": {"format": "%Y-%m-%d", "date": "$earliest_order"}},
                        "latest_order": {"$dateToString": {"format": "%Y-%m-%d", "date": "$latest_order"}},
                        "_id": 0
                    }
                }
            ]
            
            # Execute aggregation
            result = list(collection.aggregate(pipeline))
            
            if result:
                return result[0]
            else:
                return {"total_orders": 0}
            
        except Exception as e:
            print(f"Error getting total orders: {str(e)}")
            return {"total_orders": 0}

    def get_average_order_value(self) -> dict[str, object]:
        """
        Get the average order value and related statistics.
        
        Returns:
            dict: Average order value and comprehensive order value statistics
        """
        try:
            collection = self._get_collection()
            if collection is None:
                return {"average_order_value": 0}
            
            # MongoDB aggregation pipeline to calculate order value statistics
            pipeline = [
                {
                    "$addFields": {
                        "order_value": {"$toDouble": "$total_price"},
                        "subtotal_value": {"$toDouble": "$subtotal_price"}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total_orders": {"$sum": 1},
                        "total_revenue": {"$sum": "$order_value"},
                        "total_subtotal": {"$sum": "$subtotal_value"},
                        "average_order_value": {"$avg": "$order_value"},
                        "average_subtotal_value": {"$avg": "$subtotal_value"},
                        "min_order_value": {"$min": "$order_value"},
                        "max_order_value": {"$max": "$order_value"},
                        "median_calculation": {"$push": "$order_value"}
                    }
                },
                {
                    "$project": {
                        "total_orders": 1,
                        "total_revenue": {"$round": ["$total_revenue", 2]},
                        "total_subtotal": {"$round": ["$total_subtotal", 2]},
                        "average_order_value": {"$round": ["$average_order_value", 2]},
                        "average_subtotal_value": {"$round": ["$average_subtotal_value", 2]},
                        "min_order_value": {"$round": ["$min_order_value", 2]},
                        "max_order_value": {"$round": ["$max_order_value", 2]},
                        "order_value_range": {"$round": [{"$subtract": ["$max_order_value", "$min_order_value"]}, 2]},
                        "_id": 0
                    }
                }
            ]
            
            # Execute aggregation
            result = list(collection.aggregate(pipeline))
            
            if result and result[0]["total_orders"] > 0:
                stats = result[0]
                
                # Calculate additional insights
                if stats["total_orders"] > 0:
                    stats["revenue_per_order"] = round(stats["total_revenue"] / stats["total_orders"], 2)
                
                return stats
            else:
                return {
                    "total_orders": 0,
                    "average_order_value": 0,
                    "total_revenue": 0,
                    "min_order_value": 0,
                    "max_order_value": 0
                }
            
        except Exception as e:
            print(f"Error getting average order value: {str(e)}")
            return {"average_order_value": 0}

    def get_monthly_order_data(self, year: int = None) -> list[dict[str, object]]:
        """
        Get monthly order data with total orders, total revenue, and average order value per month.
        
        Args:
            year: Filter by specific year (optional)
            
        Returns:
            list[dict]: List with monthly order statistics including total orders, revenue, and AOV
        """
        try:
            collection = self._get_collection()
            if collection is None:
                return []
            
            # Build match stage for year filter
            match_stage = {}
            if year:
                match_stage = {
                    "created_at": {
                        "$gte": datetime(year, 1, 1),
                        "$lt": datetime(year + 1, 1, 1)
                    }
                }
            
            # MongoDB aggregation pipeline to get monthly order data
            pipeline = [
                {"$match": match_stage},
                
                # Add month and year fields
                {
                    "$addFields": {
                        "month": {"$month": "$created_at"},
                        "year": {"$year": "$created_at"},
                        "order_value": {"$toDouble": "$total_price"},
                        "revenue_value": {"$toDouble": "$subtotal_price"}
                    }
                },
                
                # Group by year and month
                {
                    "$group": {
                        "_id": {
                            "year": "$year",
                            "month": "$month"
                        },
                        "total_orders": {"$sum": 1},
                        "total_revenue": {"$sum": "$revenue_value"},
                        "total_sales": {"$sum": "$order_value"},
                        "total_tax": {"$sum": {"$toDouble": "$total_tax"}},
                        "total_discounts": {"$sum": {"$toDouble": "$total_discounts"}},
                        "average_order_value": {"$avg": "$order_value"},
                        "min_order_value": {"$min": "$order_value"},
                        "max_order_value": {"$max": "$order_value"},
                        "month_start": {"$min": "$created_at"},
                        "month_end": {"$max": "$created_at"}
                    }
                },
                
                # Sort by year and month
                {"$sort": {"_id.year": 1, "_id.month": 1}},
                
                # Format output with month names and calculations
                {
                    "$project": {
                        "year": "$_id.year",
                        "month": "$_id.month",
                        "month_name": {
                            "$switch": {
                                "branches": [
                                    {"case": {"$eq": ["$_id.month", 1]}, "then": "January"},
                                    {"case": {"$eq": ["$_id.month", 2]}, "then": "February"},
                                    {"case": {"$eq": ["$_id.month", 3]}, "then": "March"},
                                    {"case": {"$eq": ["$_id.month", 4]}, "then": "April"},
                                    {"case": {"$eq": ["$_id.month", 5]}, "then": "May"},
                                    {"case": {"$eq": ["$_id.month", 6]}, "then": "June"},
                                    {"case": {"$eq": ["$_id.month", 7]}, "then": "July"},
                                    {"case": {"$eq": ["$_id.month", 8]}, "then": "August"},
                                    {"case": {"$eq": ["$_id.month", 9]}, "then": "September"},
                                    {"case": {"$eq": ["$_id.month", 10]}, "then": "October"},
                                    {"case": {"$eq": ["$_id.month", 11]}, "then": "November"},
                                    {"case": {"$eq": ["$_id.month", 12]}, "then": "December"}
                                ],
                                "default": "Unknown"
                            }
                        },
                        "year_month": {
                            "$concat": [
                                {"$toString": "$_id.year"},
                                "-",
                                {
                                    "$cond": {
                                        "if": {"$lt": ["$_id.month", 10]},
                                        "then": {"$concat": ["0", {"$toString": "$_id.month"}]},
                                        "else": {"$toString": "$_id.month"}
                                    }
                                }
                            ]
                        },
                        "total_orders": 1,
                        "total_revenue": {"$round": ["$total_revenue", 2]},
                        "total_sales": {"$round": ["$total_sales", 2]},
                        "total_tax": {"$round": ["$total_tax", 2]},
                        "total_discounts": {"$round": ["$total_discounts", 2]},
                        "average_order_value": {"$round": ["$average_order_value", 2]},
                        "min_order_value": {"$round": ["$min_order_value", 2]},
                        "max_order_value": {"$round": ["$max_order_value", 2]},
                        "order_value_range": {"$round": [{"$subtract": ["$max_order_value", "$min_order_value"]}, 2]},
                        "month_start": {"$dateToString": {"format": "%Y-%m-%d", "date": "$month_start"}},
                        "month_end": {"$dateToString": {"format": "%Y-%m-%d", "date": "$month_end"}},
                        "_id": 0
                    }
                }
            ]
            
            # Execute aggregation
            result = list(collection.aggregate(pipeline))
            
            return result
            
        except Exception as e:
            print(f"Error getting monthly order data: {str(e)}")
            return [] 