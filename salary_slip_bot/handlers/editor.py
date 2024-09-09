from aiogram import F, Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from datetime import datetime
import re

from salary_slip_bot.database.works import get_works_within_period, delete_work_entry
from salary_slip_bot.database.expenses import get_expenses_within_period, delete_expense_entry
from salary_slip_bot.keyboards.reply import main_menu, single_cancel_button_keyboard

editor_router = Router()

class FormEditor(StatesGroup):
    start = State()
    stop = State()

@editor_router.message(F.text == "Редактор")
async def editor_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "Введите дату начала периода (формат: DD-MM-YYYY):",
        reply_markup=single_cancel_button_keyboard()
    )
    await state.set_state(FormEditor.start)

@editor_router.message(FormEditor.start, F.text)
async def editor_start_handler(message: Message, state: FSMContext) -> None:
    date_pattern = re.compile(r'^\d{2}-\d{2}-\d{4}$')
    if not date_pattern.match(message.text):
        await message.answer("Ошибка: Неправильный формат даты. Пожалуйста, используйте формат DD-MM-YYYY.")
        return

    try:
        date_obj = datetime.strptime(message.text, '%d-%m-%Y')
        start_timestamp = int(date_obj.timestamp())
    except ValueError as e:
        await message.answer(f"Ошибка при преобразовании даты: {str(e)}")
        return

    await state.update_data(start=start_timestamp)
    await message.answer(
        "Введите дату окончания периода (формат: DD-MM-YYYY):",
        reply_markup=single_cancel_button_keyboard()
    )
    await state.set_state(FormEditor.stop)

@editor_router.message(FormEditor.stop, F.text)
async def editor_stop_handler(message: Message, state: FSMContext) -> None:
    date_pattern = re.compile(r'^\d{2}-\d{2}-\d{4}$')
    if not date_pattern.match(message.text):
        await message.answer("Ошибка: Неправильный формат даты. Пожалуйста, используйте формат DD-MM-YYYY.")
        return

    try:
        date_obj = datetime.strptime(message.text, '%d-%m-%Y')
        stop_timestamp = int(date_obj.timestamp())
    except ValueError as e:
        await message.answer(f"Ошибка при преобразовании даты: {str(e)}")
        return

    data = await state.get_data()
    start_timestamp = data.get('start')
    user_id = message.from_user.id

    # Получаем записи за период
    works = await get_works_within_period(user_id, start_timestamp, stop_timestamp)
    expenses = await get_expenses_within_period(user_id, start_timestamp, stop_timestamp)

    # Если данных нет
    if not works and not expenses:
        await message.answer("Нет данных за указанный период.", reply_markup=main_menu())
        await state.clear()
        return

    # Формируем текст вывода
    response_text = "Записи за указанный период:\n\n"

    if works:
        response_text += "Работы:\n"
        for work in works:
            work_id, work_type, duration, timestamp = work
            # date = datetime.fromtimestamp(timestamp).strftime('%d-%m-%Y')
            response_text += f"{work_id}. {work_type} - {duration} ч\n"
            # response_text += f"/wd{work_id}\n"  # Команда для удаления работы

    if expenses:
        response_text += "\nРасходы:\n"
        for expense in expenses:
            expense_id, expense_type, amount, timestamp = expense
            # date = datetime.fromtimestamp(timestamp).strftime('%d-%m-%Y')
            response_text += f"{expense_id}. {expense_type} - {amount} руб\n"
            # response_text += f"/ed{expense_id}\n"  # Команда для удаления расхода

    await message.answer(response_text, reply_markup=main_menu())
    await state.clear()

@editor_router.message(F.text.regexp(r'^/(wd|ed)(\d+)$'))
async def delete_record_handler(message: Message) -> None:
    # Извлекаем тип команды и ID записи
    match = re.match(r'^/(wd|ed)(\d+)$', message.text)
    
    if not match:
        await message.answer("Неправильный формат команды.")
        return
    
    command_type, record_id = match.groups()
    record_id = int(record_id)
    user_id = message.from_user.id

    # Проверяем тип команды и вызываем соответствующий метод удаления
    if command_type == "wd":
        success = await delete_work_entry(user_id, record_id)
        if success:
            await message.answer(f"Запись о работе с ID {record_id} успешно удалена.")
        else:
            await message.answer(f"Ошибка: запись о работе с ID {record_id} не найдена.")
    
    elif command_type == "ed":
        success = await delete_expense_entry(user_id, record_id)
        if success:
            await message.answer(f"Запись о расходе с ID {record_id} успешно удалена.")
        else:
            await message.answer(f"Ошибка: запись о расходе с ID {record_id} не найдена.")