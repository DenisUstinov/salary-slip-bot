from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from salary_slip_bot.keyboards.reply import main_menu

cancel_router = Router()

@cancel_router.message(StateFilter('*'), F.text.casefold() == "отмена")
async def cancel_handler(message: Message, state: FSMContext) -> None:

    #current_state = await state.get_state()
    #if current_state is None:
    #    return

    await state.clear()
    await message.answer("Действия отменены", reply_markup=main_menu())