from rest_framework import serializers
from .models import Category, Task


class CategorySerializer(serializers.ModelSerializer):
    # для категорий
    class Meta:
        model = Category
        fields = ['id', 'name', 'created_at']


class TaskSerializer(serializers.ModelSerializer):
    # для задач
    categories = CategorySerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'created_at', 'due_date', 'user_id', 'categories']
