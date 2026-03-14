from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..dependencies import get_db, get_current_user
from ..models.user import User
from ..schemas.cart import CartOut, CartItemAdd, CartItemUpdate
from ..services import cart_service

router = APIRouter(prefix="/cart", tags=["cart"])


def _cart_out(cart, db) -> CartOut:
    db.refresh(cart)
    return CartOut(
        id=cart.id,
        items=cart.items,
        total=cart_service.cart_total(cart),
    )


@router.get("/", response_model=CartOut)
def get_cart(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cart = cart_service.get_or_create_cart(db, current_user.id)
    return _cart_out(cart, db)


@router.post("/items", response_model=CartOut)
def add_item(data: CartItemAdd, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cart = cart_service.add_item(db, current_user.id, data.product_id, data.quantity)
    return _cart_out(cart, db)


@router.put("/items/{item_id}", response_model=CartOut)
def update_item(item_id: int, data: CartItemUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cart = cart_service.update_item(db, current_user.id, item_id, data.quantity)
    return _cart_out(cart, db)


@router.delete("/items/{item_id}", response_model=CartOut)
def remove_item(item_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cart = cart_service.remove_item(db, current_user.id, item_id)
    return _cart_out(cart, db)


@router.delete("/", response_model=CartOut)
def clear_cart(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cart = cart_service.clear_cart(db, current_user.id)
    return _cart_out(cart, db)
