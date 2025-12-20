import os
from dotenv import load_dotenv
# переменные из файла .env
load_dotenv()

# здесь токен
BOT_TOKEN = os.getenv('BOT_TOKEN')
# URL Django API
API_URL = "http://localhost:8000/api"


# Проверяем, что токен загружен
if not BOT_TOKEN:
    raise ValueError("❌ Не найден BOT_TOKEN в переменных окружения!")
