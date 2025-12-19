from celery import shared_task
from django.utils import timezone
from .models import Task

# Проверяет просроченные задачи и отправляет уведомления.
@shared_task
def check_overdue_tasks():
    now = timezone.now()  # текущее время с учетом Часового пояса
    # overdue_tasks = задачи которые наступили или прошли
    overdue_tasks = Task.objects.filter(due_date__lte=now, due_date__isnull=False)

    # проходим по всем задачам
    for task in overdue_tasks:
        # И выводим в консоль все задачи по одной
        # для настройки(потом в телегу после настройки)
        print(f'Просрочена задача "{task.title}"')
        print(f'    User ID {task.user_id}, Due: {task.due_date}')
        # далее логика для телеги
    # отчет о количестве найденных задач
    return f'Found {overdue_tasks.count()} Overdue tasks'


# @shared_task
# def check_overdue_tasks():
#     """Упрощённая версия для теста"""
#     print("✅ Задача Celery запущена!")
#     return "Успешное выполнение задачи"
