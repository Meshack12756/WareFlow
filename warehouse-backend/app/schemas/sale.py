# app/schemas/sale.py
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from decimal import Decimal

class SaleItemCreate(BaseModel):
    """Schema for creating a sale item"""
    product_id: int
    quantity: int

    class Config:
        from_attributes = True

class SaleCreate(BaseModel):
    """Schema for creating a sale"""
    employee_id: int
    items: List[SaleItemCreate]

    class Config:
        from_attributes = True

class SaleItemResponse(BaseModel):
    """Schema for sale item response"""
    id: int
    product_id: int
    product_name: str
    product_sku: str
    quantity: int
    unit_cost_price: Decimal
    unit_selling_price: Decimal
    subtotal_cost: Decimal
    subtotal_amount: Decimal

    class Config:
        from_attributes = True

class SaleResponse(BaseModel):
    """Schema for sale response"""
    id: int
    employee_id: int
    employee_name: str
    timestamp: datetime
    total_amount: Decimal
    total_cost: Decimal
    gross_profit: Decimal
    net_profit: Decimal
    items: List[SaleItemResponse]

    class Config:
        from_attributes = True

class SalesFilter(BaseModel):
    """Schema for filtering sales"""
    employee_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None

    class Config:
        from_attributes = True