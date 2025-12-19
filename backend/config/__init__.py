# обращаемся с файлу celery и берем из него app
from .celery import app as celery_app

# Чтобы при загрузке Django автоматически инициализировался Celery.
__all__ = ('celery_app',)
