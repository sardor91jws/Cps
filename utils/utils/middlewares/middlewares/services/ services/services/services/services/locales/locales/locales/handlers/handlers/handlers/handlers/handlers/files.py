from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from pathlib import Path
from utils.i18n import get_text
from utils.temp_files import create_temp_path, cleanup_file, cleanup_dir, check_file_size
from services.zip_service import create_zip, extract_zip
from utils.logger import setup_logger

logger = setup_logger(__name__)
router = Router(name="files")

class FilesStates(StatesGroup):
    collecting_files = State()

# Simple in-memory storage for user files (MVP)
user_files: dict[int, list[Path]] = {}

def back_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=get_text("btn_back", lang), callback_data="menu:main")]
        ]
    )

@router.callback_query(F.data == "menu:files")
async def files_menu(callback: CallbackQuery, state: FSMContext, lang: str):
    await state.set_state(FilesStates.collecting_files)
    user_files[callback.from_user.id] = []
    await callback.message.edit_text(
        get_text("files_help", lang),
        reply_markup=back_keyboard(lang),
        parse_mode="HTML",
    )
    await callback.answer()

@router.message(FilesStates.collecting_files, F.document)
async def collect_document(message: Message, bot: Bot, lang: str):
    doc = message.document
    if not check_file_size(doc.file_size or 0):
        await message.answer(get_text("error_file_too_large", lang))
        return

    user_id = message.from_user.id
    if user_id not in user_files:
        user_files[user_id] = []

    # If it's a ZIP — extract immediately
    if doc.file_name and doc.file_name.lower().endswith(".zip"):
        input_path = create_temp_path(suffix=".zip")
        extract_dir = None
        try:
            await bot.download(doc, destination=input_path)
            extract_dir = await extract_zip(input_path)
            files = list(extract_dir.rglob("*"))
            files = [f for f in files if f.is_file()]
            if not files:
                await message.answer(get_text("error_processing", lang))
                return

            await message.answer(get_text("zip_extracted", lang))
            for f in files[:10]:  # limit to 10 files for safety
                await message.answer_document(FSInputFile(f))
            if len(files) > 10:
                await message.answer(f"... and {len(files) - 10} more files")
        except Exception as e:
            logger.exception(e)
            await message.answer(get_text("error_processing", lang))
        finally:
            cleanup_file(input_path)
            if extract_dir:
                cleanup_dir(extract_dir)
        return

    # Collect for later ZIP
    suffix = Path(doc.file_name or "file").suffix
    path = create_temp_path(suffix=suffix)
    try:
        await bot.download(doc, destination=path)
        user_files[user_id].append(path)
        await message.answer(f"✅ {doc.file_name} added ({len(user_files[user_id])} files)")
    except Exception as e:
        logger.exception(e)
        cleanup_file(path)
        await message.answer(get_text("error_processing", lang))

@router.message(Command("zip"))
async def cmd_zip(message: Message, lang: str):
    user_id = message.from_user.id
    files = user_files.get(user_id, [])
    if not files:
        await message.answer(get_text("error_no_files_for_zip", lang))
        return

    zip_path = None
    try:
        zip_path = await create_zip(files)
        await message.answer_document(
            FSInputFile(zip_path, filename="megatools_archive.zip"),
            caption=get_text("zip_created", lang),
        )
    except Exception as e:
        logger.exception(e)
        await message.answer(get_text("error_processing", lang))
    finally:
        if zip_path:
            cleanup_file(zip_path)
        for f in files:
            cleanup_file(f)
        user_files[user_id] = []
