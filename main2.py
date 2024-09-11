import logging
import sys
from os import getenv

from aiohttp import web

from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

#from salary_slip_bot.config import BASE_WEBHOOK_URL, BOT_TOKEN, WEB_SERVER_HOST, WEB_SERVER_PORT, WEBHOOK_PATH, WEBHOOK_SECRET
from salary_slip_bot.database.sqlite import init_db
from salary_slip_bot.keyboards.reply import main_menu
from salary_slip_bot.handlers.cancel import cancel_router
from salary_slip_bot.handlers.attendance import attendance_router
from salary_slip_bot.handlers.expenses import expenses_router
from salary_slip_bot.handlers.settings import settings_router
from salary_slip_bot.handlers.calculation import calculation_router
from salary_slip_bot.handlers.lists import lists_router
from salary_slip_bot.handlers.deleter import deleter_router


TOKEN = getenv("BOT_TOKEN")

WEBHOOK_PATH = "/" + getenv("PROJECT_NAME")

DOMAIN = getenv("DOMAIN_NAME")

EXTERNAL_PORT = 8443

BASE_WEBHOOK_URL = "https://" + DOMAIN + ":" + str(EXTERNAL_PORT)

WEB_SERVER_HOST = "127.0.0.1"

WEB_SERVER_PORT = 8080

WEBHOOK_SECRET = "my-secret"

start_router = Router()

@start_router.message(CommandStart())
async def command_start_handler(message: types.Message) -> None:
    user_id = message.from_user.id

    await init_db(user_id)
    await message.answer(
        f"Привет, {message.from_user.full_name}!",
        reply_markup=main_menu()
    )

async def on_startup(bot: Bot) -> None:
    await bot.set_webhook(f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}", secret_token=WEBHOOK_SECRET)

async def on_shutdown(bot: Bot) -> None:
    await bot.delete_webhook()

def main() -> None:
    dp = Dispatcher()

    dp.include_routers(
        cancel_router,
        attendance_router,
        expenses_router,
        settings_router,
        calculation_router,
        lists_router,
        start_router,
        deleter_router
    )

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=WEBHOOK_SECRET,
    )
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main()