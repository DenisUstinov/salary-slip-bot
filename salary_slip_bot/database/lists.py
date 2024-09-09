from salary_slip_bot.database.sqlite import get_db_connection

async def get_all_lists(user_id: int):
    async with get_db_connection(user_id) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute('SELECT id, item FROM lists')
            rows = await cursor.fetchall()
            return rows