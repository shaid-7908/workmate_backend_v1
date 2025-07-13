from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import ClassVar

class ProductVariantCreateSchema(BaseModel):
    variantId: int
    sku: str
    price: str
    inventory_quantity: int = Field(ge=0)

class ProductCreateSchema(BaseModel):
    productId: int
    title: str
    variants: list[ProductVariantCreateSchema]
    vendor: str
    tags: list[str] = []
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ProductUpdateSchema(BaseModel):
    productId: int | None = None
    title: str | None = None
    variants: list[ProductVariantCreateSchema] | None = None
    vendor: str | None = None
    tags: list[str] | None = None
    updatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
