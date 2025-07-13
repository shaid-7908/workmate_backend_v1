from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, timezone
from bson import ObjectId
from typing import ClassVar

class ProductVariantSchema(BaseModel):
    variantId: int
    sku: str
    price: str
    inventory_quantity: int = Field(ge=0)

class ProductImageSchema(BaseModel):
    image_url: str
    image_alt_text: str = Field(default="")
    image_type: str = Field(default="main")
    image_order: int = Field(default=0)
    is_primary: bool = Field(default=False)
    file_size: int | None = Field(None)
    dimensions: dict[str, int] | None = Field(None)
    mime_type: str | None = Field(None)

class ProductSchema(BaseModel):  # Optional _id, set by MongoDB
    productId: int
    title: str
    variants: list[ProductVariantSchema]
    images: list[ProductImageSchema] = []
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
