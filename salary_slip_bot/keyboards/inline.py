from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def create_inline_keyboard(button_texts, callback_data):
    """
    Создает клавиатуру типа InlineKeyboardMarkup.
    
    :param button_texts: Список текстов кнопок
    :param callback_data: Список данных для callback, которые будут отправлены при нажатии кнопки
    :return: Объект InlineKeyboardMarkup
    """
    # Проверка входных данных
    if not all(isinstance(s, str) for s in button_texts) or not all(isinstance(d, str) for d in callback_data):
        raise ValueError("button_texts и callback_data должны быть списками строк.")
    
    # Создание клавиатуры
    keyboard = []
    for text, data in zip(button_texts, callback_data):
        keyboard.append([InlineKeyboardButton(text=text, callback_data=data)])

    # Создание и возвращение объекта InlineKeyboardMarkup
    return InlineKeyboardMarkup(inline_keyboard=keyboard)