from pydantic import BaseModel
from datetime import date
from typing import Optional
from decimal import Decimal

class TimecardBase(BaseModel):
    employee_id: int
    date: date
    hours_worked: Decimal

class TimecardCreate(TimecardBase):
    pass

class TimecardResponse(TimecardBase):
    id: int
    
    class Config:
        from_attributes = True