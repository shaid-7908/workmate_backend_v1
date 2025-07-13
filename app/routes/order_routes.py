from fastapi import APIRouter, HTTPException, status, Query
from fastapi import status as http_status
from app.model.order_schema import OrderSchema
from app.controller.order_controller import OrderController
from typing import Optional

# Create router
router = APIRouter(
    prefix="/api/orders",
    tags=["orders"],
    responses={404: {"description": "Not found"}}
)

# Initialize controller
order_controller = OrderController()

@router.post("/", status_code=http_status.HTTP_201_CREATED)
async def create_new_order(order_data: dict):
    """
    Create a new order.
    
    Args:
        order_data: Order data including line items, customer, addresses, etc.
        
    Returns:
        dict: Created order with MongoDB _id
        
    Raises:
        HTTPException: If order creation fails
    """
    try:
        created_order = order_controller.create_order(order_data)
        return {
            "success": True,
            "message": "Order created successfully",
            "data": created_order
        }
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create order: {str(e)}"
        )

@router.post("/from-shopify", status_code=http_status.HTTP_201_CREATED)
async def create_orders_from_shopify(
    limit: int = Query(default=50, description="Maximum number of orders to fetch"),
    status: Optional[str] = Query(default=None, description="Filter by order status (open, closed, cancelled, any)")
):
    """
    Create orders from Shopify data.
    
    Args:
        limit: Maximum number of orders to fetch from Shopify
        status: Filter by order status
        
    Returns:
        dict: Success message with count of orders created
    """
    try:
        order_controller.create_order_from_shopify(limit, status)
        return {
            "success": True,
            "message": f"Orders created successfully from Shopify (limit: {limit}, status: {status})"
        }
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create orders from Shopify: {str(e)}"
        )

@router.post("/with-schema", status_code=http_status.HTTP_201_CREATED)
async def create_order_using_schema(order: OrderSchema):
    """
    Create a new order using OrderSchema validation.
    
    Args:
        order: OrderSchema instance with validated data
        
    Returns:
        dict: Created order with MongoDB _id
        
    Raises:
        HTTPException: If order creation fails
    """
    try:
        created_order = order_controller.create_order_with_schema(order)
        return {
            "success": True,
            "message": "Order created successfully",
            "data": created_order
        }
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create order: {str(e)}"
        )

@router.get("/{order_id}")
async def get_order(order_id: str):
    """
    Get an order by its MongoDB ID.
    
    Args:
        order_id: Order ID as string
        
    Returns:
        dict: Order data or error message
        
    Raises:
        HTTPException: If order not found
    """
    try:
        order = order_controller.get_order_by_id(order_id)
        if order:
            return {
                "success": True,
                "message": "Order retrieved successfully",
                "data": order
            }
        else:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=f"Order with ID {order_id} not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving order: {str(e)}"
        )

@router.get("/shopify/{shopify_order_id}")
async def get_order_by_shopify_id(shopify_order_id: int):
    """
    Get an order by its Shopify order ID.
    
    Args:
        shopify_order_id: Shopify order ID as integer
        
    Returns:
        dict: Order data or error message
        
    Raises:
        HTTPException: If order not found
    """
    try:
        order = order_controller.get_order_by_shopify_id(shopify_order_id)
        if order:
            return {
                "success": True,
                "message": "Order retrieved successfully",
                "data": order
            }
        else:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=f"Order with Shopify ID {shopify_order_id} not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving order: {str(e)}"
        )

@router.get("/customer/{customer_id}")
async def get_orders_by_customer_id(customer_id: int):
    """
    Get all orders for a specific customer.
    
    Args:
        customer_id: Customer ID as integer
        
    Returns:
        dict: List of orders for the customer
        
    Raises:
        HTTPException: If error occurs
    """
    try:
        orders = order_controller.get_orders_by_customer_id(customer_id)
        return {
            "success": True,
            "message": f"Retrieved {len(orders)} orders for customer {customer_id}",
            "data": orders,
            "count": len(orders)
        }
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving orders for customer: {str(e)}"
        )

@router.get("/status/{status}")
async def get_orders_by_status(status: str):
    """
    Get all orders with a specific status.
    
    Args:
        status: Order status (pending, paid, shipped, delivered, cancelled)
        
    Returns:
        dict: List of orders with the specified status
        
    Raises:
        HTTPException: If error occurs
    """
    try:
        orders = order_controller.get_orders_by_status(status)
        return {
            "success": True,
            "message": f"Retrieved {len(orders)} orders with status '{status}'",
            "data": orders,
            "count": len(orders)
        }
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving orders by status: {str(e)}"
        )

@router.get("/")
async def get_all_orders(
    limit: int = Query(default=100, description="Maximum number of orders to return"),
    skip: int = Query(default=0, description="Number of orders to skip")
):
    """
    Get all orders with pagination.
    
    Args:
        limit: Maximum number of orders to return
        skip: Number of orders to skip
        
    Returns:
        dict: List of orders with pagination info
        
    Raises:
        HTTPException: If error occurs
    """
    try:
        orders = order_controller.get_all_orders(limit, skip)
        return {
            "success": True,
            "message": f"Retrieved {len(orders)} orders",
            "data": orders,
            "count": len(orders),
            "pagination": {
                "limit": limit,
                "skip": skip,
                "total_returned": len(orders)
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving orders: {str(e)}"
        )

@router.put("/{order_id}/status")
async def update_order_status(order_id: str, new_status: str):
    """
    Update the status of an order.
    
    Args:
        order_id: Order ID as string
        new_status: New status to set
        
    Returns:
        dict: Updated order data
        
    Raises:
        HTTPException: If order not found or update fails
    """
    try:
        updated_order = order_controller.update_order_status(order_id, new_status)
        if updated_order:
            return {
                "success": True,
                "message": f"Order status updated to '{new_status}' successfully",
                "data": updated_order
            }
        else:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=f"Order with ID {order_id} not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating order status: {str(e)}"
        )

@router.put("/{order_id}")
async def update_order(order_id: str, order_data: dict):
    """
    Update an order by its ID.
    
    Args:
        order_id: Order ID as string
        order_data: Updated order data
        
    Returns:
        dict: Updated order data
        
    Raises:
        HTTPException: If order not found or update fails
    """
    try:
        # First check if order exists
        existing_order = order_controller.get_order_by_id(order_id)
        if not existing_order:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=f"Order with ID {order_id} not found"
            )
        
        # TODO: Implement update logic in controller
        # For now, return a placeholder response
        return {
            "success": True,
            "message": "Order update endpoint - implement in controller",
            "data": existing_order
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating order: {str(e)}"
        )

@router.delete("/{order_id}")
async def delete_order(order_id: str):
    """
    Delete an order by its ID.
    
    Args:
        order_id: Order ID as string
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException: If order not found or deletion fails
    """
    try:
        # First check if order exists
        existing_order = order_controller.get_order_by_id(order_id)
        if not existing_order:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=f"Order with ID {order_id} not found"
            )
        
        # TODO: Implement delete logic in controller
        # For now, return a placeholder response
        return {
            "success": True,
            "message": "Order delete endpoint - implement in controller",
            "data": {"deleted_id": order_id}
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting order: {str(e)}"
        ) 