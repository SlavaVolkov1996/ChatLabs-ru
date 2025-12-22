import os
from celery import Celery
from django.conf import settings

# переменная окружения для наших настроек джанго
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# экземпляр Celery с именем config
app = Celery('config')

# берем настройки из джанго
app.config_from_object('django.conf:settings', namespace='CELERY')

# автоматически находит все файлы tasks.py в приложениях Django
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
