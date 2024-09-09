from aiogram import F, Router
from aiogram.filters import or_f
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from salary_slip_bot.keyboards.reply import select_work_type_keyboard, single_back_button_keyboard
from salary_slip_bot.database.works import add_work_entry

attendance_router = Router()

class FormWork(StatesGroup):
    type = State()
    duration = State()
    

@attendance_router.message(F.text == "Табель")
@attendance_router.message(FormWork.duration, F.text == "Назад")
async def attendance_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "Выберите вид работ!",
        reply_markup=select_work_type_keyboard()
    )
    await state.set_state(FormWork.type)

@attendance_router.message(FormWork.type, or_f(F.text.in_(["Смена", "Подработка", "Ремонт"])))
async def select_work_type_handler(message: Message, state: FSMContext) -> None:
    await state.update_data(type=message.text)
    await message.answer(
        "Введите отработанные часы!",
        reply_markup=single_back_button_keyboard()
    )
    await state.set_state(FormWork.duration)

@attendance_router.message(FormWork.duration, F.text)
async def add_work_duration_handler(message: Message, state: FSMContext) -> None:
    try:
        duration = int(message.text)
    except ValueError:
        await message.answer("Ошибка: Введено не числовое значение. Пожалуйста, введите корректное число.")
        return

    user_id = message.from_user.id
    data = await state.get_data()
    type = data.get('type')

    await add_work_entry(user_id, type, duration)

    await message.answer(
        "Добавлено!",
        reply_markup=select_work_type_keyboard()
    )
    await state.clear()
    await state.set_state(FormWork.type)