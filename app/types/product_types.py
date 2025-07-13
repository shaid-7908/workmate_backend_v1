from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import ClassVar

class ProductVariantCreateSchema(BaseModel):
    variantId: int
    sku: str
    price: str
    inventory_quantity: int = Field(ge=0)

class ProductImageCreateSchema(BaseModel):
    image_url: str
    image_alt_text: str = Field(default="")
    image_type: str = Field(default="main")
    image_order: int = Field(default=0)
    is_primary: bool = Field(default=False)
    file_size: int | None = Field(None)
    dimensions: dict[str, int] | None = Field(None)
    mime_type: str | None = Field(None)

class ProductCreateSchema(BaseModel):
    productId: int
    title: str
    variants: list[ProductVariantCreateSchema]
    images: list[ProductImageCreateSchema] = []
    vendor: str
    tags: list[str] = []
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ProductUpdateSchema(BaseModel):
    productId: int | None = None
    title: str | None = None
    variants: list[ProductVariantCreateSchema] | None = None
    images: list[ProductImageCreateSchema] | None = None
    vendor: str | None = None
    tags: list[str] | None = None
    updatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
