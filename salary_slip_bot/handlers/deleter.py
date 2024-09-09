from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from salary_slip_bot.keyboards.reply import main_menu

deleter_router = Router()

@deleter_router.message()
async def handle_and_delete_message(message: Message, state: FSMContext):
        await state.clear()
        await message.answer(
            "Неопознанная команда!",
            reply_markup=main_menu()
        )
        await message.delete()