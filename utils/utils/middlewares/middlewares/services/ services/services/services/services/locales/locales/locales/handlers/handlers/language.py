from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from utils.i18n import get_text
from handlers.start import language_keyboard

router = Router(name="language")

@router.message(Command("language"))
async def cmd_language(message: Message, lang: str):
    await message.answer(
        get_text("choose_language", lang),
        reply_markup=language_keyboard(),
    )
