import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in .env")

DATABASE_PATH = os.getenv("DATABASE_PATH", "megatools.db")
TEMP_DIR = os.getenv("TEMP_DIR", "temp")
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB
LOG_FILE = os.getenv("LOG_FILE", "bot.log")

SUPPORTED_LANGUAGES = ("uz", "ru", "en")
DEFAULT_LANGUAGE = "uz"
