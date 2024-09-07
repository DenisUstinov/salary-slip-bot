import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

ENV = "LOCAL" #PROD

ALLOWED_UPDATES = [
    'message',
    'edited_message',
    'callback_query'
]
ADMIN_ID_LIST = [
    512647405
    ]

CHAT_TYPE_LIST = [
    'private'
]

BASE_DIR = 'databases'