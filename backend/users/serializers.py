from recipes.models import Recipes
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

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
        user = self.context.get("request").user
        if obj == user or user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj).exists()


class SupportRecipesSerializer(serializers.ModelSerializer):
    """Сериализатор рецепта для добавления в Избранное"""

    class Meta:
        model = Recipes
        fields = ("id", "name", "image", "cooking_time")


class SubscribeListSerializer(serializers.ModelSerializer):
    """Сериализатор Подписок"""
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

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

    read_only_fields = ("is_subscribed", "recipes", "recipes_count")

    def __get_checked_user_authorized(self, obj):
        request = self.context.get('request')
        return request and request.user.is_authenticated

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if self.__get_checked_user_authorized(obj) is True:
            return Follow.objects.filter(
                user=request.user, author=obj).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        if self.__get_checked_user_authorized(obj) is True:
            context = {'request': request}
            recipes_limit = request.query_params.get('recipes_limit')
            recipes = obj.recipes.all()
            if recipes_limit is not None:
                recipes = recipes[:int(recipes_limit)]
            return SupportRecipesSerializer(
                recipes, many=True, context=context).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class SubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ('user', 'author')
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'author'),
                message='Вы уже подписаны на этого автора!'
            )
        ]

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return SubscribeListSerializer(
            instance.author, context=context).data
