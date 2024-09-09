from salary_slip_bot.database.sqlite import get_db_connection

async def add_expense_entry(user_id: int, expense_type: str, amount: int) -> None:
    async with get_db_connection(user_id) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute('''
                INSERT INTO expenses (type, payment) VALUES (?, ?)
            ''', (expense_type, amount))
            await conn.commit()

async def get_expenses_within_period(user_id: int, start: int, stop: int, expense_type: str = None):
    async with get_db_connection(user_id) as conn:
        async with conn.cursor() as cursor:
            query = '''
                SELECT id, type, payment, date
                FROM expenses
                WHERE date BETWEEN ? AND ?
            '''
            params = [start, stop]

            if expense_type:
                query += ' AND type = ?'
                params.append(expense_type)
            
            await cursor.execute(query, params)
            expenses = await cursor.fetchall()
            return expenses

async def delete_expense_entry(user_id: int, expense_id: int) -> bool:
    async with get_db_connection(user_id) as conn:
        async with conn.cursor() as cursor:
            try:
                await cursor.execute('''
                    DELETE FROM expenses WHERE id = ?
                ''', (expense_id,))
                await conn.commit()
                return cursor.rowcount == 1
            except Exception as e:
                print(f"Ошибка при удалении записи расхода: {str(e)}")
                return False