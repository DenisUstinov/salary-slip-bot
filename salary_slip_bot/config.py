import os
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

# Токен бота
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Окружение (LOCAL или PROD)
ENV = os.getenv("ENV", "LOCAL")

# Вебхуки
SELF_SSL = os.getenv("SELF_SSL", "False").lower() == "true"
DOMAIN = os.getenv("DOMAIN_IP") if SELF_SSL else os.getenv("DOMAIN_NAME")
WEBHOOK_PATH = "/" + os.getenv("PROJECT_NAME")
EXTERNAL_PORT = int(os.getenv("EXTERNAL_PORT", 8443))
BASE_WEBHOOK_URL = f"https://{DOMAIN}:{EXTERNAL_PORT}" if SELF_SSL else f"https://{DOMAIN}"
WEB_SERVER_HOST = "127.0.0.1" if not SELF_SSL else DOMAIN
WEB_SERVER_PORT = 8080 if not SELF_SSL else EXTERNAL_PORT
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "my-secret")

# SSL-сертификаты для работы с вебхуками (если используется самоподписанный сертификат)
WEBHOOK_SSL_CERT = os.getenv("WEBHOOK_SSL_CERT", "../SSL/yourdomain.self.crt")
WEBHOOK_SSL_PRIV = os.getenv("WEBHOOK_SSL_PRIV", "../SSL/yourdomain.self.key")

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