from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from decimal import Decimal
from sqlalchemy import func
from app.core.auth import get_current_user, require_role
from app.database.connection import get_db
from app.database.models import Employee, Sale, SaleItem, Product, Refund, RefundItem
from app.schemas.refund import RefundCreate, RefundResponse, RefundFilter

router = APIRouter()

@router.post("", response_model=RefundResponse, status_code=status.HTTP_201_CREATED)
async def create_refund(
    refund_data: RefundCreate,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_role("admin"))
):
    """
    Process a refund for a sale.
    
    - Validates sale exists and is not fully refunded.
    - Validates item quantities.
    - Optionally restocks items.
    - Creates refund records.
    - Does NOT modify original sale record.
    """
    # 1. Validate sale
    sale = db.query(Sale).filter(Sale.id == refund_data.sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    
    # 2. Check if sale is already fully refunded
    total_refunded = db.query(Refund).filter(Refund.sale_id == sale.id).with_entities(
        func.sum(Refund.total_refund_amount)
    ).scalar() or Decimal('0.00')
    
    if total_refunded >= sale.total_amount:
        raise HTTPException(status_code=400, detail="Sale is already fully refunded")
    
    # 3. Process each item
    refund_items_data = []
    total_refund_amount = Decimal('0.00')
    
    for item_data in refund_data.items:
        # Get original sale item
        sale_item = db.query(SaleItem).filter(SaleItem.id == item_data.sale_item_id).first()
        if not sale_item:
            raise HTTPException(status_code=404, detail=f"Sale item {item_data.sale_item_id} not found")
        
        # Validate quantity
        already_refunded_qty = db.query(func.sum(RefundItem.quantity)).filter(
            RefundItem.sale_item_id == sale_item.id
        ).scalar() or 0
        
        available_qty = sale_item.quantity - already_refunded_qty
        if item_data.quantity > available_qty:
            raise HTTPException(
                status_code=400,
                detail=f"Quantity {item_data.quantity} exceeds available quantity {available_qty} for item {sale_item.id}"
            )
        
        # Determine refund unit price
        unit_price = item_data.refund_unit_price or sale_item.unit_selling_price
        
        # Calculate subtotal
        subtotal = unit_price * item_data.quantity
        total_refund_amount += subtotal
        
        # Restock? (item-specific override, else use global)
        restock = item_data.restock if item_data.restock is not None else refund_data.restock_items
        
        # If restock, add back to product stock
        if restock:
            product = db.query(Product).filter(Product.id == sale_item.product_id).first()
            if product:
                product.stock_quantity += item_data.quantity
        
        refund_items_data.append({
            "sale_item_id": sale_item.id,
            "product_id": sale_item.product_id,
            "quantity": item_data.quantity,
            "refund_unit_price": unit_price,
            "restock": restock,
        })
    
    # 4. Create refund record
    new_refund = Refund(
        sale_id=sale.id,
        employee_id=refund_data.employee_id,
        total_refund_amount=total_refund_amount,
        reason=refund_data.reason,
        restock_items=refund_data.restock_items
    )
    db.add(new_refund)
    db.flush()  # to get refund ID
    
    # 5. Create refund items
    for item in refund_items_data:
        refund_item = RefundItem(
            refund_id=new_refund.id,
            sale_item_id=item["sale_item_id"],
            product_id=item["product_id"],
            quantity=item["quantity"],
            refund_unit_price=item["refund_unit_price"],
            restock=item["restock"]
        )
        db.add(refund_item)
    
    db.commit()
    db.refresh(new_refund)
    
    # Load relationships for response
    complete_refund = db.query(Refund).options(
        joinedload(Refund.employee),
        joinedload(Refund.items).joinedload(RefundItem.product)
    ).filter(Refund.id == new_refund.id).first()
    
    return complete_refund

@router.get("", response_model=List[RefundResponse])
async def get_refunds(
    filters: RefundFilter = Depends(),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """List refunds with optional filters."""
    query = db.query(Refund).options(
        joinedload(Refund.employee),
        joinedload(Refund.items).joinedload(RefundItem.product)
    )
    
    if current_user.role == "worker":
        # Workers can only see refunds they processed
        query = query.filter(Refund.employee_id == current_user.id)
    else:
        if filters.sale_id:
            query = query.filter(Refund.sale_id == filters.sale_id)
        if filters.employee_id:
            query = query.filter(Refund.employee_id == filters.employee_id)
        if filters.start_date:
            query = query.filter(Refund.refund_date >= filters.start_date)
        if filters.end_date:
            query = query.filter(Refund.refund_date <= filters.end_date)
    
    query = query.order_by(Refund.refund_date.desc())
    refunds = query.offset(skip).limit(limit).all()
    return refunds

@router.get("/{refund_id}", response_model=RefundResponse)
async def get_refund(
    refund_id: int,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Get a specific refund by ID."""
    refund = db.query(Refund).options(
        joinedload(Refund.employee),
        joinedload(Refund.items).joinedload(RefundItem.product)
    ).filter(Refund.id == refund_id).first()
    
    if not refund:
        raise HTTPException(status_code=404, detail="Refund not found")
    
    if current_user.role == "worker" and current_user.id != refund.employee_id:
        raise HTTPException(status_code=403, detail="Workers can only view their own refunds")
    
    return refund

@router.get("/sale/{sale_id}", response_model=List[RefundResponse])
async def get_refunds_by_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Get all refunds for a specific sale."""
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    
    query = db.query(Refund).options(
        joinedload(Refund.employee),
        joinedload(Refund.items).joinedload(RefundItem.product)
    ).filter(Refund.sale_id == sale_id)
    
    # Permissions
    if current_user.role == "worker" and current_user.id != sale.employee_id:
        raise HTTPException(status_code=403, detail="Workers can only view their own sales")
    
    refunds = query.order_by(Refund.refund_date.desc()).all()
    return refunds