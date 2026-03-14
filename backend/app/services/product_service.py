from __future__ import annotations
from sqlalchemy.orm import Session
from sqlalchemy import or_
from ..models.product import Product, Category
from ..schemas.product import ProductCreate, ProductUpdate


def list_products(
    db: Session,
    category: str | None = None,
    search: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    skip: int = 0,
    limit: int = 20,
) -> list[Product]:
    q = db.query(Product)
    if category:
        q = q.join(Product.category).filter(Category.slug == category)
    if search:
        q = q.filter(or_(Product.name.ilike(f"%{search}%"), Product.description.ilike(f"%{search}%")))
    if min_price is not None:
        q = q.filter(Product.price >= min_price)
    if max_price is not None:
        q = q.filter(Product.price <= max_price)
    return q.offset(skip).limit(limit).all()


def get_product(db: Session, product_id: int) -> Product | None:
    return db.get(Product, product_id)


def create_product(db: Session, data: ProductCreate) -> Product:
    product = Product(**data.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def update_product(db: Session, product_id: int, data: ProductUpdate) -> Product | None:
    product = db.get(Product, product_id)
    if not product:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product_id: int) -> bool:
    product = db.get(Product, product_id)
    if not product:
        return False
    db.delete(product)
    db.commit()
    return True


def list_categories(db: Session) -> list[Category]:
    return db.query(Category).all()


def create_category(db: Session, name: str, slug: str) -> Category:
    category = Category(name=name, slug=slug)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category
