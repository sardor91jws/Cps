from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User
from utils.database import get_user_language
from config import DEFAULT_LANGUAGE

class I18nMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user: User | None = data.get("event_from_user")
        lang = DEFAULT_LANGUAGE
        if user:
            stored = await get_user_language(user.id)
            if stored:
                lang = stored
        data["lang"] = lang
        return await handler(event, data)
