from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Task, Category
from .serializers import TaskSerializer, CategorySerializer


# CRUD благодаря ViewSet
class CategoryViewSet(viewsets.ModelViewSet):
    # объединяем логику для категорий
    queryset = Category.objects.all()  # работаем со всеми категориями.
    serializer_class = CategorySerializer  # используем созданный сериализатор.


class TaskViewSet(viewsets.ModelViewSet):
    # объединяем логику для задач
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    # фильтрация
    filter_backends = [DjangoFilterBackend, filters.SearchFilter,
                       filters.OrderingFilter]  # список классов для фильтрации, поиска и сортировки.
    filterset_fields = ['user_id', 'categories']  # поля фильтрации
    search_fields = ['title', 'description']  # поля текстового поиска
    ordering_fields = ['created_at', 'due_date']  # поля сортировки

    # для аутентификации
    # def get_queryset(self):
    ####     return queryset = super().get_queryset()
    #     user_id = self.request.query_params.get('user_id')
    #     if user_id:
    #         queryset = queryset.filter(user_id=user_id)
    ####     return queryset
