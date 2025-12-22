import asyncio
import logging
import os
from datetime import datetime
from typing import Optional

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import DialogManager, StartMode, setup_dialogs
from aiogram_dialog.widgets.kbd import Button
from dotenv import load_dotenv

from dialogs.task_dialog import task_dialog, TaskDialog
from services.api_client import APIClient

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv('BOT_TOKEN')
API_URL = os.getenv('API_URL', 'http://backend:8000/api')

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не установлен в переменных окружения")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


async def check_api_health():
    """Проверка доступности API"""
    try:
        async with APIClient(API_URL) as client:
            result = await client._request('GET', 'health/')
            return result is not None
    except Exception as e:
        logger.error(f"Ошибка проверки API: {e}")
        return False


@dp.message(Command("start"))
async def cmd_start(message: Message, dialog_manager: DialogManager):
    await message.answer(
        "👋 *Добро пожаловать в ToDo List бот!*\n\n"
        "Я помогу вам управлять вашими задачами.\n\n"
        "📋 *Доступные команды:*\n"
        "/start - это сообщение\n"
        "/tasks - показать мои задачи\n"
        "/add - добавить задачу\n"
        "/menu - открыть меню\n"
        "/help - помощь\n\n"
        "🆔 Ваш ID: `{user_id}`".format(user_id=message.from_user.id),
        parse_mode="Markdown"
    )

    # Проверяем доступность API
    if not await check_api_health():
        await message.answer("⚠️ *Внимание:* Сервер задач временно недоступен. Попробуйте позже.",
                             parse_mode="Markdown")


@dp.message(Command("menu"))
async def cmd_menu(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(TaskDialog.main, mode=StartMode.RESET_STACK)


@dp.message(Command("tasks"))
async def cmd_tasks(message: Message):
    user_id = message.from_user.id

    async with APIClient(API_URL) as client:
        tasks = await client.get_tasks(user_id)

    if not tasks:
        await message.answer("📭 У вас пока нет задач.\nИспользуйте /add чтобы создать первую.")
        return

    response = "📋 *Ваши задачи:*\n\n"

    for i, task in enumerate(tasks, 1):
        created_at = task.get('created_at', '')
        try:
            dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            formatted_date = dt.strftime("%d.%m.%Y %H:%M")
        except:
            formatted_date = created_at

        status = "✅" if task.get('completed') else "⏳"

        response += f"{i}. {status} *{task['title']}*\n"

        if task.get('description'):
            desc = task['description'][:50] + "..." if len(task['description']) > 50 else task['description']
            response += f"   📝 {desc}\n"

        response += f"   📅 Создано: {formatted_date}\n"

        if task.get('due_date'):
            try:
                due_dt = datetime.fromisoformat(task['due_date'].replace('Z', '+00:00'))
                due_date_str = due_dt.strftime('%d.%m.%Y %H:%M')
                response += f"   ⏰ Срок: {due_date_str}\n"
            except:
                pass

        if task.get('categories'):
            cat_names = [cat['name'] for cat in task['categories']]
            response += f"   🏷️ Категории: {', '.join(cat_names)}\n"

        response += "\n"

    response += f"📊 *Всего задач: {len(tasks)}*"

    if len(response) > 4000:
        response = response[:4000] + "\n\n... (сообщение сокращено)"

    await message.answer(response, parse_mode="Markdown")


@dp.message(Command("add"))
async def cmd_add(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(TaskDialog.add_task_title, mode=StartMode.RESET_STACK)


@dp.message(Command("help"))
async def cmd_help(message: Message):
    help_text = (
        "📚 *Помощь по командам:*\n\n"
        "/start - приветственное сообщение\n"
        "/menu - открыть интерактивное меню\n"
        "/tasks - показать все ваши задачи\n"
        "/add - добавить новую задачу\n"
        "/help - эта справка\n\n"
        "💡 *Советы:*\n"
        "• Вы можете добавлять задачи через меню или командой /add\n"
        "• Задачи можно категоризировать\n"
        "• Бот напомнит о просроченных задачах\n\n"
        "🔄 *Обновления:*\n"
        "Следите за обновлениями бота!"
    )
    await message.answer(help_text, parse_mode="Markdown")


@dp.message(Command("health"))
async def cmd_health(message: Message):
    api_healthy = await check_api_health()
    status = "✅" if api_healthy else "❌"

    response = (
        f"*Состояние системы:*\n\n"
        f"🤖 Бот: {status} Работает\n"
        f"🔗 API: {'✅ Доступен' if api_healthy else '❌ Недоступен'}\n"
        f"🆔 Ваш ID: `{message.from_user.id}`"
    )

    await message.answer(response, parse_mode="Markdown")


@dp.message(F.text)
async def handle_text(message: Message):
    text = message.text.strip()

    if text.lower() in ['меню', 'menu', 'старт', 'start']:
        await cmd_menu(message, DialogManager)
    elif text.lower() in ['задачи', 'tasks']:
        await cmd_tasks(message)
    elif text.lower() in ['помощь', 'help', 'справка']:
        await cmd_help(message)
    else:
        await message.answer(
            "🤔 Не понял команду. Используйте:\n"
            "/start, /menu, /help\n\n"
            "Или напишите 'меню' для открытия меню."
        )


async def on_startup():
    logger.info("Бот запускается...")

    if await check_api_health():
        logger.info("API доступен")
    else:
        logger.warning("API недоступен")


async def on_shutdown():
    logger.info("Бот останавливается...")


async def main():
    logger.info("Запуск бота...")

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # Регистрируем диалоги
    dp.include_router(task_dialog)
    setup_dialogs(dp)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())