from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.core.auth import get_current_user, require_role
from app.database.connection import get_db
from app.database.models import Employee, Sale, Product, SaleItem

router = APIRouter()

@router.get("/sales/top-products")
async def get_top_products(
    days: int = 30,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("admin"))
):
    """Get top-selling products (Admin only)"""
    start_date = datetime.now() - timedelta(days=days)
    
    results = db.query(
        Product.id,
        Product.name,
        Product.sku,
        func.sum(SaleItem.quantity).label('total_quantity'),
        func.sum(SaleItem.unit_selling_price * SaleItem.quantity).label('total_revenue')
    ).join(
        SaleItem, SaleItem.product_id == Product.id
    ).join(
        Sale, Sale.id == SaleItem.sale_id
    ).filter(
        Sale.timestamp >= start_date
    ).group_by(
        Product.id, Product.name, Product.sku
    ).order_by(
        func.sum(SaleItem.quantity).desc()
    ).limit(limit).all()
    
    return [
        {
            "id": r.id,
            "name": r.name,
            "sku": r.sku,
            "total_quantity": r.total_quantity,
            "total_revenue": float(r.total_revenue)
        }
        for r in results
    ]

@router.get("/sales/daily")
async def get_daily_sales(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("admin"))
):
    """Get daily sales trends (Admin only)"""
    start_date = datetime.now() - timedelta(days=days)
    
    results = db.query(
        func.date(Sale.timestamp).label('date'),
        func.count(Sale.id).label('sales_count'),
        func.sum(Sale.total_amount).label('total_revenue'),
        func.sum(Sale.gross_profit).label('total_profit')
    ).filter(
        Sale.timestamp >= start_date
    ).group_by(
        func.date(Sale.timestamp)
    ).order_by(
        func.date(Sale.timestamp)
    ).all()
    
    return [
        {
            "date": r.date.isoformat(),
            "sales_count": r.sales_count,
            "total_revenue": float(r.total_revenue or 0),
            "total_profit": float(r.total_profit or 0)
        }
        for r in results
    ]

@router.get("/inventory/low-stock")
async def get_low_stock(
    threshold: int = 10,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("admin"))
):
    """Get products with low stock (Admin only)"""
    products = db.query(Product).filter(
        Product.stock_quantity <= threshold
    ).order_by(Product.stock_quantity).all()
    
    return [
        {
            "id": p.id,
            "name": p.name,
            "sku": p.sku,
            "stock_quantity": p.stock_quantity,
            "cost_price": float(p.cost_price),
            "selling_price": float(p.selling_price)
        }
        for p in products
    ]

@router.get("/employee/performance")
async def get_employee_performance(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("admin"))
):
    """Get employee performance metrics (Admin only)"""
    start_date = datetime.now() - timedelta(days=days)
    
    results = db.query(
        Employee.id,
        Employee.name,
        Employee.pay_model,
        func.count(Sale.id).label('sales_count'),
        func.sum(Sale.total_amount).label('total_revenue'),
        func.sum(Sale.gross_profit).label('total_profit'),
        func.avg(Sale.gross_profit).label('avg_profit_per_sale')
    ).join(
        Sale, Sale.employee_id == Employee.id
    ).filter(
        Sale.timestamp >= start_date
    ).group_by(
        Employee.id, Employee.name, Employee.pay_model
    ).order_by(
        func.sum(Sale.gross_profit).desc()
    ).all()
    
    return [
        {
            "id": r.id,
            "name": r.name,
            "pay_model": r.pay_model,
            "sales_count": r.sales_count,
            "total_revenue": float(r.total_revenue or 0),
            "total_profit": float(r.total_profit or 0),
            "avg_profit_per_sale": float(r.avg_profit_per_sale or 0)
        }
        for r in results
    ]
