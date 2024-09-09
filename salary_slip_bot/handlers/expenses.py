from aiogram import F, Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from salary_slip_bot.keyboards.reply import single_back_button_keyboard, select_expense_type_keyboard
from salary_slip_bot.database.expenses import add_expense_entry

expenses_router = Router()

class FormExpenses(StatesGroup):
    type = State()
    amount = State()

@expenses_router.message(F.text == "Финансы")
@expenses_router.message(FormExpenses.amount, F.text == "Назад")
async def expenses_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "Выберите категорию:",
        reply_markup=select_expense_type_keyboard()
    )
    await state.set_state(FormExpenses.type)

@expenses_router.message(FormExpenses.type, F.text.in_(["Столовая", "Проезд", "Медкомиссия", "Переводы"]))
async def select_expense_type_handler(message: Message, state: FSMContext) -> None:
    await state.update_data(type=message.text)
    if message.text == "Переводы":
        await message.answer(
            "Введите сумму перевода.",
            reply_markup=single_back_button_keyboard()
        )
    else:
        await message.answer(
            "Введите сумму расхода.",
            reply_markup=single_back_button_keyboard()
        )
    await state.set_state(FormExpenses.amount)

@expenses_router.message(FormExpenses.amount, F.text)
async def add_expense_amount_handler(message: Message, state: FSMContext) -> None:
    try:
        amount = int(message.text)
    except ValueError:
        await message.answer("Ошибка: Введено не числовое значение. Пожалуйста, введите корректное число.")
        return

    user_id = message.from_user.id
    data = await state.get_data()
    finance_type = data.get('type')

    if finance_type == "Переводы":
        await add_expense_entry(user_id, finance_type, amount)
        await message.answer(
            "Перевод добавлен!",
            reply_markup=select_expense_type_keyboard()
        )
    else:
        await add_expense_entry(user_id, finance_type, amount)
        await message.answer(
            "Расход добавлен!",
            reply_markup=select_expense_type_keyboard()
        )

    await state.clear()
    await state.set_state(FormExpenses.type)