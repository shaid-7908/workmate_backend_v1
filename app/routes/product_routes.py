from fastapi import APIRouter, HTTPException, status
from app.model.product_schema import ProductSchema
from app.types.product_types import ProductCreateSchema, ProductUpdateSchema
from app.controller.product_controller import ProductController
from pydantic import BaseModel
from typing import Dict, Any
from app.llmfunc.product_analyzer import ProductAnalyzer

class ProductAnalysisRequest(BaseModel):
        product_data: Dict[str, Any]
        analysis_type: str = "comprehensive"

# Create router
router = APIRouter(
    prefix="/api/products",
    tags=["products"],
    responses={404: {"description": "Not found"}}
)

# Initialize controller
product_controller = ProductController()


@router.post("/ai/analyze-product")
async def analyze_product(request: ProductAnalysisRequest):
        """Analyze a product using AI."""
        try:
            analyzer = ProductAnalyzer()
            result = analyzer.analyze_product(
                request.product_data, 
                request.analysis_type
            )
            return {"success": True, "analysis": result}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_new_product(product_data: ProductCreateSchema):
    """
    Create a new product.
    
    Args:
        product_data: Product data including variants, vendor, tags, etc.
        
    Returns:
        dict: Created product with MongoDB _id
        
    Raises:
        HTTPException: If product creation fails
    """
    try:
        created_product = product_controller.create_product(product_data)
        return {
            "success": True,
            "message": "Product created successfully",
            "data": created_product
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create product: {str(e)}"
        )

@router.post("/from-shopify", status_code=status.HTTP_201_CREATED)
async def create_product_from_shopify():
    product_controller.create_product_from_shopify()
    return {
        "success": True,
        "message": "Product created successfully"
    }

@router.post("/with-schema", status_code=status.HTTP_201_CREATED)
async def create_product_using_schema(product: ProductSchema):
    """
    Create a new product using ProductSchema validation.
    
    Args:
        product: ProductSchema instance with validated data
        
    Returns:
        dict: Created product with MongoDB _id
        
    Raises:
        HTTPException: If product creation fails
    """
    try:
        created_product = product_controller.create_product_with_schema(product)
        return {
            "success": True,
            "message": "Product created successfully",
            "data": created_product
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create product: {str(e)}"
        )

@router.get("/get-product-by-id/{product_id}")
async def get_product(product_id: str):
    """
    Get a product by its ID.
    
    Args:
        product_id: Product ID as string
        
    Returns:
        dict: Product data or error message
        
    Raises:
        HTTPException: If product not found
    """
    try:
        product = product_controller.get_product_by_id(product_id)
        if product:
            return {
                "success": True,
                "message": "Product retrieved successfully",
                "data": product
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {product_id} not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving product: {str(e)}"
        )

@router.get("/store/{store_id}")
async def get_products_by_store_id(store_id: str):
    """
    Get all products for a specific store.
    
    Args:
        store_id: Store ID as string
        
    Returns:
        dict: List of products for the store
        
    Raises:
        HTTPException: If error occurs
    """
    try:
        products = product_controller.get_products_by_store(store_id)
        return {
            "success": True,
            "message": f"Retrieved {len(products)} products for store {store_id}",
            "data": products,
            "count": len(products)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving products for store: {str(e)}"
        )

@router.get("/")
async def get_all_products():
    """
    Get all products (placeholder for pagination).
    
    Returns:
        dict: List of all products
        
    Raises:
        HTTPException: If error occurs
    """
    print("Getting all products =================================")
    try:
        # This is a placeholder - you might want to add pagination
        # For now, we'll return a message indicating this endpoint needs implementation
        return {
            "success": True,
            "message": "Get all products endpoint - implement pagination",
            "data": [],
            "count": 0
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving products: {str(e)}"
        )

@router.get("/units-sold")
async def get_units_sold_per_product():
    """
    Get total units sold per product by aggregating all order line items.
    
    Returns:
        dict: List with product analytics including total units sold, orders count, and revenue
        
    Raises:
        HTTPException: If error occurs
    """
    print("Getting total units sold per product =================================")
    try:
        units_sold_data = product_controller.get_total_units_sold_per_product()
        return {
            "success": True,
            "message": f"Retrieved sales data for {len(units_sold_data)} products",
            "data": units_sold_data,
            "count": len(units_sold_data)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving units sold per product: {str(e)}"
        )

@router.get("/revenue")
async def get_revenue_per_product():
    """
    Get total revenue per product by proportionally distributing order totals.
    
    Returns:
        dict: List with product revenue analytics including total revenue, quantities, and average price
        
    Raises:
        HTTPException: If error occurs
    """
    print("Getting total revenue per product =================================")
    try:
        revenue_data = product_controller.get_total_revenue_per_product()
        return {
            "success": True,
            "message": f"Retrieved revenue data for {len(revenue_data)} products",
            "data": revenue_data,
            "count": len(revenue_data)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving revenue per product: {str(e)}"
        )

@router.put("/update-product-by-id/{product_id}")
async def update_product(product_id: str, product_data: ProductUpdateSchema):
    """
    Update a product by its ID.
    
    Args:
        product_id: Product ID as string
        product_data: Updated product data
        
    Returns:
        dict: Updated product data
        
    Raises:
        HTTPException: If product not found or update fails
    """
    try:
        # First check if product exists
        existing_product = product_controller.get_product_by_id(product_id)
        if not existing_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {product_id} not found"
            )
        
        # TODO: Implement update logic in controller
        # For now, return a placeholder response
        return {
            "success": True,
            "message": "Product update endpoint - implement in controller",
            "data": existing_product
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating product: {str(e)}"
        )

@router.delete("/{product_id}")
async def delete_product(product_id: str):
    """
    Delete a product by its ID.
    
    Args:
        product_id: Product ID as string
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException: If product not found or deletion fails
    """
    try:
        # First check if product exists
        existing_product = product_controller.get_product_by_id(product_id)
        if not existing_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {product_id} not found"
            )
        
        # TODO: Implement delete logic in controller
        # For now, return a placeholder response
        return {
            "success": True,
            "message": "Product delete endpoint - implement in controller",
            "data": {"deleted_id": product_id}
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting product: {str(e)}"
        ) 