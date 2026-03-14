"""
Payments router — Pine Labs webhook receiver.

Pine Labs calls POST /payments/webhook when a payment completes.
We look up the order by pine_labs_order_id and update its status.
"""

import logging

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from ..dependencies import get_db
from ..models.order import Order
from ..services import order_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/webhook")
async def pine_labs_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Receive payment status callbacks from Pine Labs.
    Expected body contains at minimum: order_id, status.
    """
    try:
        body = await request.json()
    except Exception:
        return {"status": "ignored"}

    pine_order_id = body.get("order_id") or body.get("id")
    raw_status = body.get("status") or body.get("order_status", "")

    logger.info("Pine Labs webhook: order=%s status=%s", pine_order_id, raw_status)

    if not pine_order_id:
        return {"status": "ignored"}

    order: Order | None = db.query(Order).filter(Order.pine_labs_order_id == pine_order_id).first()
    if order:
        order.payment_status = raw_status
        if raw_status in ("CHARGED", "SUCCESS", "CAPTURED"):
            order.status = "confirmed"
        elif raw_status in ("FAILED", "CANCELLED", "EXPIRED"):
            order.status = "cancelled"
        db.commit()

    return {"status": "ok"}
