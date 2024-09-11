from aiogram import F, Router


@dp.message(CommandStart())
async def command_start_handler(message: types.Message) -> None:
    user_id = message.from_user.id

    await init_db(user_id)
    await message.answer(
        f"Привет, {message.from_user.full_name}!",
        reply_markup=main_menu()
    )