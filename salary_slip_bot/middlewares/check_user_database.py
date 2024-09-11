from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message
from salary_slip_bot.database.sqlite import check_user_db_exists

class UserDatabaseMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id

        # Проверяем наличие базы данных для пользователя
        db_exists = await check_user_db_exists(user_id)

        if not db_exists:  
            await event.reply(
                "Для начала работы с ботом необходимо создать базу данных. Пожалуйста, нажмите кнопку ниже /start, чтобы запустить бота."
            )
            return  # Не передаем обработку дальше

        return await handler(event, data)