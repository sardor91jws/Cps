from aiogram import Router
from .start import router as start_router
from .language import router as language_router
from .media import router as media_router
from .tools import router as tools_router
from .files import router as files_router

def setup_routers() -> Router:
    root = Router()
    root.include_router(start_router)
    root.include_router(language_router)
    root.include_router(media_router)
    root.include_router(tools_router)
    root.include_router(files_router)
    return root
