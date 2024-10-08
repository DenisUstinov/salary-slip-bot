from salary_slip_bot.database.sqlite import get_db_connection

async def add_item_to_list(user_id: int, category: str, item: str) -> None:
    async with get_db_connection(user_id) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute('INSERT INTO lists (header, item) VALUES (?, ?)', (category, item))
            await conn.commit()

async def get_all_lists(user_id: int):
    async with get_db_connection(user_id) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute('SELECT id, header, item FROM lists ORDER BY item ASC')
            rows = await cursor.fetchall()
            return rows

async def delete_item_to_list(user_id: int, item_id: int) -> None:
    async with get_db_connection(user_id) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute('DELETE FROM lists WHERE id = ?', (item_id,))
            await conn.commit()