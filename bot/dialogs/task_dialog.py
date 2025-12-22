from aiogram.filters.state import StatesGroup, State
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Button, Group, Back, Cancel, Row, Select
from aiogram_dialog.widgets.text import Const, Format, List
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput
from aiogram.types import Message, CallbackQuery
from datetime import datetime
from typing import Any
import logging

from services.api_client import APIClient

logger = logging.getLogger(__name__)


class TaskDialog(StatesGroup):
    main = State()
    view_tasks = State()
    add_task_title = State()
    add_task_description = State()
    add_task_due_date = State()
    add_task_categories = State()
    task_details = State()


async def get_tasks_data(dialog_manager: DialogManager, **kwargs):
    user_id = dialog_manager.event.from_user.id
    api_url = dialog_manager.middleware_data.get('api_url', 'http://backend:8000/api')

    async with APIClient(api_url) as client:
        tasks = await client.get_tasks(user_id)

    return {
        'tasks': tasks[:10],  # Ограничиваем 10 задачами
        'tasks_count': len(tasks),
        'user_id': user_id
    }


async def get_categories_data(dialog_manager: DialogManager, **kwargs):
    api_url = dialog_manager.middleware_data.get('api_url', 'http://backend:8000/api')

    async with APIClient(api_url) as client:
        categories = await client.get_categories()

    return {
        'categories': categories,
        'categories_count': len(categories)
    }


async def on_task_selected(callback: CallbackQuery, widget: Any,
                           dialog_manager: DialogManager, item_id: str):
    dialog_manager.dialog_data['selected_task_id'] = item_id
    await dialog_manager.switch_to(TaskDialog.task_details)


async def on_add_task_click(callback: CallbackQuery, button: Button,
                            dialog_manager: DialogManager):
    await dialog_manager.switch_to(TaskDialog.add_task_title)


async def on_title_entered(message: Message, widget: ManagedTextInput,
                           dialog_manager: DialogManager, text: str):
    if len(text) < 2:
        await message.answer("Заголовок должен содержать минимум 2 символа")
        return
    dialog_manager.dialog_data['title'] = text
    await dialog_manager.switch_to(TaskDialog.add_task_description)


async def on_description_entered(message: Message, widget: ManagedTextInput,
                                 dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data['description'] = text
    await dialog_manager.switch_to(TaskDialog.add_task_due_date)


async def on_due_date_entered(message: Message, widget: ManagedTextInput,
                              dialog_manager: DialogManager, text: str):
    try:
        due_date = datetime.strptime(text, "%Y-%m-%d %H:%M")
        dialog_manager.dialog_data['due_date'] = due_date.isoformat()
    except ValueError:
        try:
            due_date = datetime.strptime(text, "%Y-%m-%d")
            dialog_manager.dialog_data['due_date'] = due_date.isoformat()
        except ValueError:
            await message.answer("Неверный формат даты. Используйте ГГГГ-ММ-ДД или ГГГГ-ММ-ДД ЧЧ:ММ")
            return

    user_id = message.from_user.id
    api_url = dialog_manager.middleware_data.get('api_url', 'http://backend:8000/api')

    task_data = {
        "title": dialog_manager.dialog_data['title'],
        "description": dialog_manager.dialog_data.get('description', ''),
        "due_date": dialog_manager.dialog_data.get('due_date'),
        "telegram_user_id": user_id,
    }

    async with APIClient(api_url) as client:
        result = await client.create_task(task_data)

    if result:
        await message.answer(f"✅ Задача '{task_data['title']}' успешно добавлена!")
    else:
        await message.answer("❌ Ошибка при добавлении задачи. Попробуйте позже.")

    await dialog_manager.done()


# Windows
main_window = Window(
    Const("📋 *Главное меню*\n\nВыберите действие:"),
    Group(
        Button(Const("📝 Мои задачи"), id="view_tasks", on_click=lambda c, b, d: d.switch_to(TaskDialog.view_tasks)),
        Button(Const("➕ Добавить задачу"), id="add_task", on_click=on_add_task_click),
        Button(Const("⏰ Просроченные"), id="overdue_tasks"),
        Cancel(Const("❌ Закрыть")),
    ),
    state=TaskDialog.main,
    parse_mode="Markdown"
)

view_tasks_window = Window(
    Format("📋 *Ваши задачи* (всего: {tasks_count}):\n"),
    List(
        field=Format("{pos}. {item[title]}"),
        items="tasks",
    ),
    Group(
        Button(Const("🔙 Назад"), id="back", on_click=lambda c, b, d: d.switch_to(TaskDialog.main)),
    ),
    state=TaskDialog.view_tasks,
    getter=get_tasks_data,
    parse_mode="Markdown"
)

title_window = Window(
    Const("✏️ Введите заголовок задачи:"),
    TextInput(
        id="title_input",
        on_success=on_title_entered,
    ),
    Group(
        Back(Const("🔙 Назад")),
    ),
    state=TaskDialog.add_task_title,
)

description_window = Window(
    Const("📝 Введите описание задачи (можно пропустить, нажав 'Пропустить'):"),
    TextInput(
        id="description_input",
        on_success=on_description_entered,
    ),
    Group(
        Button(Const("⏭️ Пропустить"), id="skip", on_click=lambda c, b, d: d.switch_to(TaskDialog.add_task_due_date)),
        Back(Const("🔙 Назад")),
    ),
    state=TaskDialog.add_task_description,
)

due_date_window = Window(
    Const("📅 Введите дату и время выполнения (формат: ГГГГ-ММ-ДД или ГГГГ-ММ-ДД ЧЧ:ММ):\n"
          "Пример: 2024-12-31 или 2024-12-31 18:30"),
    TextInput(
        id="due_date_input",
        on_success=on_due_date_entered,
    ),
    Group(
        Button(Const("⏭️ Без срока"), id="no_date", on_click=lambda c, b, d: d.done()),
        Back(Const("🔙 Назад")),
    ),
    state=TaskDialog.add_task_due_date,
)

task_dialog = Dialog(
    main_window,
    view_tasks_window,
    title_window,
    description_window,
    due_date_window,
)