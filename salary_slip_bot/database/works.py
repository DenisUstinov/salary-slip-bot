from salary_slip_bot.database.sqlite import get_db_connection

async def add_work_entry(user_id: int, work_type: str, duration: int) -> None:
    async with get_db_connection(user_id) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute('''
                INSERT INTO works (type, duration) VALUES (?, ?)
            ''', (work_type, duration))
            await conn.commit()

async def get_works_within_period(user_id: int, start: int, stop: int):
    async with get_db_connection(user_id) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute('''
                SELECT id, type, duration, date 
                FROM works 
                WHERE date BETWEEN ? AND ?
            ''', (start, stop))
            works = await cursor.fetchall()
            return works

async def delete_work_entry(user_id: int, work_id: int) -> bool:
    async with get_db_connection(user_id) as conn:
        async with conn.cursor() as cursor:
            try:
                await cursor.execute('''
                    DELETE FROM works WHERE id = ?
                ''', (work_id,))
                await conn.commit()
                return cursor.rowcount == 1  # Возвращает True, если была удалена одна запись
            except Exception as e:
                print(f"Ошибка при удалении записи работы: {str(e)}")
                return False