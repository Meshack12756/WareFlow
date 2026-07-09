from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.redis_client import redis_client
from app.core.auth import require_role, get_current_user
from app.database.connection import get_db
from app.utils.cache import cache
from app.database.models import Product, Employee, SaleItem
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse

router = APIRouter()

@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_role("admin"))
):
    """Create a new product (Admin only)"""
    existing = db.query(Product).filter(Product.sku == product.sku).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SKU already exists"
        )
    
    new_product = Product(**product.dict())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    redis_client.delete_pattern("get_products:*")
    redis_client.delete_pattern("get_low_stock:*")
    return new_product

@router.get("", response_model=List[ProductResponse])
#@cache(ttl=60)
async def get_products(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Get all products (Any authenticated user)"""
    products = db.query(Product).offset(skip).limit(limit).all()
    return products

@router.get("/{product_id}", response_model=None)
async def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Get a product by ID"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.put("/{product_id}", response_model=None)
async def update_product(
    product_id: int,
    product_update: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_role("admin"))
):
    """Update a product (Admin only)"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    update_data = product_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)
    
    db.commit()
    db.refresh(product)
    return product

@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_role("admin"))
):
    """Delete a product (Admin only)"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    sales_items = db.query(SaleItem).filter(SaleItem.product_id == product_id).first()
    if sales_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete product with existing sales history. Deactivate instead."
        )
    db.delete(product)
    db.commit()
    return {"message": "Product deleted successfully"}

