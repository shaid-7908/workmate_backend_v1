from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, timezone
from bson import ObjectId
from typing import ClassVar

class ProductVariantSchema(BaseModel):
    variantId: int
    sku: str
    price: str
    inventory_quantity: int = Field(ge=0)

class ProductSchema(BaseModel):  # Optional _id, set by MongoDB
    productId: int
    title: str
    variants: list[ProductVariantSchema]
    vendor: str
    tags: list[str] = []
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Collection name (like Mongoose model name)
    __collection_name__: ClassVar[str] = "shopify_products"

    model_config: ClassVar[ConfigDict] = {
        "title": "ProductSchema",
        "populate_by_name": True,
        "json_encoders": {ObjectId: str}
    }
