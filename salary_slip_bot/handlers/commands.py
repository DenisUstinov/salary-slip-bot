from aiogram import Router, types
from aiogram.filters import CommandStart
from salary_slip_bot.keyboards.reply import main_menu
from salary_slip_bot.database.sqlite import init_db

commands_router = Router()

@commands_router.message(CommandStart())
async def command_start_handler(message: types.Message) -> None:
    user_id = message.from_user.id
    
    await init_db(user_id)
    await message.answer(
        f"Привет, {message.from_user.full_name}!",
        reply_markup=main_menu()
    )