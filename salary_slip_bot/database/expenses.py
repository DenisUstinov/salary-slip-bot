from salary_slip_bot.database.sqlite import get_db_connection

async def add_expense_entry(user_id: int, expense_type: str, amount: int) -> None:
    async with get_db_connection(user_id) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute('''
                INSERT INTO expenses (type, payment) VALUES (?, ?)
            ''', (expense_type, amount))
            await conn.commit()

async def get_expenses_within_period(user_id: int, start: int, stop: int, expense_type: str):
    async with get_db_connection(user_id) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute('''
                SELECT id, payment, date 
                FROM expenses 
                WHERE date BETWEEN ? AND ? AND type = ?
            ''', (start, stop, expense_type))
            expenses = await cursor.fetchall()
            return expenses