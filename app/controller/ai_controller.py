from app.repository.product_repository import ProductRepository
from app.repository.order_repository import OrderRepository

class AiController:
    def __init__(self):
        self.product_repository = ProductRepository()
        self.order_repository = OrderRepository()

    def top_selling_products_by_unit_sold(self,limit:int=10):
        """
        Get the top selling products by unit sold.
        Args:
            limit: The number of products to return.
        Returns:
            list[dict]: List of products with their unit sold.
        """
        products = self.product_repository.get_top_selling_products_by_unit_sold(limit)
        return products
    