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

@router.get("/analytics/sales/weekly")
async def get_sales_by_week(
    year: Optional[int] = Query(default=None, description="Filter by specific year (e.g., 2024)")
):
    """
    Get sales data grouped by week.
    
    Args:
        year: Filter by specific year (optional)
        
    Returns:
        dict: Sales data grouped by week with totals and order counts
        
    Raises:
        HTTPException: If error occurs
    """
    try:
        sales_data = order_controller.get_sales_by_week(year)
        
        # Calculate summary statistics
        total_sales = sum(item.get('total_sales', 0) for item in sales_data)
        total_orders = sum(item.get('order_count', 0) for item in sales_data)
        total_weeks = len(sales_data)
        
        return {
            "success": True,
            "message": f"Retrieved weekly sales data{f' for year {year}' if year else ''}",
            "data": sales_data,
            "summary": {
                "total_sales": round(total_sales, 2),
                "total_orders": total_orders,
                "total_weeks": total_weeks,
                "average_sales_per_week": round(total_sales / total_weeks if total_weeks > 0 else 0, 2),
                "average_orders_per_week": round(total_orders / total_weeks if total_weeks > 0 else 0, 2),
                "year_filter": year
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving weekly sales data: {str(e)}"
        )

@router.get("/analytics/sales/monthly")
async def get_sales_by_month(
    year: Optional[int] = Query(default=None, description="Filter by specific year (e.g., 2024)")
):
    """
    Get sales data grouped by month.
    
    Args:
        year: Filter by specific year (optional)
        
    Returns:
        dict: Sales data grouped by month with totals and order counts
        
    Raises:
        HTTPException: If error occurs
    """
    try:
        sales_data = order_controller.get_sales_by_month(year)
        
        # Calculate summary statistics
        total_sales = sum(item.get('total_sales', 0) for item in sales_data)
        total_orders = sum(item.get('order_count', 0) for item in sales_data)
        total_months = len(sales_data)
        
        return {
            "success": True,
            "message": f"Retrieved monthly sales data{f' for year {year}' if year else ''}",
            "data": sales_data,
            "summary": {
                "total_sales": round(total_sales, 2),
                "total_orders": total_orders,
                "total_months": total_months,
                "average_sales_per_month": round(total_sales / total_months if total_months > 0 else 0, 2),
                "average_orders_per_month": round(total_orders / total_months if total_months > 0 else 0, 2),
                "year_filter": year
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving monthly sales data: {str(e)}"
        )

# Analytics routes for product performance
@router.get("/analytics/products/units-sold")
async def get_total_units_sold_per_product():
    """
    Get total units sold per product.
    
    Returns:
        dict: List of products with total quantities sold and order counts
        
    Raises:
        HTTPException: If error occurs
    """
    try:
        product_data = order_controller.get_total_units_sold_per_product()
        
        # Calculate summary statistics
        total_units = sum(item.get('total_quantity_sold', 0) for item in product_data)
        total_products = len(product_data)
        
        return {
            "success": True,
            "message": f"Retrieved units sold data for {total_products} products",
            "data": product_data,
            "summary": {
                "total_units_sold": total_units,
                "total_products": total_products,
                "average_units_per_product": round(total_units / total_products if total_products > 0 else 0, 2)
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving product units sold data: {str(e)}"
        )

@router.get("/analytics/products/revenue")
async def get_total_revenue_per_product():
    """
    Get total revenue per product.
    
    Returns:
        dict: List of products with total revenue and sales metrics
        
    Raises:
        HTTPException: If error occurs
    """
    try:
        product_data = order_controller.get_total_revenue_per_product()
        
        # Calculate summary statistics
        total_revenue = sum(item.get('total_revenue', 0) for item in product_data)
        total_products = len(product_data)
        
        return {
            "success": True,
            "message": f"Retrieved revenue data for {total_products} products",
            "data": product_data,
            "summary": {
                "total_revenue": round(total_revenue, 2),
                "total_products": total_products,
                "average_revenue_per_product": round(total_revenue / total_products if total_products > 0 else 0, 2)
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving product revenue data: {str(e)}"
        )

@router.get("/analytics/sales/by-day")
async def get_sales_by_day_of_week(
    year: Optional[int] = Query(default=None, description="Filter by specific year (e.g., 2024)")
):
    """
    Get sales data grouped by day of the week.
    
    Args:
        year: Filter by specific year (optional)
        
    Returns:
        dict: Sales data grouped by day of week with performance metrics
        
    Raises:
        HTTPException: If error occurs
    """
    try:
        sales_data = order_controller.get_sales_by_day_of_week(year)
        
        # Calculate summary statistics and find best/worst days
        if sales_data:
            best_day = max(sales_data, key=lambda x: x.get('total_sales', 0))
            worst_day = min(sales_data, key=lambda x: x.get('total_sales', 0))
            
            total_sales = sum(item.get('total_sales', 0) for item in sales_data)
            total_orders = sum(item.get('order_count', 0) for item in sales_data)
            
            return {
                "success": True,
                "message": f"Retrieved sales data by day of week{f' for year {year}' if year else ''}",
                "data": sales_data,
                "insights": {
                    "best_day": {
                        "day": best_day.get('day_name'),
                        "total_sales": best_day.get('total_sales'),
                        "order_count": best_day.get('order_count')
                    },
                    "worst_day": {
                        "day": worst_day.get('day_name'),
                        "total_sales": worst_day.get('total_sales'),
                        "order_count": worst_day.get('order_count')
                    },
                    "performance_ratio": round(best_day.get('total_sales', 0) / worst_day.get('total_sales', 1), 2)
                },
                "summary": {
                    "total_sales": round(total_sales, 2),
                    "total_orders": total_orders,
                    "average_daily_sales": round(total_sales / len(sales_data), 2),
                    "average_daily_orders": round(total_orders / len(sales_data), 2),
                    "year_filter": year
                }
            }
        else:
            return {
                "success": True,
                "message": "No sales data found",
                "data": [],
                "insights": None,
                "summary": None
            }
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving sales data by day: {str(e)}"
        )

@router.get("/analytics/sales/by-hour")
async def get_sales_by_hour(
    year: Optional[int] = Query(default=None, description="Filter by specific year (e.g., 2024)")
):
    """
    Get sales data grouped by hour of the day.
    
    Args:
        year: Filter by specific year (optional)
        
    Returns:
        dict: Sales data grouped by hour with peak performance insights
        
    Raises:
        HTTPException: If error occurs
    """
    try:
        sales_data = order_controller.get_sales_by_hour(year)
        
        # Calculate summary statistics and find peak hours
        if sales_data:
            peak_hour = max(sales_data, key=lambda x: x.get('total_sales', 0))
            low_hour = min(sales_data, key=lambda x: x.get('total_sales', 0))
            
            # Group by time periods for insights
            time_periods = {}
            for item in sales_data:
                period = item.get('time_period', 'Unknown')
                if period not in time_periods:
                    time_periods[period] = {'sales': 0, 'orders': 0}
                time_periods[period]['sales'] += item.get('total_sales', 0)
                time_periods[period]['orders'] += item.get('order_count', 0)
            
            best_period = max(time_periods.items(), key=lambda x: x[1]['sales'])
            
            total_sales = sum(item.get('total_sales', 0) for item in sales_data)
            total_orders = sum(item.get('order_count', 0) for item in sales_data)
            
            return {
                "success": True,
                "message": f"Retrieved sales data by hour{f' for year {year}' if year else ''}",
                "data": sales_data,
                "insights": {
                    "peak_hour": {
                        "hour": peak_hour.get('hour'),
                        "formatted_time": peak_hour.get('formatted_time'),
                        "total_sales": peak_hour.get('total_sales'),
                        "order_count": peak_hour.get('order_count'),
                        "time_period": peak_hour.get('time_period')
                    },
                    "lowest_hour": {
                        "hour": low_hour.get('hour'),
                        "formatted_time": low_hour.get('formatted_time'),
                        "total_sales": low_hour.get('total_sales'),
                        "order_count": low_hour.get('order_count'),
                        "time_period": low_hour.get('time_period')
                    },
                    "best_time_period": {
                        "period": best_period[0],
                        "total_sales": round(best_period[1]['sales'], 2),
                        "total_orders": best_period[1]['orders']
                    },
                    "time_period_breakdown": {k: {"sales": round(v['sales'], 2), "orders": v['orders']} for k, v in time_periods.items()}
                },
                "summary": {
                    "total_sales": round(total_sales, 2),
                    "total_orders": total_orders,
                    "average_hourly_sales": round(total_sales / len(sales_data), 2),
                    "average_hourly_orders": round(total_orders / len(sales_data), 2),
                    "year_filter": year
                }
            }
        else:
            return {
                "success": True,
                "message": "No sales data found",
                "data": [],
                "insights": None,
                "summary": None
            }
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving sales data by hour: {str(e)}"
        )

@router.get("/analytics/products/combos")
async def get_most_popular_product_combos(
    min_combo_size: int = Query(default=2, description="Minimum number of products in combination"),
    limit: int = Query(default=20, description="Maximum number of combinations to return")
):
    """
    Get most popular product combinations from orders.
    
    Args:
        min_combo_size: Minimum number of products in combination (default: 2)
        limit: Maximum number of combinations to return (default: 20)
        
    Returns:
        dict: Most popular product combinations with frequency and revenue data
        
    Raises:
        HTTPException: If error occurs
    """
    try:
        combo_data = order_controller.get_most_popular_product_combos(min_combo_size, limit)
        
        # Calculate summary statistics
        if combo_data:
            total_combinations = len(combo_data)
            total_combo_revenue = sum(item.get('total_revenue', 0) for item in combo_data)
            total_combo_frequency = sum(item.get('frequency', 0) for item in combo_data)
            
            # Find most valuable combo
            most_valuable = max(combo_data, key=lambda x: x.get('total_revenue', 0))
            most_frequent = max(combo_data, key=lambda x: x.get('frequency', 0))
            
            # Analyze combo sizes
            combo_sizes = {}
            for item in combo_data:
                size = item.get('combo_size', 0)
                if size not in combo_sizes:
                    combo_sizes[size] = {'count': 0, 'total_revenue': 0}
                combo_sizes[size]['count'] += 1
                combo_sizes[size]['total_revenue'] += item.get('total_revenue', 0)
            
            return {
                "success": True,
                "message": f"Retrieved top {total_combinations} product combinations",
                "data": combo_data,
                "insights": {
                    "most_frequent_combo": {
                        "products": most_frequent.get('product_combination'),
                        "frequency": most_frequent.get('frequency'),
                        "total_revenue": most_frequent.get('total_revenue'),
                        "combo_size": most_frequent.get('combo_size')
                    },
                    "most_valuable_combo": {
                        "products": most_valuable.get('product_combination'),
                        "frequency": most_valuable.get('frequency'),
                        "total_revenue": most_valuable.get('total_revenue'),
                        "combo_size": most_valuable.get('combo_size')
                    },
                    "combo_size_breakdown": {
                        str(k): {
                            "count": v['count'], 
                            "total_revenue": round(v['total_revenue'], 2),
                            "avg_revenue_per_combo": round(v['total_revenue'] / v['count'], 2)
                        } for k, v in combo_sizes.items()
                    }
                },
                "summary": {
                    "total_combinations_found": total_combinations,
                    "total_combo_revenue": round(total_combo_revenue, 2),
                    "total_combo_frequency": total_combo_frequency,
                    "average_revenue_per_combo": round(total_combo_revenue / total_combinations, 2),
                    "average_frequency": round(total_combo_frequency / total_combinations, 2),
                    "filters": {
                        "min_combo_size": min_combo_size,
                        "limit": limit
                    }
                }
            }
        else:
            return {
                "success": True,
                "message": f"No product combinations found with minimum size {min_combo_size}",
                "data": [],
                "insights": None,
                "summary": {
                    "total_combinations_found": 0,
                    "filters": {
                        "min_combo_size": min_combo_size,
                        "limit": limit
                    }
                }
            }
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving product combinations: {str(e)}"
        ) 

@router.get("/analytics/total-orders")
async def get_total_orders():
    """
    Get the total number of orders and comprehensive order statistics.
    
    Returns:
        dict: Total order count and comprehensive statistics including revenue, tax, discounts, and date range
        
    Raises:
        HTTPException: If error occurs
    """
    try:
        order_stats = order_controller.get_total_orders()
        
        # Enhance response with additional insights
        total_orders = order_stats.get('total_orders', 0)
        total_revenue = order_stats.get('total_revenue', 0)
        
        insights = {}
        if total_orders > 0:
            insights = {
                "revenue_per_order": round(total_revenue / total_orders, 2),
                "has_order_data": True,
                "date_range": {
                    "earliest_order": order_stats.get('earliest_order'),
                    "latest_order": order_stats.get('latest_order')
                }
            }
        else:
            insights = {
                "has_order_data": False,
                "message": "No orders found in the database"
            }
        
        return {
            "success": True,
            "message": f"Total orders: {total_orders}",
            "data": order_stats,
            "insights": insights
        }
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving total orders: {str(e)}"
        )

@router.get("/analytics/average-order-value")
async def get_average_order_value():
    """
    Get the average order value and comprehensive order value statistics.
    
    Returns:
        dict: Average order value with detailed statistics including min/max values, revenue insights
        
    Raises:
        HTTPException: If error occurs
    """
    try:
        aov_stats = order_controller.get_average_order_value()
        
        # Enhance response with additional insights and categorization
        total_orders = aov_stats.get('total_orders', 0)
        avg_order_value = aov_stats.get('average_order_value', 0)
        min_value = aov_stats.get('min_order_value', 0)
        max_value = aov_stats.get('max_order_value', 0)
        
        insights = {}
        if total_orders > 0:
            # Categorize order value performance
            if avg_order_value < 50:
                value_category = "Low"
            elif avg_order_value < 150:
                value_category = "Medium"
            elif avg_order_value < 300:
                value_category = "High"
            else:
                value_category = "Premium"
            
            insights = {
                "value_category": value_category,
                "value_distribution": {
                    "range_size": aov_stats.get('order_value_range', 0),
                    "min_to_avg_ratio": round(min_value / avg_order_value if avg_order_value > 0 else 0, 2),
                    "max_to_avg_ratio": round(max_value / avg_order_value if avg_order_value > 0 else 0, 2)
                },
                "revenue_insights": {
                    "total_revenue": aov_stats.get('total_revenue', 0),
                    "revenue_per_order": aov_stats.get('revenue_per_order', 0),
                    "average_subtotal": aov_stats.get('average_subtotal_value', 0)
                },
                "has_order_data": True
            }
        else:
            insights = {
                "has_order_data": False,
                "message": "No orders found in the database"
            }
        
        return {
            "success": True,
            "message": f"Average order value: ${avg_order_value}",
            "data": aov_stats,
            "insights": insights
        }
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving average order value: {str(e)}"
        )

@router.get("/analytics/monthly-order-data")
async def get_monthly_order_data(
    year: Optional[int] = Query(default=None, description="Filter by specific year (e.g., 2024)")
):
    """
    Get monthly order data with total orders, total revenue, and average order value per month.
    
    Args:
        year: Filter by specific year (optional)
        
    Returns:
        dict: Monthly order data with comprehensive statistics and insights
        
    Raises:
        HTTPException: If error occurs
    """
    try:
        monthly_data = order_controller.get_monthly_order_data(year)
        
        # Calculate comprehensive summary statistics
        if monthly_data:
            # Overall totals
            total_orders_all_months = sum(item.get('total_orders', 0) for item in monthly_data)
            total_revenue_all_months = sum(item.get('total_revenue', 0) for item in monthly_data)
            total_sales_all_months = sum(item.get('total_sales', 0) for item in monthly_data)
            
            # Calculate overall average order value
            overall_aov = round(total_sales_all_months / total_orders_all_months if total_orders_all_months > 0 else 0, 2)
            
            # Find best and worst performing months
            best_revenue_month = max(monthly_data, key=lambda x: x.get('total_revenue', 0))
            worst_revenue_month = min(monthly_data, key=lambda x: x.get('total_revenue', 0))
            
            best_orders_month = max(monthly_data, key=lambda x: x.get('total_orders', 0))
            worst_orders_month = min(monthly_data, key=lambda x: x.get('total_orders', 0))
            
            best_aov_month = max(monthly_data, key=lambda x: x.get('average_order_value', 0))
            worst_aov_month = min(monthly_data, key=lambda x: x.get('average_order_value', 0))
            
            # Calculate growth trends (comparing consecutive months)
            growth_trends = []
            for i in range(1, len(monthly_data)):
                prev_month = monthly_data[i-1]
                curr_month = monthly_data[i]
                
                revenue_growth = ((curr_month.get('total_revenue', 0) - prev_month.get('total_revenue', 0)) / prev_month.get('total_revenue', 1)) * 100
                orders_growth = ((curr_month.get('total_orders', 0) - prev_month.get('total_orders', 0)) / prev_month.get('total_orders', 1)) * 100
                aov_growth = ((curr_month.get('average_order_value', 0) - prev_month.get('average_order_value', 0)) / prev_month.get('average_order_value', 1)) * 100
                
                growth_trends.append({
                    "month": curr_month.get('month_name'),
                    "year": curr_month.get('year'),
                    "revenue_growth_percent": round(revenue_growth, 2),
                    "orders_growth_percent": round(orders_growth, 2),
                    "aov_growth_percent": round(aov_growth, 2)
                })
            
            # Monthly averages
            total_months = len(monthly_data)
            avg_orders_per_month = round(total_orders_all_months / total_months, 1)
            avg_revenue_per_month = round(total_revenue_all_months / total_months, 2)
            
            return {
                "success": True,
                "message": f"Retrieved monthly order data for {total_months} months{f' in {year}' if year else ''}",
                "data": monthly_data,
                "insights": {
                    "best_performance": {
                        "highest_revenue_month": {
                            "month": best_revenue_month.get('month_name'),
                            "year": best_revenue_month.get('year'),
                            "total_revenue": best_revenue_month.get('total_revenue'),
                            "total_orders": best_revenue_month.get('total_orders'),
                            "average_order_value": best_revenue_month.get('average_order_value')
                        },
                        "highest_orders_month": {
                            "month": best_orders_month.get('month_name'),
                            "year": best_orders_month.get('year'),
                            "total_orders": best_orders_month.get('total_orders'),
                            "total_revenue": best_orders_month.get('total_revenue'),
                            "average_order_value": best_orders_month.get('average_order_value')
                        },
                        "highest_aov_month": {
                            "month": best_aov_month.get('month_name'),
                            "year": best_aov_month.get('year'),
                            "average_order_value": best_aov_month.get('average_order_value'),
                            "total_orders": best_aov_month.get('total_orders'),
                            "total_revenue": best_aov_month.get('total_revenue')
                        }
                    },
                    "worst_performance": {
                        "lowest_revenue_month": {
                            "month": worst_revenue_month.get('month_name'),
                            "year": worst_revenue_month.get('year'),
                            "total_revenue": worst_revenue_month.get('total_revenue')
                        },
                        "lowest_orders_month": {
                            "month": worst_orders_month.get('month_name'),
                            "year": worst_orders_month.get('year'),
                            "total_orders": worst_orders_month.get('total_orders')
                        },
                        "lowest_aov_month": {
                            "month": worst_aov_month.get('month_name'),
                            "year": worst_aov_month.get('year'),
                            "average_order_value": worst_aov_month.get('average_order_value')
                        }
                    },
                    "growth_trends": growth_trends[-3:] if len(growth_trends) > 3 else growth_trends  # Show last 3 months growth
                },
                "summary": {
                    "total_months_analyzed": total_months,
                    "total_orders_all_months": total_orders_all_months,
                    "total_revenue_all_months": round(total_revenue_all_months, 2),
                    "total_sales_all_months": round(total_sales_all_months, 2),
                    "overall_average_order_value": overall_aov,
                    "average_orders_per_month": avg_orders_per_month,
                    "average_revenue_per_month": avg_revenue_per_month,
                    "revenue_range": {
                        "highest_month_revenue": best_revenue_month.get('total_revenue'),
                        "lowest_month_revenue": worst_revenue_month.get('total_revenue'),
                        "range": round(best_revenue_month.get('total_revenue', 0) - worst_revenue_month.get('total_revenue', 0), 2)
                    },
                    "orders_range": {
                        "highest_month_orders": best_orders_month.get('total_orders'),
                        "lowest_month_orders": worst_orders_month.get('total_orders'),
                        "range": best_orders_month.get('total_orders', 0) - worst_orders_month.get('total_orders', 0)
                    },
                    "aov_range": {
                        "highest_month_aov": best_aov_month.get('average_order_value'),
                        "lowest_month_aov": worst_aov_month.get('average_order_value'),
                        "range": round(best_aov_month.get('average_order_value', 0) - worst_aov_month.get('average_order_value', 0), 2)
                    },
                    "year_filter": year
                }
            }
        else:
            return {
                "success": True,
                "message": f"No monthly order data found{f' for year {year}' if year else ''}",
                "data": [],
                "insights": None,
                "summary": {
                    "total_months_analyzed": 0,
                    "total_orders_all_months": 0,
                    "total_revenue_all_months": 0,
                    "overall_average_order_value": 0,
                    "year_filter": year
                }
            }
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving monthly order data: {str(e)}"
        ) 