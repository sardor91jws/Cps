from pathlib import Path
import qrcode
from pyzbar.pyzbar import decode
from PIL import Image
from utils.temp_files import create_temp_path, cleanup_file
from utils.logger import setup_logger

logger = setup_logger(__name__)

async def generate_qr(data: str) -> Path:
    output_path = create_temp_path(suffix=".png")
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(output_path)
        logger.info(f"QR generated for data length={len(data)}")
        return output_path
    except Exception as e:
        cleanup_file(output_path)
        logger.exception(f"QR generation failed: {e}")
        raise

async def read_qr(image_path: Path) -> str | None:
    try:
        with Image.open(image_path) as img:
            decoded = decode(img)
            if not decoded:
                return None
            return decoded[0].data.decode("utf-8", errors="ignore")
    except Exception as e:
        logger.exception(f"QR reading failed: {e}")
        raise
