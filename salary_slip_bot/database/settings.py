from salary_slip_bot.database.sqlite import get_db_connection

async def get_settings(user_id: int):
    async with get_db_connection(user_id) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute('''
                SELECT * FROM settings WHERE id = 1
            ''')
            result = await cursor.fetchone()
            return result if result else None

async def update_pricing(user_id: int, pricing_type: str, hour_price: int) -> None:
    column_map = {
        "Смена": "pricing_hour_shift",
        "Подработка": "pricing_hour_moonlighting",
        "Ремонт": "pricing_hour_repairing",
    }
    column = column_map.get(pricing_type)

    if column:
        async with get_db_connection(user_id) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(f'''
                    UPDATE settings
                    SET {column} = ?
                    WHERE id = 1
                ''', (hour_price,))
                await conn.commit()

async def update_meal_compensation(user_id: int, meal_compensation: int) -> None:
    async with get_db_connection(user_id) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute('''
                UPDATE settings
                SET meal_compensation = ?
                WHERE id = 1
            ''', (meal_compensation,))
            await conn.commit()