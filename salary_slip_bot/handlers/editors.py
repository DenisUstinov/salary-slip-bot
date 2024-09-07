from aiogram import F, Router
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, BufferedInputFile
from aiogram.filters.callback_data import CallbackData
from salary_slip_bot.keyboards.reply import single_cancel_button_keyboard
from salary_slip_bot.database.sqlite import get_last_rotations, get_settings, get_works_within_period
import datetime

from utils.generate_image import generate_image
from utils.calculations import calculate_work_costs

calculation_router = Router()

# Измененный CallbackData
class RotationCallback(CallbackData, prefix="rotation"):
    start: int
    stop: int
    id: int

@calculation_router.message(F.text == "Расчетка")
async def calculation_handler(message: Message) -> None:
    user_id = message.from_user.id
    rotations = await get_last_rotations(user_id)

    keyboard_buttons = []
    for rotation in rotations:
        rotation_id, start, stop = rotation

        callback_data = RotationCallback(start=int(start), stop=int(stop), id=int(rotation_id)).pack()

        start_date = datetime.datetime.fromtimestamp(start).strftime('%d.%m.%Y')
        stop_date = datetime.datetime.fromtimestamp(stop).strftime('%d.%m.%Y')
        button_text = f"{start_date} - {stop_date}"
        keyboard_buttons.append([InlineKeyboardButton(text=button_text, callback_data=callback_data)])

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

    await message.answer(
        f"Выберите запись для дальнейшей обработки:",
        reply_markup=keyboard
    )

# Хендлер для обработки обратного вызова
@calculation_router.callback_query(RotationCallback.filter())
async def rotation_callback_handler(query: CallbackQuery, callback_data: RotationCallback) -> None:
    user_id = query.from_user.id
    start_date = callback_data.start
    stop_date = callback_data.stop

    # Получаем настройки и данные о работах
    settings = await get_settings(user_id)
    works = await get_works_within_period(user_id, start_date, stop_date)

    if not settings:
        await query.message.answer(
            "Настройки пользователя отсутствуют. Пожалуйста, установите настройки и попробуйте снова.",
            reply_markup=single_cancel_button_keyboard()
        )
        return

    if not works:
        await query.message.answer(
            "Нет данных о работах в указанном периоде. Пожалуйста, проверьте правильность указанных дат и попробуйте снова.",
            reply_markup=single_cancel_button_keyboard()
        )
        return

    # Если все данные есть, продолжаем обработку
    costs = calculate_work_costs(works, settings)

    pricing_hour_shift = costs['shift']
    pricing_hour_repairing = costs['repairing']
    pricing_hour_moonlighting = costs['moonlighting']
    total_shift_hours = costs['shift']
    total_repairing_hours = costs['repairing']
    total_moonlighting_hours = costs['moonlighting']
    total_cost_shift = costs['shift']
    total_cost_repairing = costs['repairing']
    total_cost_moonlighting = costs['moonlighting']
    overall_total_cost = costs['overall_total']

    # Генерация изображения
    image_buffer = generate_image(
        pricing_hour_shift, pricing_hour_repairing, pricing_hour_moonlighting,
        total_shift_hours, total_repairing_hours, total_moonlighting_hours,
        total_cost_shift, total_cost_repairing, total_cost_moonlighting,
        overall_total_cost
    )

    # Создаем объект BufferedInputFile на основе буфера изображения
    image_file = BufferedInputFile(image_buffer.read(), filename="calculation.png")

    # Отправка изображения
    await query.message.answer_photo(photo=image_file, reply_markup=single_cancel_button_keyboard())

    # Удаление предыдущего сообщения
    await query.message.delete()