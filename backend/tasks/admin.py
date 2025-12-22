from django.contrib import admin
from .models import Task, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at', 'task_count')
    search_fields = ('name',)
    list_filter = ('created_at',)
    readonly_fields = ('id', 'created_at')

    def task_count(self, obj):
        return obj.tasks.count()

    task_count.short_description = 'Количество задач'


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'telegram_user_id', 'created_at', 'due_date', 'completed', 'category_list')
    list_filter = ('completed', 'created_at', 'due_date', 'categories')
    search_fields = ('title', 'description', 'telegram_user_id')
    readonly_fields = ('id', 'created_at')
    filter_horizontal = ('categories',)
    date_hierarchy = 'created_at'
    list_per_page = 25

    def category_list(self, obj):
        return ", ".join([cat.name for cat in obj.categories.all()])

    category_list.short_description = 'Категории'

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('categories')