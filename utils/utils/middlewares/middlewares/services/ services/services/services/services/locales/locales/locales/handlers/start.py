from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from utils.database import get_user_language, set_user_language
from utils.i18n import get_text
from config import SUPPORTED_LANGUAGES

router = Router(name="start")

def language_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="O‘zbek 🇺🇿", callback_data="lang:uz"),
                InlineKeyboardButton(text="Русский 🇷🇺", callback_data="lang:ru"),
                InlineKeyboardButton(text="English 🇬🇧", callback_data="lang:en"),
            ]
        ]
    )

def main_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=get_text("btn_media", lang), callback_data="menu:media"
                ),
                InlineKeyboardButton(
                    text=get_text("btn_tools", lang), callback_data="menu:tools"
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_text("btn_files", lang), callback_data="menu:files"
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_text("btn_language", lang), callback_data="menu:language"
                ),
            ],
        ]
    )

@router.message(CommandStart())
async def cmd_start(message: Message, lang: str):
    user_id = message.from_user.id
    stored_lang = await get_user_language(user_id)

    if stored_lang is None:
        await message.answer(
            get_text("choose_language", "en"),
            reply_markup=language_keyboard(),
        )
        return

    await message.answer(
        get_text("welcome", stored_lang),
        reply_markup=main_menu_keyboard(stored_lang),
    )

@router.callback_query(F.data.startswith("lang:"))
async def process_language(callback: CallbackQuery):
    lang_code = callback.data.split(":")[1]
    if lang_code not in SUPPORTED_LANGUAGES:
        await callback.answer()
        return

    await set_user_language(callback.from_user.id, lang_code)
    await callback.message.edit_text(
        get_text("language_changed", lang_code),
        reply_markup=main_menu_keyboard(lang_code),
    )
    await callback.answer()

@router.callback_query(F.data == "menu:language")
async def show_language_menu(callback: CallbackQuery, lang: str):
    await callback.message.edit_text(
        get_text("choose_language", lang),
        reply_markup=language_keyboard(),
    )
    await callback.answer()

@router.callback_query(F.data == "menu:main")
async def back_to_main(callback: CallbackQuery, lang: str):
    await callback.message.edit_text(
        get_text("welcome", lang),
        reply_markup=main_menu_keyboard(lang),
    )
    await callback.answer()
