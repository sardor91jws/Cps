import os
import shutil
import uuid
from pathlib import Path
from config import TEMP_DIR, MAX_FILE_SIZE
from utils.logger import setup_logger

logger = setup_logger(__name__)

def ensure_temp_dir() -> Path:
    path = Path(TEMP_DIR)
    path.mkdir(parents=True, exist_ok=True)
    return path

def create_temp_path(suffix: str = "") -> Path:
    ensure_temp_dir()
    name = f"{uuid.uuid4().hex}{suffix}"
    return Path(TEMP_DIR) / name

def cleanup_file(path: str | Path) -> None:
    try:
        p = Path(path)
        if p.exists() and p.is_file():
            p.unlink()
            logger.debug(f"Deleted temp file: {p}")
    except Exception as e:
        logger.warning(f"Failed to delete {path}: {e}")

def cleanup_dir(path: str | Path) -> None:
    try:
        p = Path(path)
        if p.exists() and p.is_dir():
            shutil.rmtree(p, ignore_errors=True)
            logger.debug(f"Deleted temp dir: {p}")
    except Exception as e:
        logger.warning(f"Failed to delete dir {path}: {e}")

def check_file_size(file_size: int) -> bool:
    return file_size <= MAX_FILE_SIZE
