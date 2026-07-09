#!/usr/bin/env python3
"""
Automated PostgreSQL backup script with rotation and logging.
Usage:
    python -m app.scripts.backup
"""
import os
import sys
import subprocess
import datetime
import glob
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env (or specify path)
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)

# ==================== Configuration ====================
BACKUP_DIR = Path(os.getenv("BACKUP_DIR", "./backups")).resolve()
LOG_FILE = Path(os.getenv("BACKUP_LOG", "./logs/backup.log")).resolve()
RETENTION_DAYS = int(os.getenv("BACKUP_RETENTION_DAYS", 7))

# Database connection details from .env
DB_HOST = os.getenv("DATABASE_HOST", "localhost")
DB_PORT = os.getenv("DATABASE_PORT", "5432")
DB_NAME = os.getenv("DATABASE_NAME", "warehouse_db")
DB_USER = os.getenv("DATABASE_USER", "postgres")
DB_PASSWORD = os.getenv("DATABASE_PASSWORD", "")
PGDUMP_PATH = os.getenv("PGDUMP_PATH", "pg_dump")  # full path if not in PATH

# ==================== Setup Logging ====================
def setup_logging():
    """Configure logging to file and console."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

# ==================== Core Functions ====================

def ensure_backup_dir():
    """Create backup directory if it doesn't exist."""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"Backup directory: {BACKUP_DIR}")

def get_backup_filename():
    """Generate a unique backup filename with timestamp."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return BACKUP_DIR / f"backup_{timestamp}.sql.gz"

def run_pg_dump(outfile):
    """
    Run pg_dump and compress output to outfile.
    Returns True on success, False on failure.
    """
    # Build the pg_dump command
    cmd = [
        PGDUMP_PATH,
        "--host", DB_HOST,
        "--port", DB_PORT,
        "--username", DB_USER,
        "--no-password",
        "--format", "custom",          # compressed, allows restore with pg_restore
        "--file", str(outfile),
        DB_NAME
    ]
    
    # Set environment for password (if provided)
    env = os.environ.copy()
    if DB_PASSWORD:
        env["PGPASSWORD"] = DB_PASSWORD
    
    try:
        logger.info(f"Starting backup: {' '.join(cmd)}")
        result = subprocess.run(cmd, env=env, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            logger.error(f"pg_dump failed with code {result.returncode}")
            logger.error(f"stderr: {result.stderr}")
            return False
        logger.info(f"Backup successful: {outfile} ({outfile.stat().st_size / 1024 / 1024:.2f} MB)")
        return True
    except FileNotFoundError:
        logger.error(f"pg_dump not found at '{PGDUMP_PATH}'. Please install PostgreSQL or set PGDUMP_PATH.")
        return False
    except Exception as e:
        logger.exception(f"Unexpected error during backup: {e}")
        return False

def rotate_backups():
    """
    Delete backup files older than RETENTION_DAYS.
    """
    cutoff = datetime.datetime.now() - datetime.timedelta(days=RETENTION_DAYS)
    pattern = str(BACKUP_DIR / "backup_*.sql.gz")
    deleted_count = 0
    for filepath in glob.glob(pattern):
        mtime = datetime.datetime.fromtimestamp(os.path.getmtime(filepath))
        if mtime < cutoff:
            try:
                os.remove(filepath)
                logger.info(f"Deleted old backup: {filepath}")
                deleted_count += 1
            except Exception as e:
                logger.warning(f"Could not delete {filepath}: {e}")
    if deleted_count == 0:
        logger.info("No old backups to delete.")
    return deleted_count

def get_latest_backup_info():
    """
    Return path and size of the most recent backup file, or None.
    """
    pattern = str(BACKUP_DIR / "backup_*.sql.gz")
    files = glob.glob(pattern)
    if not files:
        return None
    latest = max(files, key=os.path.getmtime)
    size_mb = os.path.getsize(latest) / (1024 * 1024)
    return {
        "path": latest,
        "size_mb": round(size_mb, 2),
        "modified": datetime.datetime.fromtimestamp(os.path.getmtime(latest)).isoformat()
    }

# ==================== Main Entry Point ====================

def main():
    """Run the backup process."""
    logger.info("========== Starting backup process ==========")
    ensure_backup_dir()
    
    outfile = get_backup_filename()
    success = run_pg_dump(outfile)
    
    if success:
        rotate_backups()
        logger.info("Backup process completed successfully.")
        sys.exit(0)
    else:
        logger.error("Backup process failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()