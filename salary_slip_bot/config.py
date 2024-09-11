import os
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

# Токен бота
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_PATH = "/" + os.getenv("PROJECT_NAME")
DOMAIN = os.getenv("DOMAIN_IP")
EXTERNAL_PORT = 8443
BASE_WEBHOOK_URL = "https://" + DOMAIN + ":" + str(EXTERNAL_PORT)
WEB_SERVER_HOST = "127.0.0.1"
WEB_SERVER_PORT = 8080
WEBHOOK_SECRET = "my-secret"

# Окружение (LOCAL или PROD)
ENV = os.getenv("ENV", "PROD")

# Настройки обновлений
ALLOWED_UPDATES = [
    'message',
    'edited_message',
    'callback_query'
]

# Список разрешенных ID пользователей
USER_ID_LIST = [
    512647405,
    1745922009
]

# Список админов
ADMIN_ID_LIST = [
    512647405,
]

# Типы чатов
CHAT_TYPE_LIST = [
    'private'
]

# Базовая директория для хранения данных
BASE_DIR = 'databases'