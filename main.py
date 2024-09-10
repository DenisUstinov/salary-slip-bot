import asyncio
import logging
import sys
import ssl
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram.types import FSInputFile

from salary_slip_bot.config import (
    BOT_TOKEN, ALLOWED_UPDATES, USER_ID_LIST, CHAT_TYPE_LIST, ENV,
    SELF_SSL, DOMAIN, WEBHOOK_PATH, EXTERNAL_PORT, BASE_WEBHOOK_URL, 
    WEB_SERVER_HOST, WEB_SERVER_PORT, WEBHOOK_SECRET, WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV
)
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

async def on_startup(bot: Bot) -> None:
    if SELF_SSL:
        # Если используешь самоподписанный сертификат, отправь его в Telegram
        await bot.set_webhook(
            f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}",
            certificate=FSInputFile(WEBHOOK_SSL_CERT),
            secret_token=WEBHOOK_SECRET,
        )
    else:
        # Установка вебхука для обычного домена
        await bot.set_webhook(f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}", secret_token=WEBHOOK_SECRET)

async def on_shutdown(bot: Bot) -> None:
    # Удаление вебхука при завершении работы бота
    await bot.delete_webhook()

def setup_webhook(app, dp, bot):
    # Создание экземпляра обработчика запросов для вебхуков
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=WEBHOOK_SECRET,
    )
    # Регистрация обработчика вебхуков на маршруте
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    # Настройка приложения aiohttp с хендлерами бота
    setup_application(app, dp, bot=bot)

async def main() -> None:
    bot: Bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    if ENV == "LOCAL":
        # Удаление вебхука и работа с long-polling
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=ALLOWED_UPDATES)
    else:
        # Настройка вебхуков для окружения
        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)

        # Создание aiohttp приложения
        app = web.Application()
        setup_webhook(app, dp, bot)

        if SELF_SSL:
            context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
            context.load_cert_chain(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV)
            web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT, ssl_context=context)
        else:
            web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)

if __name__ == "__main__":
    if ENV == "LOCAL":
        # Логирование для локальной среды
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('bot.log', mode='a')
            ]
        )
    else:
        # Логирование для продакшена
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('bot.log', mode='a')
            ]
        )

    # Запуск основной асинхронной функции
    asyncio.run(main())