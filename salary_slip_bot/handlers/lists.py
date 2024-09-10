from aiogram import F, Router
from aiogram.filters import or_f
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from salary_slip_bot.keyboards.reply import select_categories_type_keyboard, single_back_button_keyboard, select_action_type_keyboard
from salary_slip_bot.database.lists import add_item_to_list, get_all_lists  # Импортируем функции из нового файла

list_router = Router()

class FormList(StatesGroup):
    category = State()
    item = State()

@list_router.message(F.text == "Списки")
async def lists_handler(message: Message, state: FSMContext) -> None:
    await message.answer(
        "Выберите категорию!",
        reply_markup=select_categories_type_keyboard()
    )
    await state.set_state(FormList.category)

@list_router.message(FormList.category, or_f(F.text.in_(["Гигиена", "Аптечка", "Одежды", "Еда", "Развлечения", "Гаджеты", "Рыбалка", "Другое"])))
async def select_category_handler(message: Message, state: FSMContext) -> None:
    await state.update_data(category=message.text)
    await message.answer(
        "Введите новый элемент для добавления в категорию!",
        reply_markup=single_back_button_keyboard()
    )
    await state.set_state(FormList.item)

@list_router.message(FormList.item, F.text)
async def add_item_handler(message: Message, state: FSMContext) -> None:
    category = (await state.get_data()).get('category')
    item = message.text
    user_id = message.from_user.id
    await add_item_to_list(user_id, category, item)

    await message.answer(
        "Элемент добавлен!",
        reply_markup=select_categories_type_keyboard()
    )
    await state.clear()