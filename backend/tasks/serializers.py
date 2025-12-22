from rest_framework import serializers
from .models import Task, Category

# для категорий
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'created_at']
        read_only_fields = ['id', 'created_at']

# для задач
class TaskSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    category_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Category.objects.all(),
        source='categories',
        write_only=True,
        required=False
    )

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'created_at',
            'due_date', 'completed', 'telegram_user_id',
            'categories', 'category_ids'
        ]
        read_only_fields = ['id', 'created_at']

    def validate_telegram_user_id(self, value):
        if value <= 0:
            raise serializers.ValidationError("telegram_user_id должен быть положительным числом")
        return value

    def create(self, validated_data):
        categories = validated_data.pop('categories', [])
        task = Task.objects.create(**validated_data)
        if categories:
            task.categories.set(categories)
        return task

    def update(self, instance, validated_data):
        categories = validated_data.pop('categories', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if categories is not None:
            instance.categories.set(categories)
        return instance