import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

ENV = "LOCAL" # PROD LOCAL

ALLOWED_UPDATES = [
    'message',
    'edited_message',
    'callback_query'
]

USER_ID_LIST = [
    512647405,
    1745922009
    ]

ADMIN_ID_LIST = [
    512647405,
    ]

CHAT_TYPE_LIST = [
    'private'
]

BASE_DIR = 'databases'