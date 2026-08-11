import zipfile
from pathlib import Path
from utils.temp_files import create_temp_path, cleanup_file, cleanup_dir
from utils.logger import setup_logger

logger = setup_logger(__name__)

async def create_zip(files: list[Path], zip_name: str = "archive.zip") -> Path:
    output_path = create_temp_path(suffix=".zip")
    try:
        with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for f in files:
                if f.exists() and f.is_file():
                    zf.write(f, arcname=f.name)
        logger.info(f"ZIP created: {output_path}")
        return output_path
    except Exception as e:
        cleanup_file(output_path)
        logger.exception(f"ZIP create failed: {e}")
        raise

async def extract_zip(zip_path: Path) -> Path:
    extract_dir = create_temp_path(suffix="_extracted")
    extract_dir.mkdir(parents=True, exist_ok=True)
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            # Security: prevent path traversal
            for member in zf.namelist():
                member_path = Path(member)
                if member_path.is_absolute() or ".." in member_path.parts:
                    raise ValueError(f"Unsafe path in archive: {member}")
            zf.extractall(extract_dir)
        logger.info(f"ZIP extracted to: {extract_dir}")
        return extract_dir
    except Exception as e:
        cleanup_dir(extract_dir)
        logger.exception(f"ZIP extract failed: {e}")
        raise
