from __future__ import annotations
import logging

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..models.order import Order, OrderItem
from ..models.user import User
from . import cart_service
from . import payment_service
from .payment_service import PaymentError

logger = logging.getLogger(__name__)


def create_order_from_cart(db: Session, user: User) -> Order:
    user_id = user.id
    cart = cart_service.get_or_create_cart(db, user_id)

    if not cart.items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cart is empty")

    # Validate stock and snapshot prices
    order_items_data = []
    total = 0.0
    for item in cart.items:
        product = item.product
        if product.stock < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for {product.name}",
            )
        order_items_data.append({
            "product_id": product.id,
            "quantity": item.quantity,
            "unit_price": product.price,
        })
        total += item.quantity * product.price

    # Decrement stock atomically
    for item in cart.items:
        item.product.stock -= item.quantity

    order = Order(user_id=user_id, total_amount=round(total, 2), status="pending")
    db.add(order)
    db.flush()  # get order.id

    for data in order_items_data:
        db.add(OrderItem(order_id=order.id, **data))

    # Clear cart
    for item in list(cart.items):
        db.delete(item)

    db.commit()
    db.refresh(order)

    # Initiate Pine Labs hosted checkout
    try:
        amount_paise = int(round(order.total_amount * 100))
        result = payment_service.hosted_checkout_create(
            merchant_order_reference=str(order.id),
            amount_paise=amount_paise,
            customer_email=user.email,
            customer_name=user.full_name,
        )
        order.pine_labs_order_id = result.get("order_id") or result.get("id")
        order.checkout_url = result.get("redirect_url") or result.get("checkout_url")
        order.status = "payment_initiated"
        db.commit()
        db.refresh(order)
    except PaymentError as exc:
        # Payment initiation failed — order is saved but stays in "pending" so
        # the user can retry from the order detail page.
        logger.warning("Pine Labs checkout initiation failed for order %s: %s", order.id, exc)

    return order


def list_orders(db: Session, user_id: int) -> list[Order]:
    return db.query(Order).filter(Order.user_id == user_id).all()


def get_order(db: Session, user_id: int, order_id: int) -> Order | None:
    return db.query(Order).filter(Order.id == order_id, Order.user_id == user_id).first()


def sync_payment_status(db: Session, order: Order) -> Order:
    """Poll Pine Labs for current payment status and persist it."""
    if not order.pine_labs_order_id:
        return order
    try:
        data = payment_service.get_order_status(order.pine_labs_order_id)
        raw_status = data.get("status") or data.get("order_status", "")
        order.payment_status = raw_status
        # Map Pine Labs statuses to our order statuses
        if raw_status in ("CHARGED", "SUCCESS", "CAPTURED"):
            order.status = "confirmed"
        elif raw_status in ("FAILED", "CANCELLED", "EXPIRED"):
            order.status = "cancelled"
        db.commit()
        db.refresh(order)
    except PaymentError as exc:
        logger.warning("Status sync failed for order %s: %s", order.id, exc)
    return order


def refund_order(db: Session, order: Order) -> Order:
    """Issue a full refund via Pine Labs and mark the order cancelled."""
    if not order.pine_labs_order_id:
        raise HTTPException(status_code=400, detail="No Pine Labs order ID — cannot refund")
    amount_paise = int(round(order.total_amount * 100))
    payment_service.create_refund(order.pine_labs_order_id, amount_paise)
    order.status = "cancelled"
    order.payment_status = "REFUNDED"
    db.commit()
    db.refresh(order)
    return order
