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