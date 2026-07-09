from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from app.core.auth import get_current_user, require_role
from app.core.security import get_password_hash
from app.database.connection import get_db
from app.database.models import Employee, Timecard, Sale
from app.schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeResponse
from app.schemas.timecard import TimecardCreate, TimecardResponse

router = APIRouter()

# Employee CRUD
@router.post("", response_model=None, status_code=status.HTTP_201_CREATED)
async def create_employee(
    employee: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_role("admin"))
):
    """Create a new employee (Admin only)"""
    existing = db.query(Employee).filter(Employee.email == employee.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    new_employee = Employee(
        name=employee.name,
        email=employee.email,
        hashed_password=get_password_hash(employee.password),
        role=employee.role,
        pay_model=employee.pay_model,
        hourly_rate=employee.hourly_rate,
        commission_rate=employee.commission_rate,
        bonus_rate=employee.bonus_rate
    )
    
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    return new_employee

@router.get("", response_model=None)
async def get_employees(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Get all employees"""
    if current_user.role == "worker":
        return [current_user]
    
    employees = db.query(Employee).offset(skip).limit(limit).all()
    return employees

@router.get("/{employee_id}", response_model=None)
async def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Get a specific employee by ID"""
    if current_user.role == "worker" and current_user.id != employee_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Workers can only view their own profile"
        )
    
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {employee_id} not found"
        )
    return employee

@router.put("/{employee_id}", response_model=None)
async def update_employee(
    employee_id: int,
    employee_update: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_role("admin"))
):
    """Update an employee (Admin only)"""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {employee_id} not found"
        )
    
    update_data = employee_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(employee, key, value)
    
    db.commit()
    db.refresh(employee)
    return employee

@router.delete("/{employee_id}")
async def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_role("admin"))
):
    """Delete an employee (Admin only)"""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {employee_id} not found"
        )
    
    if employee.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    db.delete(employee)
    db.commit()
    return {"message": f"Employee {employee.name} deleted successfully"}

# Timecard operations
@router.post("/timecards/", response_model=None)
async def create_timecard(
    timecard_data: TimecardCreate,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_role("admin"))
):
    """Create a timecard entry (Admin only)"""
    employee = db.query(Employee).filter(Employee.id == timecard_data.employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {timecard_data.employee_id} not found"
        )
    
    existing = db.query(Timecard).filter(
        Timecard.employee_id == timecard_data.employee_id,
        Timecard.date == timecard_data.date
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Timecard already exists for this employee on this date"
        )
    
    timecard = Timecard(
        employee_id=timecard_data.employee_id,
        date=timecard_data.date,
        hours_worked=timecard_data.hours_worked
    )
    
    db.add(timecard)
    db.commit()
    db.refresh(timecard)
    return timecard

@router.get("/timecards/", response_model=None)
async def get_timecards(
    employee_id: int = None,
    start_date: datetime = None,
    end_date: datetime = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Get timecards with optional filtering"""
    query = db.query(Timecard)
    
    if current_user.role == "worker":
        query = query.filter(Timecard.employee_id == current_user.id)
    elif employee_id:
        query = query.filter(Timecard.employee_id == employee_id)
    
    if start_date:
        query = query.filter(Timecard.date >= start_date.date())
    if end_date:
        query = query.filter(Timecard.date <= end_date.date())
    
    query = query.order_by(Timecard.date.desc())
    timecards = query.offset(skip).limit(limit).all()
    return timecards

@router.get("/timecards/employee/{employee_id}", response_model=None)
async def get_employee_timecards(
    employee_id: int,
    start_date: datetime = None,
    end_date: datetime = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Get timecards for a specific employee"""
    if current_user.role == "worker" and current_user.id != employee_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Workers can only view their own timecards"
        )
    
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {employee_id} not found"
        )
    
    query = db.query(Timecard).filter(Timecard.employee_id == employee_id)
    
    if start_date:
        query = query.filter(Timecard.date >= start_date.date())
    if end_date:
        query = query.filter(Timecard.date <= end_date.date())
    
    query = query.order_by(Timecard.date.desc())
    timecards = query.offset(skip).limit(limit).all()
    return timecards

# Employee performance
@router.get("/{employee_id}/performance")
async def get_employee_performance(
    employee_id: int,
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Get performance metrics for a specific employee"""
    if current_user.role == "worker" and current_user.id != employee_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Workers can only view their own performance"
        )
    
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
    total_revenue = sum(s.total_amount for s in sales) if sales else 0
    total_profit = sum(s.gross_profit for s in sales) if sales else 0
    
    # Calculate daily trend (last 7 days)
    trend_data = []
    for i in range(7, 0, -1):
        day_start = datetime.now() - timedelta(days=i)
        day_end = datetime.now() - timedelta(days=i-1)
        
        day_sales = [s for s in sales if day_start <= s.timestamp < day_end]
        trend_data.append({
            "date": day_start.date().isoformat(),
            "sales_count": len(day_sales),
            "revenue": sum(s.total_amount for s in day_sales) if day_sales else 0
        })
    
    return {
        "employee_id": employee.id,
        "employee_name": employee.name,
        "pay_model": employee.pay_model,
        "period_days": days,
        "total_sales": total_sales,
        "total_revenue": float(total_revenue),
        "total_profit": float(total_profit),
        "average_sale_value": float(total_revenue / total_sales) if total_sales > 0 else 0,
        "trend": trend_data
    }

@router.get("/summary/payroll")
async def get_payroll_summary(
    start_date: datetime,
    end_date: datetime,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_role("admin"))
):
    """Get payroll summary for all employees for a period (Admin only)"""
    employees = db.query(Employee).all()
    
    payroll_data = []
    total_payroll = 0
    
    # Group by pay model
    model_counts = {}
    model_totals = {}
    for item in payroll_data:
        model = item["pay_model"]
        model_counts[model] = model_counts.get(model, 0) + 1
        model_totals[model] = model_totals.get(model, 0) + item["total_pay"]
    
    return {
        "period_start": start_date.isoformat(),
        "period_end": end_date.isoformat(),
        "total_employees": len(payroll_data),
        "total_payroll": float(total_payroll),
        "breakdown_by_model": {
            "model_counts": model_counts,
            "model_totals": {k: float(v) for k, v in model_totals.items()}
        },
        "employees": payroll_data
    }
