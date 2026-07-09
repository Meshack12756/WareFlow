from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, DECIMAL, Date, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.connection import Base

class Employee(Base):
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="worker")  # "admin" or "worker"
    
    # Pay model configuration
    pay_model = Column(String(10), nullable=False)  # "A", "B", or "C"
    hourly_rate = Column(DECIMAL(10, 2), default=0.00)
    commission_rate = Column(DECIMAL(5, 2), default=0.00)  # Percentage
    bonus_rate = Column(DECIMAL(5, 2), default=0.00)  # Percentage
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    sales = relationship("Sale", back_populates="employee")
    timecards = relationship("Timecard", back_populates="employee")

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(String(500))
    cost_price = Column(DECIMAL(10, 2), nullable=False)
    selling_price = Column(DECIMAL(10, 2), nullable=False)
    stock_quantity = Column(Integer, default=0, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    sale_items = relationship("SaleItem", back_populates="product")

class Sale(Base):
    __tablename__ = "sales"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    total_amount = Column(DECIMAL(10, 2), nullable=False)
    total_cost = Column(DECIMAL(10, 2), nullable=False)
    gross_profit = Column(DECIMAL(10, 2), nullable=False)
    net_profit = Column(DECIMAL(10, 2), nullable=False)
    
    # Relationships
    employee = relationship("Employee", back_populates="sales")
    items = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")
    refunds = relationship("Refund", back_populates="sale")

class SaleItem(Base):
    __tablename__ = "sales_items"
    
    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_cost_price = Column(DECIMAL(10, 2), nullable=False)
    unit_selling_price = Column(DECIMAL(10, 2), nullable=False)
    
    # Relationships
    sale = relationship("Sale", back_populates="items")
    product = relationship("Product", back_populates="sale_items")
    refunds = relationship("RefundItem", back_populates="sale_item")

class Refund(Base):
    __tablename__ = "refunds"
    
    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    refund_date = Column(DateTime(timezone=True), server_default=func.now())
    total_refund_amount = Column(DECIMAL(10, 2), nullable=False)
    reason = Column(String(255), nullable=True)
    restock_items = Column(Boolean, default=True)  # global default, can be overridden per item
    
    # Relationships
    sale = relationship("Sale", back_populates="refunds")
    employee = relationship("Employee")
    items = relationship("RefundItem", back_populates="refund", cascade="all, delete-orphan")

class RefundItem(Base):
    __tablename__ = "refund_items"
    
    id = Column(Integer, primary_key=True, index=True)
    refund_id = Column(Integer, ForeignKey("refunds.id"), nullable=False)
    sale_item_id = Column(Integer, ForeignKey("sales_items.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    refund_unit_price = Column(DECIMAL(10, 2), nullable=False)  # price at refund time
    restock = Column(Boolean, default=True)  # per-item override
    
    # Relationships
    refund = relationship("Refund", back_populates="items")
    sale_item = relationship("SaleItem")
    product = relationship("Product")

class Timecard(Base):
    __tablename__ = "timecards"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    date = Column(Date, nullable=False)
    hours_worked = Column(DECIMAL(5, 2), nullable=False, default=0.00)
    
    # Relationships
    employee = relationship("Employee", back_populates="timecards")

class PeriodSummary(Base):
    __tablename__ = "period_summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    period_type = Column(String(20), nullable=False)  # "daily", "weekly", "monthly"
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    gross_profit_total = Column(DECIMAL(10, 2), default=0.00)
    net_profit_total = Column(DECIMAL(10, 2), default=0.00)
    pay_calculated = Column(DECIMAL(10, 2), default=0.00)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())