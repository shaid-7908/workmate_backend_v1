from app.repository.product_repository import ProductRepository
from app.model.product_schema import ProductSchema
from app.types.product_types import ProductCreateSchema

class ProductController:
    """Controller for product business logic."""
    
    def __init__(self):
        self.repository = ProductRepository()
    
    def create_product(self, product_data: ProductCreateSchema) -> dict[str, object]:
        """
        Create a new product.
        
        Args:
            product_data: Product data to create
            
        Returns:
            dict: Created product with MongoDB _id
            
        Raises:
            Exception: If product creation fails
        """
        return self.repository.create_product(product_data)
    
    def create_product_with_schema(self, product: ProductSchema) -> dict[str, object]:
        """
        Create a new product using ProductSchema instance.
        
        Args:
            product: ProductSchema instance with validated data
            
        Returns:
            dict: Created product with MongoDB _id
            
        Raises:
            Exception: If product creation fails
        """
        return self.repository.create_product_with_schema(product)
    
    def get_product_by_id(self, product_id: str) -> dict[str, object] | None:
        """
        Get a product by its MongoDB _id.
        
        Args:
            product_id: Product ID as string
            
        Returns:
            dict | None: Product data or None if not found
        """
        return self.repository.get_product_by_id(product_id)
    
    def get_products_by_store(self, store_id: str) -> list[dict[str, object]]:
        """
        Get all products for a specific store.
        
        Args:
            store_id: Store ID as string
            
        Returns:
            list[dict]: List of products for the store
        """
        return self.repository.get_products_by_store(store_id)
    
    def update_product(self, product_id: str, product_data: dict[str, object]) -> dict[str, object] | None:
        """
        Update a product by its ID.
        
        Args:
            product_id: Product ID as string
            product_data: Updated product data
            
        Returns:
            dict | None: Updated product data or None if not found
            
        Raises:
            Exception: If update fails
        """
        # TODO: Implement update logic in repository
        # For now, return None to indicate not implemented
        return None
    
    def delete_product(self, product_id: str) -> bool:
        """
        Delete a product by its ID.
        
        Args:
            product_id: Product ID as string
            
        Returns:
            bool: True if deleted successfully, False otherwise
            
        Raises:
            Exception: If deletion fails
        """
        # TODO: Implement delete logic in repository
        # For now, return False to indicate not implemented
        return False
