from recipes.models import Recipes
from rest_framework import serializers

from .models import CustomUser, Follow


class ListDetailUserSerializer(serializers.ModelSerializer):
    """Сериализатор модели Юзер GET запрос."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed"
        )

    def get_is_subscribed(self, obj):
        """Проверка на наличие подписок"""
        user = self.context.get("request").user
        return user.is_authenticated and Follow.objects.filter(
            user=user, author=obj.id).exists()


class SupportRecipesSerializer(serializers.ModelSerializer):
    """Сериализатор рецепта для добавления в Избранное"""

    class Meta:
        model = Recipes
        fields = ("id", "name", "image", "cooking_time")


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор Подписок"""
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CustomUser
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count"
        )

    def get_is_subscribed(self, obj):
        """Проверка на наличие подписок"""
        user = self.context.get("request").user
        return user.is_authenticated and Follow.objects.filter(
            user=user, author=obj.id).exists()

    def get_recipes(self, obj):
        """Рецепты автора"""
        recipes = obj.recipes.all()
        return SupportRecipesSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        """Кол-во рецептов"""
        author = obj.id
        queryset = Recipes.objects.filter(author=author).count()
        return queryset
