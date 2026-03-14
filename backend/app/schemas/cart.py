from pydantic import BaseModel
from .product import ProductOut


class CartItemAdd(BaseModel):
    product_id: int
    quantity: int = 1


class CartItemUpdate(BaseModel):
    quantity: int


class CartItemOut(BaseModel):
    id: int
    product: ProductOut
    quantity: int

    model_config = {"from_attributes": True}


class CartOut(BaseModel):
    id: int
    items: list[CartItemOut]
    total: float

    model_config = {"from_attributes": True}
