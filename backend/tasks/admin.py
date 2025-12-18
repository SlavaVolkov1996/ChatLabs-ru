from django.contrib import admin
# админка для управления данными(суперпользователь)
# Register your models here.

from .models import Task, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')
    search_fields = ('name',)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user_id', 'created_at', 'due_date')
    list_filter = ('categories', 'created_at')
    search_fields = ('title', 'description')
    filter_horizontal = ('categories',)
