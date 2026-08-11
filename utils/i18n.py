import json
from pathlib import Path
from config import SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE
from utils.logger import setup_logger

logger = setup_logger(__name__)

LOCALES_DIR = Path(__file__).parent.parent / "locales"
_translations: dict[str, dict] = {}

def load_translations() -> None:
    global _translations
    for lang in SUPPORTED_LANGUAGES:
        path = LOCALES_DIR / f"{lang}.json"
        try:
            with open(path, "r", encoding="utf-8") as f:
                _translations[lang] = json.load(f)
            logger.info(f"Loaded locale: {lang}")
        except Exception as e:
            logger.error(f"Failed to load locale {lang}: {e}")
            _translations[lang] = {}

def get_text(key: str, lang: str = DEFAULT_LANGUAGE, **kwargs) -> str:
    if lang not in _translations:
        lang = DEFAULT_LANGUAGE
    text = _translations.get(lang, {}).get(key) or _translations.get(DEFAULT_LANGUAGE, {}).get(key) or key
    try:
        return text.format(**kwargs) if kwargs else text
    except Exception:
        return text
