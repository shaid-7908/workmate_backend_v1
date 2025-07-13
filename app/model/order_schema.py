from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, timezone
from typing import List, Optional, ClassVar
from bson import ObjectId


class OrderLineItem(BaseModel):
    product_id: int
    variant_id: int
    quantity: int
    total_discount: float = 0.0
    requires_shipping: bool = False

class CustomerInfo(BaseModel):
    customer_id: int
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    tags: List[str] = []
    created_at: datetime
    verified_email: bool = True

class Address(BaseModel):
    first_name: str
    last_name: str
    address1: str
    address2: Optional[str] = None
    city: str
    zip: str
    province: Optional[str] = None
    country: str
    country_code: str
    phone: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class OrderSchema(BaseModel):
    order_id: int
    order_number: int
    name: str
    created_at: datetime
    processed_at: Optional[datetime] = None
    updated_at: datetime

    financial_status: str
    fulfillment_status: Optional[str] = None
    currency: str

    subtotal_price: float
    total_price: float
    total_tax: float
    total_discounts: float

    line_items: List[OrderLineItem]
    customer: CustomerInfo
    billing_address: Optional[Address] = None
    shipping_address: Optional[Address] = None

    tags: List[str] = []
    source_name: Optional[str] = None
    email: Optional[str] = None

    __collection_name__: ClassVar[str] = "shopify_orders"

    model_config: ClassVar[ConfigDict] = {
        "title": "OrderSchema",
        "populate_by_name": True,
        "json_encoders": {ObjectId: str}
    }
