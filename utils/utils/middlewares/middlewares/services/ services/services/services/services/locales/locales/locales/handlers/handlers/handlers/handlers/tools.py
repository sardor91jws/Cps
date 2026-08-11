from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from pathlib import Path
from utils.i18n import get_text
from utils.temp_files import create_temp_path, cleanup_file, check_file_size
from services.qr_service import generate_qr, read_qr
from services.password_service import generate_password
from utils.logger import setup_logger

logger = setup_logger(__name__)
router = Router(name="tools")

class ToolsStates(StatesGroup):
    waiting_qr_text = State()
    waiting_qr_image = State()

def back_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=get_text("btn_back", lang), callback_data="menu:main")]
        ]
    )

def tools_submenu(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📱 QR Create", callback_data="tools:qr_create"),
                InlineKeyboardButton(text="📷 QR Read", callback_data="tools:qr_read"),
            ],
            [
                InlineKeyboardButton(text="🔐 Password", callback_data="tools:password"),
            ],
            [
                InlineKeyboardButton(text=get_text("btn_back", lang), callback_data="menu:main"),
            ],
        ]
    )

@router.callback_query(F.data == "menu:tools")
async def tools_menu(callback: CallbackQuery, state: FSMContext, lang: str):
    await state.clear()
    await callback.message.edit_text(
        get_text("tools_help", lang),
        reply_markup=tools_submenu(lang),
        parse_mode="HTML",
    )
    await callback.answer()

@router.callback_query(F.data == "tools:qr_create")
async def qr_create_start(callback: CallbackQuery, state: FSMContext, lang: str):
    await state.set_state(ToolsStates.waiting_qr_text)
    await callback.message.edit_text(
        get_text("send_text_for_qr", lang),
        reply_markup=back_keyboard(lang),
    )
    await callback.answer()

@router.message(ToolsStates.waiting_qr_text, F.text)
async def process_qr_text(message: Message, state: FSMContext, lang: str):
    text = message.text.strip()
    if not text:
        await message.answer(get_text("error_processing", lang))
        return

    output_path = None
    try:
        output_path = await generate_qr(text)
        await message.answer_photo(
            photo=output_path.open("rb"),
            caption=get_text("success_qr_created", lang),
        )
    except Exception as e:
        logger.exception(e)
        await message.answer(get_text("error_processing", lang))
    finally:
        if output_path:
            cleanup_file(output_path)
        await state.clear()

@router.callback_query(F.data == "tools:qr_read")
async def qr_read_start(callback: CallbackQuery, state: FSMContext, lang: str):
    await state.set_state(ToolsStates.waiting_qr_image)
    await callback.message.edit_text(
        get_text("send_qr_image", lang),
        reply_markup=back_keyboard(lang),
    )
    await callback.answer()

@router.message(ToolsStates.waiting_qr_image, F.photo)
async def process_qr_image(message: Message, state: FSMContext, bot: Bot, lang: str):
    photo = message.photo[-1]
    if not check_file_size(photo.file_size or 0):
        await message.answer(get_text("error_file_too_large", lang))
        return

    input_path = create_temp_path(suffix=".jpg")
    try:
        await bot.download(photo, destination=input_path)
        result = await read_qr(input_path)
        if result is None:
            await message.answer(get_text("error_qr_empty", lang))
        else:
            await message.answer(
                get_text("success_qr_read", lang, text=result),
                parse_mode="HTML",
            )
    except Exception as e:
        logger.exception(e)
        await message.answer(get_text("error_processing", lang))
    finally:
        cleanup_file(input_path)
        await state.clear()

@router.callback_query(F.data == "tools:password")
async def password_help(callback: CallbackQuery, lang: str):
    await callback.message.edit_text(
        get_text("password_usage", lang),
        reply_markup=back_keyboard(lang),
    )
    await callback.answer()

@router.message(Command("password"))
async def cmd_password(message: Message, lang: str):
    args = message.text.split()[1:]
    try:
        length = 16
        use_upper = use_lower = use_digits = use_symbols = True

        if len(args) >= 1:
            length = int(args[0])
        if len(args) >= 2:
            use_upper = args[1] == "1"
        if len(args) >= 3:
            use_lower = args[2] == "1"
        if len(args) >= 4:
            use_digits = args[3] == "1"
        if len(args) >= 5:
            use_symbols = args[4] == "1"

        password = generate_password(
            length=length,
            use_upper=use_upper,
            use_lower=use_lower,
            use_digits=use_digits,
            use_symbols=use_symbols,
        )
        await message.answer(
            get_text("password_result", lang, password=password),
            parse_mode="HTML",
        )
    except Exception:
        await message.answer(get_text("error_invalid_password_args", lang))
