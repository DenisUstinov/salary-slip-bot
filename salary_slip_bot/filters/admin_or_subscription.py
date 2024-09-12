import time
from aiogram.filters import Filter
from aiogram import types

class AdminOrSubscriptionFilter(Filter):
    def __init__(self, admin_ids: list[int], global_settings: dict[str, int]) -> None:
        self.admin_ids = admin_ids
        self.global_settings = global_settings

    async def __call__(self, message: types.Message) -> bool:
        user_id = message.from_user.id

        current_time = int(time.time())
        if user_id in self.admin_ids or (self.global_settings["time_subscription"] > current_time):
            return True
        
        return False