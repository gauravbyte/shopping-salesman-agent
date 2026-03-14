from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..dependencies import get_db, get_current_admin
from ..schemas.product import ProductCreate, ProductUpdate, ProductOut, CategoryCreate, CategoryOut
from ..services import product_service

router = APIRouter(tags=["products"])


@router.get("/products", response_model=list[ProductOut])
def list_products(
    category: str | None = None,
    search: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    return product_service.list_products(db, category, search, min_price, max_price, skip, limit)


@router.get("/products/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = product_service.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/products", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(data: ProductCreate, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    return product_service.create_product(db, data)


@router.put("/products/{product_id}", response_model=ProductOut)
def update_product(product_id: int, data: ProductUpdate, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    product = product_service.update_product(db, product_id, data)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    if not product_service.delete_product(db, product_id):
        raise HTTPException(status_code=404, detail="Product not found")


@router.get("/categories", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return product_service.list_categories(db)


@router.post("/categories", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(data: CategoryCreate, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    return product_service.create_category(db, data.name, data.slug)
