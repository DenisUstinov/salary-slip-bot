from dotenv import load_dotenv
import os

# Загрузка переменных из файла .env
load_dotenv()

# Получение переменных окружения
token = os.getenv("TOKEN")