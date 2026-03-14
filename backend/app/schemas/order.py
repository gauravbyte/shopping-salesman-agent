from pydantic import BaseModel
from .product import ProductOut


class OrderItemOut(BaseModel):
    id: int
    product: ProductOut
    quantity: int
    unit_price: float

    model_config = {"from_attributes": True}


class OrderOut(BaseModel):
    id: int
    total_amount: float
    status: str
    items: list[OrderItemOut]
    pine_labs_order_id: str | None = None
    checkout_url: str | None = None
    payment_status: str | None = None

    model_config = {"from_attributes": True}
