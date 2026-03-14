from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from ..models.cart import Cart, CartItem
from ..models.product import Product


def get_or_create_cart(db: Session, user_id: int) -> Cart:
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        cart = Cart(user_id=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart


def add_item(db: Session, user_id: int, product_id: int, quantity: int) -> Cart:
    cart = get_or_create_cart(db, user_id)
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    existing = db.query(CartItem).filter(CartItem.cart_id == cart.id, CartItem.product_id == product_id).first()
    if existing:
        existing.quantity += quantity
    else:
        item = CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity)
        db.add(item)

    db.commit()
    db.refresh(cart)
    return cart


def update_item(db: Session, user_id: int, item_id: int, quantity: int) -> Cart:
    cart = get_or_create_cart(db, user_id)
    item = db.query(CartItem).filter(CartItem.id == item_id, CartItem.cart_id == cart.id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")
    item.quantity = quantity
    db.commit()
    db.refresh(cart)
    return cart


def remove_item(db: Session, user_id: int, item_id: int) -> Cart:
    cart = get_or_create_cart(db, user_id)
    item = db.query(CartItem).filter(CartItem.id == item_id, CartItem.cart_id == cart.id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")
    db.delete(item)
    db.commit()
    db.refresh(cart)
    return cart


def clear_cart(db: Session, user_id: int) -> Cart:
    cart = get_or_create_cart(db, user_id)
    for item in cart.items:
        db.delete(item)
    db.commit()
    db.refresh(cart)
    return cart


def cart_total(cart: Cart) -> float:
    return sum(item.quantity * item.product.price for item in cart.items)
