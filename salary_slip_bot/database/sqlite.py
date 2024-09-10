import aiosqlite
import os
from contextlib import asynccontextmanager

from salary_slip_bot.config import BASE_DIR

# Создаем папку, если она еще не существует
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

# Функция для получения пути к базе данных пользователя
def get_db_path(user_id: int) -> str:
    return os.path.join(BASE_DIR, f'{user_id}.db')

# Контекстный менеджер для подключения к базе данных пользователя
@asynccontextmanager
async def get_db_connection(user_id: int):
    db_path = get_db_path(user_id)
    async with aiosqlite.connect(db_path) as connection:
        yield connection

# Инициализация базы данных для нового пользователя
async def init_db(user_id: int):
    db_path = get_db_path(user_id)
    async with aiosqlite.connect(db_path) as conn:
        async with conn.cursor() as cursor:
            # Создание таблицы для записей о работе
            await cursor.execute('''
                CREATE TABLE IF NOT EXISTS works (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL,
                    duration INTEGER NOT NULL,
                    date INTEGER DEFAULT (strftime('%s', 'now'))
                )
            ''')

            # Создание таблицы для настроек
            await cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pricing_hour_shift INTEGER NOT NULL,
                    pricing_hour_repairing INTEGER NOT NULL,
                    pricing_hour_moonlighting INTEGER NOT NULL,
                    meal_compensation INTEGER NOT NULL
                )
            ''')

            # Создание таблицы для расходов
            await cursor.execute('''
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL,
                    payment INTEGER NOT NULL,
                    date INTEGER DEFAULT (strftime('%s', 'now'))
                )
            ''')

            # Создание таблицы для списка с иерархией
            await cursor.execute('''
                CREATE TABLE IF NOT EXISTS lists (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    header TEXT NOT NULL,
                    item TEXT NOT NULL,
                    UNIQUE(header, item)
                )
            ''')

            # Инициализация таблицы настроек, если они еще не заданы
            await cursor.execute('''
                INSERT OR IGNORE INTO settings (id, pricing_hour_shift, pricing_hour_repairing, pricing_hour_moonlighting, meal_compensation)
                VALUES (1, ?, ?, ?, ?)
            ''', (1, 1, 1, 1))

        # Подтверждение изменений
        await conn.commit()