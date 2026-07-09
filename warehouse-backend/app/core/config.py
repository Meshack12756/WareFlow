from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    DATABASE_URL_ASYNC: Optional[str] = None
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # App
    APP_NAME: str = "Warehouse Management System"
    DEBUG: bool = False
    API_VERSION: str = "v1"
    
    # Backup settings (new)
    BACKUP_DIR: str = "./backups"
    BACKUP_LOG: str = "./logs/backup.log"
    BACKUP_RETENTION_DAYS: int = 7
    
    # Database connection details for backup (new)
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: str = "5432"
    DATABASE_NAME: str = "warehouse_db"
    DATABASE_USER: str = "postgres"
    DATABASE_PASSWORD: str = ""
    PGDUMP_PATH: str = "pg_dump"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        # Allow extra fields? Yes, but we're defining all we need.
        # extra = "ignore"  # If you want to ignore extras, but better to define them.

settings = Settings()