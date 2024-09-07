from aiogram import F, Router
from aiogram.filters import or_f
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from salary_slip_bot.keyboards.reply import single_back_button_keyboard, select_expense_type_keyboard
from salary_slip_bot.database.expenses import add_expense_entry

expenses_router = Router()

class FormExpenses(StatesGroup):
    type = State()
    amount = State()
    custom_type = State()

@expenses_router.message(F.text == "Расходы")
async def expenses_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "Выберите тип расхода: Проезд, Медкомиссия или Другое.",
        reply_markup=select_expense_type_keyboard()
    )
    await state.set_state(FormExpenses.type)

@expenses_router.message(FormExpenses.type, F.text.in_(["Проезд", "Медкомиссия", "Столовая", "Другое"]))
async def select_expense_type_handler(message: Message, state: FSMContext) -> None:
    expense_type = message.text
    if expense_type == "Другое":
        await message.answer(
            "Введите тип расхода.",
            reply_markup=single_back_button_keyboard()
        )
        await state.set_state(FormExpenses.custom_type)
    else:
        await state.update_data(type=expense_type)
        await message.answer(
            "Введите сумму расхода.",
            reply_markup=single_back_button_keyboard()
        )
        await state.set_state(FormExpenses.amount)

@expenses_router.message(FormExpenses.custom_type, F.text.casefold() != "назад")
async def add_custom_expense_type_handler(message: Message, state: FSMContext) -> None:
    custom_type = message.text
    await state.update_data(type=custom_type)
    await message.answer(
        "Введите сумму расхода.",
        reply_markup=single_back_button_keyboard()
    )
    await state.set_state(FormExpenses.amount)

@expenses_router.message(FormExpenses.amount, F.text.casefold() != "назад")
async def add_expense_amount_handler(message: Message, state: FSMContext) -> None:
    try:
        amount = int(message.text)
    except ValueError:
        await message.answer("Ошибка: Введено не числовое значение. Пожалуйста, введите корректное число.")
        return

    user_id = message.from_user.id
    data = await state.get_data()
    expense_type = data.get('type')

    await add_expense_entry(user_id, expense_type, amount)

    await message.answer(
        "Расход добавлен!",
        reply_markup=select_expense_type_keyboard()
    )
    await state.clear()
    await state.set_state(FormExpenses.type)

@expenses_router.message(or_f(FormExpenses.custom_type, FormExpenses.amount), F.text.casefold() == "назад")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(FormExpenses.type)
    await message.answer("Действия отменены", reply_markup=select_expense_type_keyboard())