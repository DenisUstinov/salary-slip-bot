import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from salary_slip_bot.config import BOT_TOKEN, ALLOWED_UPDATES, USER_ID_LIST, CHAT_TYPE_LIST, ENV
from salary_slip_bot.filters.chat_types import ChatTypeFilter
from salary_slip_bot.filters.user_id import UserIdFilter

from salary_slip_bot.handlers.cancel import cancel_router
from salary_slip_bot.handlers.commands import commands_router
from salary_slip_bot.handlers.attendance import attendance_router
from salary_slip_bot.handlers.expenses import expenses_router
from salary_slip_bot.handlers.settings import settings_router
from salary_slip_bot.handlers.calculation import calculation_router
from salary_slip_bot.handlers.lists import lists_router

from salary_slip_bot.handlers.deleter import deleter_router


# Инициализация диспетчера событий
dp: Dispatcher = Dispatcher()

# Применение фильтров к сообщениям: фильтр по типу чата и по ID пользователей
dp.message.filter(ChatTypeFilter(CHAT_TYPE_LIST))
dp.message.filter(UserIdFilter(USER_ID_LIST))

# Добавление маршрутизаторов для обработки команд и сообщений
dp.include_routers(
    cancel_router,
    commands_router,
    attendance_router,
    expenses_router,
    settings_router,
    calculation_router,
    lists_router,
    
    deleter_router
)

async def main() -> None:
    bot: Bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    
    # Удаление вебхука и сброс ожидающих обновлений
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Запуск long-polling с заданными типами обновлений
    await dp.start_polling(bot, allowed_updates=ALLOWED_UPDATES)

if __name__ == "__main__":
    if ENV == "LOCAL":
        # Настройка логирования для вывода информации в файл и в консоль
        logging.basicConfig(
            level=logging.DEBUG,  # Устанавливаем уровень логирования на DEBUG
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),  # Выводим логи в консоль
                logging.FileHandler('bot.log', mode='a')  # Записываем логи в файл bot.log
            ]
        )
    else:  # PROD или любое другое значение
        # Настройка логирования только для записи в файл
        logging.basicConfig(
            level=logging.INFO,  # Устанавливаем уровень логирования на INFO или нужный вам
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('bot.log', mode='a')  # Записываем логи в файл bot.log
            ]
        )
    
    # Запуск основной асинхронной функции
    asyncio.run(main())