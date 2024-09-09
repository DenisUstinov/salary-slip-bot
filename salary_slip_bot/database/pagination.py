from aiogram import F, Router
from aiogram.filters import or_f
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

pagination_router = Router()

# Машина состояний для управления выбором и редактированием
class EditState(StatesGroup):
    choose_table = State()  # Состояние выбора таблицы (Работа, Расходы)
    pagination = State()  # Состояние для пагинации записей

# Количество записей на одной странице
ITEMS_PER_PAGE = 5

# Функция для получения записей из базы данных (замените на реальный запрос)
async def get_records(user_id: int, table: str, offset: int, limit: int):
    if table == "works":
        records = [(i, f"Работа {i}") for i in range(1, 21)]
    elif table == "expenses":
        records = [(i, f"Расход {i}") for i in range(1, 21)]
    return records[offset:offset + limit]

# Функция для создания реплай-клавиатуры для выбора таблицы
def create_table_selection_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton(text="Табель"), KeyboardButton(text="Расходы"))
    return keyboard

# Функция для создания реплай-клавиатуры для отмены
def single_back_button_keyboard():
    return ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton(text="Назад"))

# Хендлер для начала процесса редактирования (выбор таблицы)
@pagination_router.message(F.text == "Редактировать")
async def edit_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    keyboard = create_table_selection_keyboard()
    await message.answer("Выберите данные для редактирования:", reply_markup=keyboard)
    await state.set_state(EditState.choose_table)

# Хендлер для обработки выбора таблицы
@pagination_router.message(or_f(F.text == "Табель", F.text == "Расходы"))
async def choose_table_handler(message: Message, state: FSMContext) -> None:
    if message.text == "Табель":
        table = 'works'
    else:
        table = 'expenses'
    
    await state.update_data(table=table)
    await message.answer(f"Вы выбрали таблицу: {'Табель' if table == 'works' else 'Расходы'}", reply_markup=single_back_button_keyboard())
    
    # Переход к пагинации по записям
    page = 0
    user_id = message.from_user.id
    records = await get_records(user_id, table, page * ITEMS_PER_PAGE, ITEMS_PER_PAGE)
    keyboard = await create_pagination_keyboard(records, page)
    await message.answer("Выберите запись для редактирования:", reply_markup=keyboard)
    
    await state.set_state(EditState.pagination)

# Функция создания клавиатуры для пагинации
async def create_pagination_keyboard(records, page):
    keyboard_buttons = []
    for record_id, record_name in records:
        button_text = f"{record_name} (ID: {record_id})"
        keyboard_buttons.append([KeyboardButton(text=button_text)])

    # Добавляем кнопки для навигации
    navigation_buttons = []
    if page > 0:
        navigation_buttons.append(KeyboardButton(text="⬅ Назад"))
    navigation_buttons.append(KeyboardButton(text="➡ Вперед"))

    keyboard_buttons.append(navigation_buttons)
    return ReplyKeyboardMarkup(keyboard=keyboard_buttons, resize_keyboard=True)

# Хендлер для обработки пагинации и выбора записи
@pagination_router.message(EditState.pagination, or_f(F.text.contains("➡ Вперед"), F.text.contains("⬅ Назад")))
async def pagination_navigation_handler(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    table = data['table']
    user_id = message.from_user.id

    if "➡ Вперед" in message.text:
        page = data.get('page', 0) + 1
    elif "⬅ Назад" in message.text:
        page = max(data.get('page', 0) - 1, 0)

    # Обновляем страницу в состоянии
    await state.update_data(page=page)

    # Получаем записи для новой страницы
    records = await get_records(user_id, table, page * ITEMS_PER_PAGE, ITEMS_PER_PAGE)
    keyboard = await create_pagination_keyboard(records, page)

    await message.answer("Выберите запись для редактирования:", reply_markup=keyboard)

# Хендлер для обработки выбора конкретной записи
@pagination_router.message(EditState.pagination, F.text.contains("(ID:"))
async def select_record_handler(message: Message, state: FSMContext) -> None:
    record_id = int(message.text.split("(ID: ")[1].rstrip(")"))
    data = await state.get_data()
    table = data['table']

    await message.answer(f"Вы выбрали запись с ID {record_id} из таблицы {table}.", reply_markup=single_back_button_keyboard())
    # Здесь можно добавить логику редактирования выбранной записи