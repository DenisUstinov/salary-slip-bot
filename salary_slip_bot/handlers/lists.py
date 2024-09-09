from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from salary_slip_bot.keyboards.reply import select_action_type_keyboard
from aiogram.fsm.context import FSMContext
from salary_slip_bot.database.lists import get_all_lists

lists_router = Router()

@lists_router.message(F.text == "Незабыть")
async def show_lists_handler(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    rows = await get_all_lists(user_id)
    await message.answer(
        "В",
        reply_markup=select_action_type_keyboard()
    )
    
    buttons = [InlineKeyboardButton(text=item_text, callback_data=f"list_{item_id}") for item_id, item_text in rows]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])
    
    await message.answer(
        "Вот все ваши записи:",
        reply_markup=keyboard
    )