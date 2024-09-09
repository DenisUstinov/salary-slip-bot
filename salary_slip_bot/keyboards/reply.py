from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="Табель"), KeyboardButton(text="Финансы")],
        [KeyboardButton(text="Расчетка"), KeyboardButton(text="Незабыть")],
        [KeyboardButton(text="Настройки")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def select_work_type_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="Смена")],
        [KeyboardButton(text="Подработка")],
        [KeyboardButton(text="Ремонт")],
        [KeyboardButton(text="Отмена")],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def select_pricing_type_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="Смена")],
        [KeyboardButton(text="Подработка")],
        [KeyboardButton(text="Ремонт")],
        [KeyboardButton(text="Питание")],
        [KeyboardButton(text="Назад")],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def select_settings_type_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="Расценки")],
        [KeyboardButton(text="Отмена")],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def select_expense_type_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="Столовая")],
        [KeyboardButton(text="Проезд")],
        [KeyboardButton(text="Медкомиссия")],
        [KeyboardButton(text="Переводы")],
        [KeyboardButton(text="Отмена")],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def select_action_type_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="Добавить"), KeyboardButton(text="Удалить")],
        [KeyboardButton(text="Назад")],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def single_cancel_button_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [[KeyboardButton(text="Отмена")]]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def single_back_button_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [[KeyboardButton(text="Назад")]]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)