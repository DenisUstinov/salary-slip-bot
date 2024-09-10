from typing import List, Dict, Tuple
from aiogram import F, Router
from aiogram.filters import or_f
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from salary_slip_bot.keyboards.reply import select_categories_type_keyboard, single_back_button_keyboard, select_action_type_keyboard
from salary_slip_bot.database.lists import add_item_to_list, get_all_lists, delete_item_to_list

lists_router = Router()

class FormList(StatesGroup):
    action = State()
    header = State()
    item = State()
    id = State()

@lists_router.message(F.text == "Списки")
@lists_router.message(or_f(FormList.header, FormList.id), F.text == "Назад")
async def lists_selection_handler(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    lists = await get_all_lists(user_id)
    if not lists:
        await message.answer("Список пуст.")
        return
    lists_dict = transform_lists_to_dict(lists)
    response_message = format_list_items_message(lists_dict)
    await message.answer(
        response_message,
        reply_markup=select_action_type_keyboard()
    )
    await state.set_state(FormList.action)

@lists_router.message(FormList.action, F.text == "Показать")
async def show_lists_handler(message: Message, state: FSMContext) -> None:  # Было select_action_handler
    user_id = message.from_user.id
    lists = await get_all_lists(user_id)
    if not lists:
        await message.answer("Список пуст.")
        return
    lists_dict = transform_lists_to_dict(lists)
    response_message = format_list_items_message(lists_dict)  # Переименовано format_lists_message
    
    await message.answer(response_message)
    await state.set_state(FormList.action)

@lists_router.message(FormList.action, F.text == "Удалить")
async def delete_list_item_handler(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    lists = await get_all_lists(user_id)
    if not lists:
        await message.answer("Список пуст.")
        return
    
    response_message = "Вот ваши элементы с их идентификаторами:\n\n"
    for record in lists:
        record_id, header, item = record
        response_message += f"{record_id}: {item}\n"
    
    response_message += "\nВведите идентификатор записи, чтобы удалить её:"
    await message.answer(response_message, reply_markup=single_back_button_keyboard())
    await state.set_state(FormList.id)

@lists_router.message(FormList.id, F.text)
async def delete_item_handler(message: Message, state: FSMContext) -> None:  # Переименовано из add_item_handler
    id = message.text
    user_id = message.from_user.id
    await delete_item_to_list(user_id, id)
    await message.answer(
        "Элемент успешно удален!",
        reply_markup=select_action_type_keyboard()
    )
    await state.clear()
    await state.set_state(FormList.action)

@lists_router.message(FormList.action, F.text == "Добавить")
@lists_router.message(FormList.item, F.text == "Назад")
async def add_list_item_handler(message: Message, state: FSMContext) -> None:  # Было select_action_handler
    await message.answer(
        "Выберите категорию:",
        reply_markup=select_categories_type_keyboard()
    )
    await state.set_state(FormList.header)

@lists_router.message(FormList.header, F.text.in_(["Гигиена", "Аптечка", "Одежда", "Еда", "Развлечения", "Гаджеты", "Канцелярия", "Работа", "Рыбалка", "Другое"]))
async def select_header_handler(message: Message, state: FSMContext) -> None:
    await state.update_data(header=message.text)
    await message.answer(
        "Введите элемент списка:",
        reply_markup=single_back_button_keyboard()
    )
    await state.set_state(FormList.item)

@lists_router.message(FormList.item, F.text)
async def add_item_handler(message: Message, state: FSMContext) -> None:
    header = (await state.get_data()).get('header')
    item = message.text
    user_id = message.from_user.id
    await add_item_to_list(user_id, header, item)
    await message.answer(
        "Элемент успешно добавлен!",
        reply_markup=select_action_type_keyboard()
    )
    await state.clear()
    await state.set_state(FormList.action)

def transform_lists_to_dict(lists: List[Tuple[int, str, str]]) -> Dict[str, List[str]]:
    result_dict = {}
    for record in lists:
        _, header, item = record
        if header not in result_dict:
            result_dict[header] = []
        result_dict[header].append(item)
    
    return result_dict

def format_list_items_message(lists_dict: Dict[str, List[str]]) -> str:
    response_message = ""
    
    for header, items in lists_dict.items():
        response_message += f"{header}:\n"
        
        for item in items:
            response_message += f" - {item}\n"
        
        response_message += "\n"  # Разделение категорий
    
    return response_message