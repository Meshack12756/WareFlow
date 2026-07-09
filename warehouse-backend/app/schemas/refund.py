from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from decimal import Decimal

class RefundItemCreate(BaseModel):
    sale_item_id: int
    quantity: int
    refund_unit_price: Optional[Decimal] = None  # if not provided, use original sale price
    restock: bool = True

class RefundCreate(BaseModel):
    sale_id: int
    employee_id: int
    items: List[RefundItemCreate]
    reason: Optional[str] = None
    restock_items: bool = True  # global default

class RefundItemResponse(BaseModel):
    id: int
    sale_item_id: int
    product_id: int
    product_name: str
    quantity: int
    refund_unit_price: Decimal
    restock: bool
    subtotal: Decimal

    class Config:
        from_attributes = True

class RefundResponse(BaseModel):
    id: int
    sale_id: int
    employee_id: int
    employee_name: str
    refund_date: datetime
    total_refund_amount: Decimal
    reason: Optional[str]
    restock_items: bool
    items: List[RefundItemResponse]

    class Config:
        from_attributes = True

class RefundFilter(BaseModel):
    sale_id: Optional[int] = None
    employee_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None