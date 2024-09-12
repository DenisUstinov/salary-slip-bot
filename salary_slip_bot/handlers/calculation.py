import io
from typing import List, Tuple, Dict
from aiogram import F, Router
from aiogram.types import Message, BufferedInputFile
from aiogram.filters.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from datetime import datetime
import re

from salary_slip_bot.keyboards.reply import main_menu, single_back_button_keyboard, single_cancel_button_keyboard
from salary_slip_bot.database.works import get_works_within_period
from salary_slip_bot.database.expenses import get_expenses_within_period
from salary_slip_bot.database.settings import get_settings

calculation_router = Router()

class FormRotation(StatesGroup):
    start = State()
    stop = State()

@calculation_router.message(F.text == "Расчетка")
@calculation_router.message(FormRotation.stop, F.text == "Назад")
async def calculation_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "Введите дату начала вахты (формат: DD-MM-YYYY)!",
        reply_markup=single_cancel_button_keyboard()
    )
    await state.set_state(FormRotation.start)

@calculation_router.message(FormRotation.start, F.text)
async def add_date_start_handler(message: Message, state: FSMContext) -> None:
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
        "Введите дату окончания вахты (формат: DD-MM-YYYY)!",
        reply_markup=single_back_button_keyboard()
    )
    await state.set_state(FormRotation.stop)

@calculation_router.message(FormRotation.stop, F.text)
async def add_date_stop_handler(message: Message, state: FSMContext) -> None:
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
    
    settings = await get_settings(user_id)
    if not settings:
        await message.answer(
            "Настройки пользователя отсутствуют.",
            reply_markup=main_menu()
        )
        await state.clear()
        return
    
    works = await get_works_within_period(user_id, start_timestamp, stop_timestamp)

    # Получаем расходы по типам
    meal_expenses = await get_expenses_within_period(user_id, start_timestamp, stop_timestamp, 'Столовая')
    travel_expenses = await get_expenses_within_period(user_id, start_timestamp, stop_timestamp, 'Проезд')
    medical_expenses = await get_expenses_within_period(user_id, start_timestamp, stop_timestamp, 'Медкомиссия')
    transfers_expenses = await get_expenses_within_period(user_id, adjust_stop_timestamp(start_timestamp, 1), adjust_stop_timestamp(stop_timestamp, 2), 'Переводы')
    print(adjust_stop_timestamp(start_timestamp, 1), adjust_stop_timestamp(stop_timestamp, 2))
    if not works:
        await message.answer(
            "Нет данных за указанный период.",
            reply_markup=main_menu()
        )
        await state.clear()
        return

    # 1. Рассчитываем стоимость за отработанное время
    costs = calculate_work_costs(works, settings)

    # 2. Считаем стоимость питания
    total_meal_cost = calculate_total_expenses_payment(meal_expenses)

    # 3. Считаем расходы на проезд и медкомиссию
    total_travel_expenses = calculate_total_expenses_payment(travel_expenses)
    total_medical_expenses = calculate_total_expenses_payment(medical_expenses)

    total_salary_transfers = calculate_total_expenses_payment(transfers_expenses)

    # 4. Формируем вывод расчета
    meal_compensation = settings[4]
    shift_rate = settings[1]
    repairing_rate = settings[2]
    moonlighting_rate = settings[3]

    total_meal_balance = meal_compensation - total_meal_cost
    salary = costs['total_cost'] + total_meal_balance + total_travel_expenses + total_medical_expenses

    calculation_text = f"""
    +--------------------------------------------------------
    |                    Расчетный лист
    +--------------------------------------------------------
    | Питание
    |    компенсация: {meal_compensation} руб
    |    списания: {total_meal_cost} руб
    |    ------
    |    Остаток: {total_meal_balance} руб
    +--------------------------------------------------------
    | Отработано
    |    смены: {costs['shift_hours']} ч
    |    подработка: {costs['repairing_hours']} ч
    |    ремонт: {costs['moonlighting_hours']} ч
    |    ------
    |    Всего: {costs['shift_hours'] + costs['repairing_hours'] + costs['moonlighting_hours']} ч
    +--------------------------------------------------------
    | Начисления
    |    за смены: {costs['shift_hours']} * {shift_rate} = {costs['shift_cost']} руб
    |    за подработку: {costs['repairing_hours']} * {repairing_rate} = {costs['repairing_cost']} руб
    |    за ремонты: {costs['moonlighting_hours']} * {moonlighting_rate} = {costs['moonlighting_cost']} руб
    |    за питание: {total_meal_balance} руб
    |    за проезд: {total_travel_expenses} руб
    |    за медкомиссию: {total_medical_expenses} руб
    |    ------
    |    Итого: {salary} руб
    +--------------------------------------------------------
    | Всего получено оплаты: {total_salary_transfers} руб
    | Задолженность за работодателем: {salary - total_salary_transfers} руб
    +--------------------------------------------------------
    """
    await message.answer(calculation_text)

    # 5. Создаём файл в памяти с использованием BytesIO
    file_buffer = io.BytesIO()
    file_buffer.write(calculation_text.encode('utf-8'))
    file_buffer.seek(0)  # Устанавливаем указатель на начало файла

    # 6. Превращаем BytesIO в BufferedInputFile
    input_file = BufferedInputFile(file_buffer.read(), filename=f"calculation_{user_id}.txt")

    # 7. Отправляем файл пользователю
    await message.answer_document(input_file, reply_markup=main_menu())
    await state.clear()

def calculate_work_costs(
    works: List[Tuple[int, str, int, int]], 
    settings: Tuple[int, int, int, int, int]
) -> Dict[str, int]:
    _, shift_hour_rate, repairing_hour_rate, moonlighting_hour_rate, meal_compensation = settings
    
    # Инициализация суммарных значений и сумм
    total_shift_hours = 0
    total_repairing_hours = 0
    total_moonlighting_hours = 0
    
    total_cost_shift = 0
    total_cost_repairing = 0
    total_cost_moonlighting = 0
    
    # Обработка каждого типа работы
    for work in works:
        _, work_type, duration, _ = work
        
        if work_type == 'Смена':
            total_shift_hours += duration
            total_cost_shift += duration * shift_hour_rate
        elif work_type == 'Подработка':
            total_repairing_hours += duration
            total_cost_repairing += duration * repairing_hour_rate
        elif work_type == 'Ремонт':
            total_moonlighting_hours += duration
            total_cost_moonlighting += duration * moonlighting_hour_rate
    
    # Учет ограничений на часы ремонта
    if total_moonlighting_hours > 33:
        excess_moonlighting_hours = total_moonlighting_hours - 33
        total_moonlighting_hours = 33
        total_shift_hours += excess_moonlighting_hours
        total_cost_shift += excess_moonlighting_hours * shift_hour_rate
    
    # Общая стоимость
    overall_total_cost = total_cost_shift + total_cost_repairing + total_cost_moonlighting
    
    return {
        'shift_hours': total_shift_hours, # общее количество часов смен
        'repairing_hours': total_repairing_hours, # общее количество часов подработки
        'moonlighting_hours': total_moonlighting_hours, # общее количество часов ремонта
        'shift_cost': total_cost_shift, # начислена за отработанные часы смен
        'repairing_cost': total_cost_repairing, # начислена за отработанные часы подработки
        'moonlighting_cost': total_cost_moonlighting, # начислена за отработанные часы ремонта
        'total_cost': overall_total_cost, # общий заработок вообще за ремонты, подработку и смены
        'meal_compensation': meal_compensation # денежная компенсация за питание
    }

def calculate_total_expenses_payment(expenses: List[Tuple[int, int, int, int]]) -> int:
    total_expenses = 0

    for expense in expenses:
        _, _, payment, _ = expense
        total_expenses += payment

    return total_expenses

def adjust_stop_timestamp(stop_timestamp: int, months_to_add: int) -> int:
    # Преобразуем временную метку UNIX в объект datetime
    stop_date = datetime.fromtimestamp(stop_timestamp)

    # Определяем новый месяц и год, учитывая переход через декабрь (месяц 12)
    new_month = (stop_date.month + months_to_add) % 12
    new_year = stop_date.year + (stop_date.month + months_to_add) // 12

    # Если new_month стал равен 0 (то есть январь), корректируем его на 12
    if new_month == 0:
        new_month = 12
        new_year -= 1  # Возвращаем год на предыдущий

    # Создаем новую дату с корректированными месяцем и годом, устанавливаем день 10
    new_stop_date = stop_date.replace(month=new_month, year=new_year, day=10)

    # Преобразуем новую дату обратно в временную метку UNIX
    return int(new_stop_date.timestamp())