import logging
from os import getenv

from aiohttp import web

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from salary_slip_bot.handlers.cancel import cancel_router
from salary_slip_bot.handlers.attendance import attendance_router
from salary_slip_bot.handlers.expenses import expenses_router
from salary_slip_bot.handlers.settings import settings_router
from salary_slip_bot.handlers.calculation import calculation_router
from salary_slip_bot.handlers.lists import lists_router
from salary_slip_bot.handlers.start import start_router
from salary_slip_bot.handlers.deleter import deleter_router


TOKEN = getenv("BOT_TOKEN")
WEBHOOK_PATH = "/" + getenv("PROJECT_NAME")
DOMAIN = getenv("DOMAIN_NAME")
EXTERNAL_PORT = 8443
BASE_WEBHOOK_URL = "https://" + DOMAIN + ":" + str(EXTERNAL_PORT)
WEB_SERVER_HOST = "127.0.0.1"
WEB_SERVER_PORT = 8080
WEBHOOK_SECRET = "my-secret"

async def on_startup(bot: Bot) -> None:
    await bot.set_webhook(f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}", secret_token=WEBHOOK_SECRET)

async def on_shutdown(bot: Bot) -> None:
    await bot.delete_webhook()

def main() -> None:
    dp = Dispatcher()

    dp.include_routers(
        start_router,
        cancel_router,
        attendance_router,
        expenses_router,
        settings_router,
        calculation_router,
        lists_router,
        deleter_router
    )

    bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

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
    logging.basicConfig(level=logging.INFO, filename="app.log", filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    main()