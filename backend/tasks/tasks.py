from celery import shared_task
from django.utils import timezone
from django.conf import settings
import requests
import json
from .models import Task


@shared_task
def check_overdue_tasks():
    now = timezone.now()
    overdue_tasks = Task.objects.filter(
        due_date__lte=now,
        due_date__isnull=False,
        completed=False
    ).select_related()

    result = {
        'total_checked': Task.objects.count(),
        'overdue_count': overdue_tasks.count(),
        'tasks': []
    }

    for task in overdue_tasks:
        task_info = {
            'id': task.id,
            'title': task.title,
            'telegram_user_id': task.telegram_user_id,
            'due_date': task.due_date.isoformat() if task.due_date else None,
            'overdue_by': (now - task.due_date).total_seconds() if task.due_date else 0
        }
        result['tasks'].append(task_info)

        # Логирование в консоль (в production можно заменить на отправку в Telegram)
        print(f"⚠️ Задача '{task.title}' просрочена!")
        print(f"   Пользователь: {task.telegram_user_id}")
        print(f"   Срок был: {task.due_date}")

        # Здесь можно добавить отправку уведомления в Telegram
        # Пример: send_telegram_notification.delay(task.telegram_user_id, task.title)

    print(f"Проверка завершена. Найдено {overdue_tasks.count()} просроченных задач.")
    return result


@shared_task
def send_telegram_notification(user_id, task_title, task_id=None):
    """
    Задача для отправки уведомления в Telegram
    В реальном проекте нужно настроить отправку через Telegram Bot API
    """
    bot_token = getattr(settings, 'BOT_TOKEN', None)

    if not bot_token:
        print(f"⚠️ Не могу отправить уведомление для задачи '{task_title}' - BOT_TOKEN не настроен")
        return False

    message = f"⏰ Задача '{task_title}' просрочена!"

    # Пример отправки через Telegram API
    # try:
    #     response = requests.post(
    #         f"https://api.telegram.org/bot{bot_token}/sendMessage",
    #         json={
    #             'chat_id': user_id,
    #             'text': message,
    #             'parse_mode': 'HTML'
    #         }
    #     )
    #     return response.status_code == 200
    # except Exception as e:
    #     print(f"Ошибка отправки уведомления: {e}")
    #     return False

    print(f"📨 Уведомление для пользователя {user_id}: {message}")
    return True