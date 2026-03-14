from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..dependencies import get_db, get_current_user
from ..models.user import User
from ..schemas.order import OrderOut
from ..services import order_service
from ..services.payment_service import PaymentError

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", response_model=OrderOut, status_code=201)
def create_order(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return order_service.create_order_from_cart(db, current_user)


@router.get("/", response_model=list[OrderOut])
def list_orders(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return order_service.list_orders(db, current_user.id)


@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    order = order_service.get_order(db, current_user.id, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.post("/{order_id}/sync-payment", response_model=OrderOut)
def sync_payment(order_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Poll Pine Labs for latest payment status and update the order."""
    order = order_service.get_order(db, current_user.id, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order_service.sync_payment_status(db, order)


@router.post("/{order_id}/refund", response_model=OrderOut)
def refund_order(order_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Issue a full refund for a confirmed order."""
    order = order_service.get_order(db, current_user.id, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status not in ("confirmed", "shipped"):
        raise HTTPException(status_code=400, detail=f"Cannot refund order in status '{order.status}'")
    try:
        return order_service.refund_order(db, order)
    except PaymentError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail)
