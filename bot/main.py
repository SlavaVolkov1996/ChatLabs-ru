import asyncio
import logging
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command

from config import BOT_TOKEN
from services.api_client import APIClient

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Создаем объекты
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
api_client = APIClient()


# ---------- Обработчики команд ----------

@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Приветственное сообщение"""
    welcome_text = (
        "👋 Привет! Я бот для управления задачами.\n\n"
        "📋 Доступные команды:\n"
        "/start - приветствие\n"
        "/tasks - показать мои задачи\n"
        "/add - добавить задачу\n"
        "/help - помощь\n\n"
        "🆔 Ваш ID: {user_id}"
    ).format(user_id=message.from_user.id)

    await message.answer(welcome_text)


@dp.message(Command("help"))
async def cmd_help(message: Message):
    """Помощь по командам"""
    help_text = (
        "📚 Помощь по командам:\n\n"
        "/start - приветственное сообщение\n"
        "/tasks - показать все ваши задачи\n"
        "/add - добавить новую задачу\n"
        "/help - эта справка\n\n"
        "💡 Бот сохраняет задачи в системе и напомнит о них!"
    )
    await message.answer(help_text)


@dp.message(Command("tasks"))
async def cmd_tasks(message: Message):
    """Показать задачи пользователя"""
    user_id = message.from_user.id

    # Показываем "типинг" (бот печатает) - ИСПРАВЛЕННАЯ СТРОКА
    await bot.send_chat_action(message.chat.id, "typing")

    # Получаем задачи через API
    tasks = await api_client.get_tasks(user_id)

    if not tasks:
        await message.answer("📭 У вас пока нет задач.\nИспользуйте /add чтобы создать первую.")
        return

    # Формируем сообщение с задачами
    response = "📋 Ваши задачи:\n\n"

    for i, task in enumerate(tasks, 1):
        # Форматируем дату создания
        created_at = task['created_at']
        try:
            # Парсим дату из формата Django
            dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            formatted_date = dt.strftime("%d.%m.%Y %H:%M")
        except:
            formatted_date = created_at

        # Форматируем дату выполнения (если есть)
        due_date_str = ""
        if task.get('due_date'):
            try:
                due_dt = datetime.fromisoformat(task['due_date'].replace('Z', '+00:00'))
                due_date_str = f"📅 Срок: {due_dt.strftime('%d.%m.%Y')}"
            except:
                due_date_str = f"📅 Срок: {task['due_date']}"

        # Получаем категории
        categories = ""
        if task.get('categories'):
            cat_names = [cat['name'] for cat in task['categories']]
            categories = f"🏷️ Категории: {', '.join(cat_names)}"

        # Добавляем задачу в ответ
        response += f"{i}. {task['title']}\n"
        response += f"   📝 {task.get('description') or 'без описания'}\n"
        response += f"   📅 Создано: {formatted_date}\n"
        if due_date_str:
            response += f"   {due_date_str}\n"
        if categories:
            response += f"   {categories}\n"
        response += "\n"

    # Добавляем статистику
    response += f"📊 Всего задач: {len(tasks)}"

    # Telegram ограничивает сообщения 4096 символами
    if len(response) > 4000:
        response = response[:4000] + "\n\n... (сообщение сокращено)"

    await message.answer(response)


@dp.message(Command("add"))
async def cmd_add(message: Message):
    """Начать добавление задачи"""
    await message.answer(
        "➕ Чтобы добавить задачу, введите её в формате:\n\n"
        "Название\n"
        "Описание (необязательно)\n\n"
        "📅 Чтобы добавить срок, добавьте третьей строкой дату в формате ДД.ММ.ГГГГ\n\n"
        "Пример:\n"
        "Купить хлеб\n"
        "В магазине у дома\n"
        "20.12.2024"
    )


# ---------- Обработка обычных сообщений ----------

@dp.message()
async def handle_text(message: Message):
    """Обработка обычных сообщений"""
    text = message.text.strip()

    # Если сообщение многострочное — возможно, это задача
    if '\n' in text:
        lines = text.split('\n')
        if 1 <= len(lines) <= 3:
            # Создаем задачу
            await create_task_from_text(message, lines)
            return

    # Иначе — неизвестная команда
    await message.answer(
        "🤔 Не понял команду. Используйте:\n"
        "/start, /help, /tasks, /add"
    )


async def create_task_from_text(message: Message, lines: list):
    """Создать задачу из текста"""
    title = lines[0].strip()
    description = lines[1].strip() if len(lines) > 1 else ""
    due_date_str = lines[2].strip() if len(lines) > 2 else None

    # Подготавливаем данные для API
    task_data = {
        "title": title,
        "description": description,
        "user_id": message.from_user.id,
    }

    # Парсим дату, если есть
    if due_date_str:
        try:
            from datetime import datetime
            due_date = datetime.strptime(due_date_str, "%d.%m.%Y")
            # Конвертируем в ISO формат
            task_data["due_date"] = due_date.isoformat()
        except ValueError:
            await message.answer("❌ Неверный формат даты. Используйте ДД.ММ.ГГГГ")
            return

    # Отправляем задачу в API
    success = await api_client.create_task(task_data)

    if success:
        await message.answer(f"✅ Задача '{title}' успешно добавлена!")
        if due_date_str:
            await message.answer(f"📅 Срок выполнения: {due_date_str}")
    else:
        await message.answer("❌ Ошибка при сохранении задачи. Попробуйте позже.")


# ---------- Запуск бота ----------

async def main():
    logging.info("🚀 Бот запускается...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())