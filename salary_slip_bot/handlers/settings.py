from aiogram import F, Router
from aiogram.filters import or_f
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from salary_slip_bot.keyboards.reply import select_settings_type_keyboard, select_pricing_type_keyboard, single_back_button_keyboard
from salary_slip_bot.database.settings import update_meal_compensation, update_pricing

settings_router = Router()

class FormSettings(StatesGroup):
    start = State()

class FormPricing(StatesGroup):
    pricing_type = State()
    hour_price = State()

class FormMealCompensation(StatesGroup):
    meal_compensation = State()

@settings_router.message(F.text == "Настройки")
@settings_router.message(or_f(FormSettings.start, FormPricing.pricing_type), F.text == "Назад")
async def settings_handler(message: Message, state: FSMContext) -> None:
    await message.answer(
        "Выберите вид настроек!",
        reply_markup=select_settings_type_keyboard()
    )
    await state.set_state(FormSettings.start)

@settings_router.message(FormSettings.start, F.text == "Расценки")
@settings_router.message(or_f(FormPricing.hour_price, FormMealCompensation.meal_compensation), F.text == "Назад")
async def pricing_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "Выберите вид работ!",
        reply_markup=select_pricing_type_keyboard()
    )
    await state.set_state(FormPricing.pricing_type)

@settings_router.message(FormPricing.pricing_type, or_f(F.text.in_({"Смена", "Подработка", "Ремонт"})))
async def select_pricing_type_handler(message: Message, state: FSMContext) -> None:
    await state.update_data(pricing_type=message.text)
    await message.answer(
        "Введите стоимость часа!",
        reply_markup=single_back_button_keyboard()
    )
    await state.set_state(FormPricing.hour_price)

@settings_router.message(FormPricing.hour_price, F.text)
async def add_hour_price_handler(message: Message, state: FSMContext) -> None:
    try:
        hour_price = int(message.text)
    except ValueError:
        await message.answer("Ошибка: Введено не числовое значение. Пожалуйста, введите корректное число.")
        return

    data = await state.get_data()
    pricing_type = data.get('pricing_type')

    await update_pricing(message.from_user.id, pricing_type, hour_price)

    await message.answer(
        "Стоимость обновлена!",
        reply_markup=select_pricing_type_keyboard()
    )
    await state.clear()
    await state.set_state(FormPricing.pricing_type)

@settings_router.message(FormPricing.pricing_type, F.text == "Питание")
async def meal_compensation_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "Введите сумму компенсации за питание!",
        reply_markup=single_back_button_keyboard()
    )
    await state.set_state(FormMealCompensation.meal_compensation)

@settings_router.message(FormMealCompensation.meal_compensation, F.text)
async def add_meal_compensation_handler(message: Message, state: FSMContext) -> None:
    try:
        meal_compensation = int(message.text)
    except ValueError:
        await message.answer("Ошибка: Введено не числовое значение. Пожалуйста, введите корректное число.")
        return

    await update_meal_compensation(message.from_user.id, meal_compensation)

    await message.answer(
        "Компенсация за питание обновлена!",
        reply_markup=select_pricing_type_keyboard()
    )
    await state.clear()
    await state.set_state(FormPricing.pricing_type)