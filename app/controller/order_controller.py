from app import config
from app.repository.order_repository import OrderRepository
from app.model.order_schema import OrderSchema
from app.config.env_config import Config
import requests
from pprint import pprint
from datetime import datetime
from typing import List, Optional

class OrderController:
    """Controller for order business logic."""
    
    def __init__(self):
        self.repository = OrderRepository()
        self.config = Config()

    def create_order(self, order_data: dict[str, object]) -> dict[str, object]:
        """
        Create a new order.
        
        Args:
            order_data: Order data to create
            
        Returns:
            dict: Created order with MongoDB _id
            
        Raises:
            Exception: If order creation fails
        """
        return self.repository.create_order(order_data)

    def get_orders_from_shopify(self, limit: int = 50, status: Optional[str] = None):
        """
        Get orders from Shopify API.
        
        Args:
            limit: Maximum number of orders to fetch
            status: Filter by order status (open, closed, cancelled, any)
            
        Returns:
            dict: Shopify orders response
        """
        url = f"https://{self.config.SHOPIFY_STORE_NAME}/admin/api/2023-10/orders.json"
        params = {
            "limit": limit
        }
        
        if status:
            params["status"] = status
            
        headers = {
            "X-Shopify-Access-Token": self.config.SHOPIFY_ACCESS_TOKEN
        }
        
        response = requests.get(url, headers=headers, params=params)
        return response.json()

    def create_order_from_shopify(self, limit: int = 50, status: Optional[str] = None):
        """
        Create orders from Shopify data.
        
        Args:
            limit: Maximum number of orders to fetch from Shopify
            status: Filter by order status
        """
        orders_data = self.get_orders_from_shopify(limit, status)
        
        for order_data in orders_data.get('orders', []):
            pprint(order_data, sort_dicts=False)
            
            # Transform Shopify line items to match our schema
            transformed_line_items = []
            for item in order_data.get('line_items', []):
                line_item = {
                    "product_id": item['product_id'],
                    "variant_id": item['variant_id'],
                    "quantity": item['quantity'],
                    "total_discount": float(item.get('total_discount', '0.0')),
                    "requires_shipping": item.get('requires_shipping', False)
                }
                transformed_line_items.append(line_item)
            
            # Transform customer data
            customer_data = order_data.get('customer', {})
            # Ensure customer tags is always a list
            customer_tags = customer_data.get('tags', [])
            if isinstance(customer_tags, str):
                customer_tags = [tag.strip() for tag in customer_tags.split(',') if tag.strip()]
            elif not isinstance(customer_tags, list):
                customer_tags = []
            customer_info = {
                "customer_id": customer_data.get('id', 0),
                "first_name": customer_data.get('first_name', ''),
                "last_name": customer_data.get('last_name', ''),
                "email": customer_data.get('email', ''),
                "phone": customer_data.get('phone'),
                "tags": customer_tags,
                "created_at": datetime.fromisoformat(customer_data['created_at'].replace('Z', '+00:00')) if customer_data.get('created_at') else datetime.now(),
                "verified_email": customer_data.get('verified_email', True)
            }
            
            # Transform billing address
            billing_address = None
            if order_data.get('billing_address'):
                billing_data = order_data['billing_address']
                billing_address = {
                    "first_name": billing_data.get('first_name', ''),
                    "last_name": billing_data.get('last_name', ''),
                    "address1": billing_data.get('address1', ''),
                    "address2": billing_data.get('address2'),
                    "city": billing_data.get('city', ''),
                    "zip": billing_data.get('zip', ''),
                    "province": billing_data.get('province'),
                    "country": billing_data.get('country', ''),
                    "country_code": billing_data.get('country_code', ''),
                    "phone": billing_data.get('phone'),
                    "latitude": billing_data.get('latitude'),
                    "longitude": billing_data.get('longitude')
                }
            
            # Transform shipping address
            shipping_address = None
            if order_data.get('shipping_address'):
                shipping_data = order_data['shipping_address']
                shipping_address = {
                    "first_name": shipping_data.get('first_name', ''),
                    "last_name": shipping_data.get('last_name', ''),
                    "address1": shipping_data.get('address1', ''),
                    "address2": shipping_data.get('address2'),
                    "city": shipping_data.get('city', ''),
                    "zip": shipping_data.get('zip', ''),
                    "province": shipping_data.get('province'),
                    "country": shipping_data.get('country', ''),
                    "country_code": shipping_data.get('country_code', ''),
                    "phone": shipping_data.get('phone'),
                    "latitude": shipping_data.get('latitude'),
                    "longitude": shipping_data.get('longitude')
                }
            
            # Transform Shopify data to match our schema
            # Ensure order tags is always a list
            order_tags = order_data.get('tags', [])
            if isinstance(order_tags, str):
                order_tags = [tag.strip() for tag in order_tags.split(',') if tag.strip()]
            elif not isinstance(order_tags, list):
                order_tags = []
            data_to_create = {
                "order_id": order_data['id'],
                "order_number": order_data['order_number'],
                "name": order_data['name'],
                "created_at": datetime.fromisoformat(order_data['created_at'].replace('Z', '+00:00')),
                "processed_at": datetime.fromisoformat(order_data['processed_at'].replace('Z', '+00:00')) if order_data.get('processed_at') else None,
                "updated_at": datetime.fromisoformat(order_data['updated_at'].replace('Z', '+00:00')),
                "financial_status": order_data.get('financial_status', 'pending'),
                "fulfillment_status": order_data.get('fulfillment_status'),
                "currency": order_data.get('currency', 'USD'),
                "subtotal_price": float(order_data.get('subtotal_price', '0.0')),
                "total_price": float(order_data.get('total_price', '0.0')),
                "total_tax": float(order_data.get('total_tax', '0.0')),
                "total_discounts": float(order_data.get('total_discounts', '0.0')),
                "line_items": transformed_line_items,
                "customer": customer_info,
                "billing_address": billing_address,
                "shipping_address": shipping_address,
                "tags": order_tags,
                "source_name": order_data.get('source_name'),
                "email": order_data.get('email')
            }
            
            # Create OrderSchema instance from the data
            order_schema = OrderSchema(**data_to_create)
            self.create_order_with_schema(order_schema)
    
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
        return self.repository.create_order_with_schema(order)
    
    def get_order_by_id(self, order_id: str) -> dict[str, object] | None:
        """
        Get an order by its MongoDB _id.
        
        Args:
            order_id: Order ID as string
            
        Returns:
            dict | None: Order data or None if not found
        """
        return self.repository.get_order_by_id(order_id)
    
    def get_order_by_shopify_id(self, shopify_order_id: int) -> dict[str, object] | None:
        """
        Get an order by its Shopify order ID.
        
        Args:
            shopify_order_id: Shopify order ID as integer
            
        Returns:
            dict | None: Order data or None if not found
        """
        return self.repository.get_order_by_shopify_id(shopify_order_id)
    
    def get_orders_by_customer_id(self, customer_id: int) -> list[dict[str, object]]:
        """
        Get all orders for a specific customer.
        
        Args:
            customer_id: Customer ID as integer
            
        Returns:
            list[dict]: List of orders for the customer
        """
        return self.repository.get_orders_by_customer_id(customer_id)
    
    def get_orders_by_status(self, status: str) -> list[dict[str, object]]:
        """
        Get all orders with a specific status.
        
        Args:
            status: Order status (pending, paid, shipped, delivered, cancelled)
            
        Returns:
            list[dict]: List of orders with the specified status
        """
        return self.repository.get_orders_by_status(status)
    
    def update_order_status(self, order_id: str, new_status: str) -> dict[str, object] | None:
        """
        Update the status of an order.
        
        Args:
            order_id: Order ID as string
            new_status: New status to set
            
        Returns:
            dict | None: Updated order data or None if not found
        """
        return self.repository.update_order_status(order_id, new_status)
    
    def get_all_orders(self, limit: int = 100, skip: int = 0) -> list[dict[str, object]]:
        """
        Get all orders with pagination.
        
        Args:
            limit: Maximum number of orders to return
            skip: Number of orders to skip
            
        Returns:
            list[dict]: List of orders
        """
        return self.repository.get_all_orders(limit, skip)
    
    def update_order(self, order_id: str, order_data: dict[str, object]) -> dict[str, object] | None:
        """
        Update an order by its ID.
        
        Args:
            order_id: Order ID as string
            order_data: Updated order data
            
        Returns:
            dict | None: Updated order data or None if not found
            
        Raises:
            Exception: If update fails
        """
        # TODO: Implement update logic in repository
        # For now, return None to indicate not implemented
        return None
    
    def delete_order(self, order_id: str) -> bool:
        """
        Delete an order by its ID.
        
        Args:
            order_id: Order ID as string
            
        Returns:
            bool: True if deleted successfully, False otherwise
            
        Raises:
            Exception: If deletion fails
        """
        # TODO: Implement delete logic in repository
        # For now, return False to indicate not implemented
        return False 