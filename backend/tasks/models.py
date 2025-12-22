import hashlib
import time
from django.db import models


class Category(models.Model):  # Категория
    id = models.CharField(primary_key=True, max_length=16, editable=False)
    name = models.CharField(max_length=100, unique=True, verbose_name="Название категории")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def save(self, *args, **kwargs):
        if not self.id:
            raw_id = f"category_{self.name}_{time.time_ns()}_{time.perf_counter_ns()}"
            self.id = hashlib.sha256(raw_id.encode()).hexdigest()[:16]
            # хэш-функция вместо random(перевод цифр в буквы)
            # Итог: Строка, не число, не UUID
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['name']


class Task(models.Model):  # название задачи и ее свойства
    # 20 символов вместо 16 — задачи будут создаваться чаще
    id = models.CharField(primary_key=True, max_length=20, editable=False)
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    description = models.TextField(blank=True, verbose_name="Описание")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    due_date = models.DateTimeField(null=True, blank=True, verbose_name="Дата выполнения")
    completed = models.BooleanField(default=False, verbose_name="Выполнена")
    telegram_user_id = models.BigIntegerField(db_index=True, verbose_name="ID пользователя Telegram")
    categories = models.ManyToManyField(Category, blank=True, verbose_name="Категории")

    def save(self, *args, **kwargs):
        if not self.id:
            raw_id = f"task_{self.telegram_user_id}_{time.time_ns()}_{self.title}_{time.perf_counter_ns()}"
            self.id = hashlib.sha256(raw_id.encode()).hexdigest()[:20]
        super().save(*args, **kwargs)

    def __str__(self):
        status = "✓" if self.completed else "✗"
        return f"{status} {self.title}"

    # для красоты
    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['telegram_user_id', 'completed']),
            models.Index(fields=['due_date', 'completed']),
        ]