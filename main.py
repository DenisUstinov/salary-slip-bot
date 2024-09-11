import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram import types
from aiogram.filters import CommandStart

from salary_slip_bot.keyboards.reply import main_menu
from salary_slip_bot.database.sqlite import init_db

from salary_slip_bot.config import BOT_TOKEN, ALLOWED_UPDATES, USER_ID_LIST, CHAT_TYPE_LIST

from salary_slip_bot.filters.chat_types import ChatTypeFilter
from salary_slip_bot.filters.user_id import UserIdFilter
from salary_slip_bot.handlers.cancel import cancel_router
from salary_slip_bot.handlers.attendance import attendance_router
from salary_slip_bot.handlers.expenses import expenses_router
from salary_slip_bot.handlers.settings import settings_router
from salary_slip_bot.handlers.calculation import calculation_router
from salary_slip_bot.handlers.lists import lists_router
from salary_slip_bot.handlers.deleter import deleter_router
from salary_slip_bot.middlewares.check_user_database import UserDatabaseMiddleware

# Инициализация диспетчера событий
dp: Dispatcher = Dispatcher()

# Применение middleware
# dp.message.middleware(UserDatabaseMiddleware())

# Применение фильтров к сообщениям
dp.message.filter(ChatTypeFilter(CHAT_TYPE_LIST))
dp.message.filter(UserIdFilter(USER_ID_LIST))

@dp.message(CommandStart())
async def command_start_handler(message: types.Message) -> None:
    user_id = message.from_user.id
    
    await init_db(user_id)
    await message.answer(
        f"Привет, {message.from_user.full_name}!",
        reply_markup=main_menu()
    )

# Добавление маршрутизаторов
dp.include_routers(
    cancel_router,
    attendance_router,
    expenses_router,
    settings_router,
    calculation_router,
    lists_router,
    deleter_router
)

async def main() -> None:
    bot: Bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    logging.info("Starting in long-polling mode")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=ALLOWED_UPDATES)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('bot.log', mode='a')
        ]
    )
    asyncio.run(main())