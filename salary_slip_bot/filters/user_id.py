from aiogram.filters import Filter
from aiogram import types

class UserIdFilter(Filter):
    def __init__(self, user_ids: list[int]) -> None:
        self.user_ids = user_ids

    async def __call__(self, message: types.Message) -> bool:
        return message.from_user.id in self.user_ids