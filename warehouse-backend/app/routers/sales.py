from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from datetime import datetime, timedelta
from decimal import Decimal

from app.core.auth import get_current_user, require_role
from app.database.connection import get_db
from app.database.models import Employee, Product, Sale, SaleItem, Refund
from app.schemas.sale import SaleCreate, SaleResponse, SalesFilter
from app.utils.cache import cache

router = APIRouter()

@router.post("/", response_model=None, status_code=status.HTTP_201_CREATED)
async def create_sale(
    sale_data: SaleCreate,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Create a new sale transaction with atomic inventory updates."""
    # Validate employee exists
    employee = db.query(Employee).filter(Employee.id == sale_data.employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {sale_data.employee_id} not found"
        )
    
    sale_items = []
    total_cost = Decimal('0.00')
    total_amount = Decimal('0.00')
    
    try:
        for item_data in sale_data.items:
            product = db.query(Product).filter(
                Product.id == item_data.product_id
            ).with_for_update().first()
            
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product with ID {item_data.product_id} not found"
                )
            
            if product.stock_quantity < item_data.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient stock for {product.name}. "
                           f"Available: {product.stock_quantity}, Requested: {item_data.quantity}"
                )
            
            item_cost = product.cost_price * item_data.quantity
            item_amount = product.selling_price * item_data.quantity
            
            total_cost += item_cost
            total_amount += item_amount
            
            product.stock_quantity -= item_data.quantity
            
            sale_items.append({
                "product_id": product.id,
                "quantity": item_data.quantity,
                "unit_cost_price": product.cost_price,
                "unit_selling_price": product.selling_price
            })
        
        gross_profit = total_amount - total_cost
        net_profit = gross_profit
        
        new_sale = Sale(
            employee_id=sale_data.employee_id,
            total_amount=total_amount,
            total_cost=total_cost,
            gross_profit=gross_profit,
            net_profit=net_profit
        )
        
        db.add(new_sale)
        db.flush()
        
        for item in sale_items:
            sale_item = SaleItem(
                sale_id=new_sale.id,
                product_id=item["product_id"],
                quantity=item["quantity"],
                unit_cost_price=item["unit_cost_price"],
                unit_selling_price=item["unit_selling_price"]
            )
            db.add(sale_item)
        
        db.commit()
        db.refresh(new_sale)
        
        complete_sale = db.query(Sale).filter(Sale.id == new_sale.id).first()
        return complete_sale
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Transaction failed: {str(e)}"
        )

@router.get("/", response_model=None)
async def get_all_sales(
    filters: SalesFilter = Depends(),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Get all sales with optional filtering."""
    query = db.query(Sale)
    
    if current_user.role == "worker":
        query = query.filter(Sale.employee_id == current_user.id)
    elif filters.employee_id:
        query = query.filter(Sale.employee_id == filters.employee_id)
    
    if filters.start_date:
        query = query.filter(Sale.timestamp >= filters.start_date)
    if filters.end_date:
        query = query.filter(Sale.timestamp <= filters.end_date)
    if filters.min_amount:
        query = query.filter(Sale.total_amount >= filters.min_amount)
    if filters.max_amount:
        query = query.filter(Sale.total_amount <= filters.max_amount)
    
    query = query.order_by(Sale.timestamp.desc())
    sales = query.offset(skip).limit(limit).all()
    return sales

@router.get("/employee/{employee_id}", response_model=None)
async def get_employee_sales(
    employee_id: int,
    start_date: datetime = None,
    end_date: datetime = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Get sales for a specific employee."""
    if current_user.role == "worker" and current_user.id != employee_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Workers can only view their own sales"
        )
    
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {employee_id} not found"
        )
    
    query = db.query(Sale).filter(Sale.employee_id == employee_id)
    
    if start_date:
        query = query.filter(Sale.timestamp >= start_date)
    if end_date:
        query = query.filter(Sale.timestamp <= end_date)
    
    query = query.order_by(Sale.timestamp.desc())
    sales = query.offset(skip).limit(limit).all()
    return sales

@router.get("/{sale_id}", response_model=None)
async def get_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Get a specific sale by ID."""
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    
    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sale with ID {sale_id} not found"
        )
    
    if current_user.role == "worker" and current_user.id != sale.employee_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Workers can only view their own sales"
        )
    
    return sale

@router.get("/summary/today")
#@cache(ttl=60)
async def get_today_summary(
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Get today's sales summary (net of refunds)."""
    today = datetime.now().date()
    start_of_day = datetime.combine(today, datetime.min.time())
    end_of_day = datetime.combine(today, datetime.max.time())
    
    sale_query = db.query(Sale).filter(
        Sale.timestamp >= start_of_day,
        Sale.timestamp <= end_of_day
    )
    if current_user.role == "worker":
        sale_query = sale_query.filter(Sale.employee_id == current_user.id)
    
    sales = sale_query.all()
    total_sales_count = len(sales)
    gross_revenue = sum(s.total_amount for s in sales)
    gross_profit = sum(s.gross_profit for s in sales)
    
    refund_query = db.query(Refund).join(Sale, Refund.sale_id == Sale.id).filter(
        Refund.refund_date >= start_of_day,
        Refund.refund_date <= end_of_day
    )
    if current_user.role == "worker":
        refund_query = refund_query.filter(Sale.employee_id == current_user.id)
    
    refunds = refund_query.all()
    total_refund_count = len(refunds)
    total_refund_amount = sum(r.total_refund_amount for r in refunds)
    
    net_revenue = gross_revenue - total_refund_amount
    net_profit = gross_profit - total_refund_amount  
    
    return {
        "date": today.isoformat(),
        "total_sales": total_sales_count,
        "total_refunds": total_refund_count,
        "total_refund_amount": float(total_refund_amount),
        "gross_revenue": float(gross_revenue),
        "net_revenue": float(net_revenue),
        "gross_profit": float(gross_profit),
        "net_profit": float(net_profit),
        "average_sale_value": float(net_revenue / total_sales_count) if total_sales_count > 0 else 0
    }

@router.get("/summary/employee/{employee_id}")
async def get_employee_summary(
    employee_id: int,
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_role("admin"))
):
    """Get summary for a specific employee over the last N days. Admin only."""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {employee_id} not found"
        )
    
    start_date = datetime.now() - timedelta(days=days)
    
    sales = db.query(Sale).filter(
        Sale.employee_id == employee_id,
        Sale.timestamp >= start_date
    ).all()
    
    total_sales = len(sales)
    total_revenue = sum(s.total_amount for s in sales)
    total_profit = sum(s.gross_profit for s in sales)
    
    return {
        "employee_id": employee_id,
        "employee_name": employee.name,
        "period_days": days,
        "total_sales": total_sales,
        "total_revenue": float(total_revenue),
        "total_profit": float(total_profit),
        "average_sale_value": float(total_revenue / total_sales) if total_sales > 0 else 0
    }
