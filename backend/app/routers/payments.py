"""
Payments router — Pine Labs webhook receiver.

Pine Labs calls POST /payments/webhook when a payment completes.
We look up the order by pine_labs_order_id and update its status.
"""

import logging

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from ..core.config import settings
from ..dependencies import get_db
from ..models.order import Order
from ..services import order_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payments", tags=["payments"])


@router.get("/return")
def payment_return_get():
    """
    Browser GET fallback for local/dev when /payment/return is opened directly.
    Redirect users to order history.
    """
    return RedirectResponse(url=f"{settings.FRONTEND_URL}/orders", status_code=303)


@router.post("/return")
async def payment_return(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Pine Labs POSTs form data here after the customer completes/cancels payment.
    We look up the order, sync status, then redirect the browser to the frontend.
    """
    form = await request.form()
    pine_order_id = form.get("order_id") or form.get("id")
    raw_status = str(form.get("status", "")).upper()

    logger.info("Pine Labs return: order=%s status=%s", pine_order_id, raw_status)

    # Find our internal order by Pine Labs order ID
    order: Order | None = (
        db.query(Order).filter(Order.pine_labs_order_id == pine_order_id).first()
        if pine_order_id else None
    )

    if order:
        # Persist status immediately from the return callback
        order.payment_status = raw_status
        if raw_status in ("CHARGED", "SUCCESS", "CAPTURED", "PROCESSED"):
            order.status = "confirmed"
        elif raw_status in ("FAILED", "CANCELLED", "EXPIRED"):
            order.status = "cancelled"
        db.commit()
        redirect_url = (
            f"{settings.FRONTEND_URL}/payment/return"
            f"?order_id={order.id}&status={raw_status}"
        )
    else:
        redirect_url = f"{settings.FRONTEND_URL}/orders"

    return RedirectResponse(url=redirect_url, status_code=303)


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
