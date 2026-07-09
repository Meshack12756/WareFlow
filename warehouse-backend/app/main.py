from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.scripts.backup import get_latest_backup_info
from starlette.middleware.base import BaseHTTPMiddleware
from app.database.connection import engine, Base, SessionLocal
from app.routers import auth, products, sales, employees, reports, refunds #compensation
import os
import shutil
import time, datetime


# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.API_VERSION,
    description="Enterprise Warehouse Sales and Employee Performance Tracking System",
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(products.router, prefix="/api/v1/products", tags=["Products"])
app.include_router(sales.router, prefix="/api/v1/sales", tags=["Sales"])
app.include_router(employees.router, prefix="/api/v1/employees", tags=["Employees"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])
app.include_router(refunds.router, prefix="/api/v1/refunds", tags=["Refunds"])
#app.include_router(compensation.router, prefix="/api/v1/compensation", tags=["Compensation"])

@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.API_VERSION,
        "docs": "/api/docs" if settings.DEBUG else "Not available in production"
    }

@app.get("/health")
async def health_check():
    status = {"status": "healthy", "components": {}}
    
    # 1. Database check
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        status["components"]["database"] = {"status": "up", "message": "Connected"}
    except Exception as e:
        status["status"] = "unhealthy"
        status["components"]["database"] = {"status": "down", "message": str(e)}
    
    # 2. Disk space check (optional, adjust threshold)
    try:
        total, used, free = shutil.disk_usage("/")  # On Windows, use "C:\\"
        # Convert to GB
        free_gb = free // (2**30)
        if free_gb < 1:  # less than 1 GB free
            status["components"]["disk"] = {"status": "warning", "message": f"Only {free_gb} GB free"}
        else:
            status["components"]["disk"] = {"status": "up", "message": f"{free_gb} GB free"}
    except Exception as e:
        status["components"]["disk"] = {"status": "unknown", "message": str(e)}

    try:
        backup_info = get_latest_backup_info()
        if backup_info:
            # Check if backup is recent (less than 24 hours)
            backup_time = datetime.fromisoformat(backup_info["modified"])
            hours_ago = (datetime.now() - backup_time).total_seconds() / 3600
            if hours_ago < 24:
                status["components"]["backup"] = {
                    "status": "up",
                    "message": f"Latest backup: {backup_info['size_mb']} MB, {hours_ago:.1f} hours ago"
                }
            else:
                status["components"]["backup"] = {
                    "status": "warning",
                    "message": f"Backup is {hours_ago:.1f} hours old"
                }
        else:
            status["components"]["backup"] = {"status": "down", "message": "No backups found"}
    except Exception as e:
        status["components"]["backup"] = {"status": "unknown", "message": str(e)}
    
    # 3. Redis check (if used later)
    # status["components"]["redis"] = ... 
    
    # Return 200 if healthy, 503 if not
    if status["status"] == "healthy":
        return status
    else:
        raise HTTPException(status_code=503, detail=status)
    
    
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
            start_time = time.time()
            response = await call_next(request)
            process_time = time.time() - start_time
            # Log to console or file
            print(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
            return response

app.add_middleware(LoggingMiddleware)