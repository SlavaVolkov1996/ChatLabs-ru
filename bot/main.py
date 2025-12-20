import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from config import BOT_TOKEN

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# объекты бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("👋 Привет! Я бот для управления задачами.\n"
                        "Команды:\n"
                        "/start - приветствие\n"
                        "/tasks - мои задачи")

# Обработчик команды /help
@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer("Помощь:\n"
                        "/start - приветствие\n"
                        "/tasks - показать задачи\n"
                        "/add - добавить задачу")

# Функция запуска бота
async def main():
    logging.info("🚀 Бот запускается...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())