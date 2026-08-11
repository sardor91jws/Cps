import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config import BOT_TOKEN
from utils.logger import setup_logger
from utils.database import init_db
from utils.i18n import load_translations
from utils.temp_files import ensure_temp_dir
from middlewares.i18n_middleware import I18nMiddleware
from handlers import setup_routers

logger = setup_logger("megatools")

async def main() -> None:
    ensure_temp_dir()
    load_translations()
    await init_db()

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    dp.update.middleware(I18nMiddleware())
    dp.include_router(setup_routers())

    logger.info("Bot starting...")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        logger.info("Bot stopped")

if __name__ == "__main__":
    asyncio.run(main())
