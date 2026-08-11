from pathlib import Path
from PIL import Image
from utils.temp_files import create_temp_path, cleanup_file
from utils.logger import setup_logger

logger = setup_logger(__name__)

async def compress_and_resize(
    input_path: Path,
    max_width: int = 1280,
    max_height: int = 1280,
    quality: int = 75,
) -> Path:
    """
    Compress and resize image. Returns path to result JPEG.
    """
    output_path = create_temp_path(suffix=".jpg")
    try:
        with Image.open(input_path) as img:
            img = img.convert("RGB")
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            img.save(output_path, "JPEG", quality=quality, optimize=True)
        logger.info(f"Image processed: {input_path} -> {output_path}")
        return output_path
    except Exception as e:
        cleanup_file(output_path)
        logger.exception(f"Image processing failed: {e}")
        raise
