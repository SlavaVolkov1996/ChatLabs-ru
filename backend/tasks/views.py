from rest_framework import viewsets, filters, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import Task, Category
from .serializers import TaskSerializer, CategorySerializer


# CRUD благодаря ViewSet
class CategoryViewSet(viewsets.ModelViewSet):
    # объединяем логику для категорий
    queryset = Category.objects.all()  # работаем со всеми категориями.
    serializer_class = CategorySerializer  # используем созданный сериализатор.
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.AllowAny]
    # фильтрация
    filter_backends = [DjangoFilterBackend, filters.SearchFilter,
                       filters.OrderingFilter]  # список классов для фильтрации, поиска и сортировки.
    filterset_fields = ['completed', 'categories']  # поля фильтрации
    search_fields = ['title', 'description']  # поля текстового поиска
    ordering_fields = ['created_at', 'due_date', 'completed']  # поля сортировки
    ordering = ['-created_at']

    # для аутентификации
    def get_queryset(self):
        queryset = Task.objects.all()
        telegram_user_id = self.request.query_params.get('telegram_user_id')

        if telegram_user_id:
            try:
                user_id = int(telegram_user_id)
                queryset = queryset.filter(telegram_user_id=user_id)
            except ValueError:
                pass

        return queryset


# Возвращает JSON с новым статусом (упрощаем работу)
@action(detail=True, methods=['post'])
def toggle_complete(self, request, pk=None):
    task = self.get_object()
    task.completed = not task.completed
    task.save()
    return Response({'completed': task.completed})


# получения списка всех просроченных задач
@action(detail=False, methods=['get'])
def overdue(self, request):
    queryset = self.get_queryset().filter(due_date__lt=timezone.now(), completed=False)
    page = self.paginate_queryset(queryset)
    # для красоты
    if page is not None:
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    serializer = self.get_serializer(queryset, many=True)
    return Response(serializer.data)
