from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from pathlib import Path
from utils.i18n import get_text
from utils.temp_files import create_temp_path, cleanup_file, check_file_size
from services.image_service import compress_and_resize
from utils.logger import setup_logger
from handlers.start import main_menu_keyboard

logger = setup_logger(__name__)
router = Router(name="media")

class MediaStates(StatesGroup):
    waiting_photo = State()

def back_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=get_text("btn_back", lang), callback_data="menu:main")]
        ]
    )

@router.callback_query(F.data == "menu:media")
async def media_menu(callback: CallbackQuery, state: FSMContext, lang: str):
    await state.set_state(MediaStates.waiting_photo)
    await callback.message.edit_text(
        get_text("media_help", lang),
        reply_markup=back_keyboard(lang),
        parse_mode="HTML",
    )
    await callback.answer()

@router.message(MediaStates.waiting_photo, F.photo)
async def process_photo(message: Message, state: FSMContext, bot: Bot, lang: str):
    photo = message.photo[-1]
    if not check_file_size(photo.file_size or 0):
        await message.answer(get_text("error_file_too_large", lang))
        return

    input_path = create_temp_path(suffix=".jpg")
    output_path = None
    try:
        await bot.download(photo, destination=input_path)
        output_path = await compress_and_resize(input_path)
        await message.answer_photo(
            photo=output_path.open("rb"),
            caption=get_text("success_image", lang),
        )
    except Exception as e:
        logger.exception(e)
        await message.answer(get_text("error_processing", lang))
    finally:
        cleanup_file(input_path)
        if output_path:
            cleanup_file(output_path)
        await state.clear()

@router.message(MediaStates.waiting_photo)
async def media_wrong_input(message: Message, lang: str):
    await message.answer(get_text("send_photo", lang))
