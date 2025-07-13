from app import config
from app.repository.product_repository import ProductRepository
from app.model.product_schema import ProductSchema
from app.types.product_types import ProductCreateSchema, ProductVariantCreateSchema, ProductImageCreateSchema
from app.config.env_config import Config
import requests
from pprint import pprint
from datetime import datetime

class ProductController:
    """Controller for product business logic."""
    
    def __init__(self):
        self.repository = ProductRepository()
        self.config = Config()

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

    def get_products_from_shopify(self):
        url = f"https://{self.config.SHOPIFY_STORE_NAME}/admin/api/2023-10/products.json"
        headers = {
            "X-Shopify-Access-Token": self.config.SHOPIFY_ACCESS_TOKEN
        }
        response = requests.get(url, headers=headers)
        return response.json()

    def create_product_from_shopify(self):
        """
        Create a new product from Shopify data.
        
        Args:
            product_datas: List of product data to create
        """
        product_datas = self.get_products_from_shopify()
        print(product_datas['products'])
        for product_data in product_datas['products']:
            pprint(product_data,sort_dicts=False)
            
            # Transform Shopify variants to match our schema
            transformed_variants = []
            for variant in product_data['variants']:
                variant_schema = ProductVariantCreateSchema(
                    variantId=variant['id'],
                    sku=variant['sku'] or "",
                    price=variant['price'],
                    inventory_quantity=variant['inventory_quantity']
                )
                transformed_variants.append(variant_schema)
            
            # Transform Shopify images to match our schema
            transformed_images = []
            for i, image in enumerate(product_data.get('images', [])):
                image_schema = ProductImageCreateSchema(
                    image_url=image['src'],
                    image_alt_text=image.get('alt', ""),
                    image_type="main" if i == 0 else "gallery",
                    image_order=i,
                    is_primary=i == 0,  # First image is primary
                    file_size=image.get('width', 0) * image.get('height', 0) if image.get('width') and image.get('height') else None,
                    dimensions={
                        "width": image.get('width', 0),
                        "height": image.get('height', 0)
                    } if image.get('width') and image.get('height') else None,
                    mime_type="image/jpeg"  # Default, could be extracted from URL
                )
                transformed_images.append(image_schema)
            
            # Transform Shopify data to match our schema
            data_to_create = {
                "productId": product_data['id'],
                "title": product_data['title'],
                "variants": transformed_variants,
                "images": transformed_images,
                "vendor": product_data['vendor'],
                "tags": product_data['tags'].split(',') if product_data['tags'] else [],
                "createdAt": datetime.fromisoformat(product_data['created_at'].replace('Z', '+00:00')),
                "updatedAt": datetime.fromisoformat(product_data['updated_at'].replace('Z', '+00:00')),
            }
            
            # Create ProductCreateSchema instance from the data
            product_schema = ProductCreateSchema(**data_to_create)
            self.create_product(product_schema)
            print("-" * 80)
    
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
