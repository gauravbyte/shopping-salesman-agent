from typing import Optional
from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)
    # Order lifecycle: pending → payment_initiated → confirmed → shipped → delivered / cancelled
    status: Mapped[str] = mapped_column(String, default="pending")
    # Pine Labs fields (null until payment is initiated)
    pine_labs_order_id: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    checkout_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    payment_status: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # raw status from Pine Labs

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
