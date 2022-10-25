from djoser.serializers import UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import Recipes

from .models import CustomUser, Follow


class CurrentUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if obj == request.user or request.user.is_anonymous:
            return False
        return Follow.objects.filter(user=request.user, author=obj.id).exists()


class SupportRecipesSerializer(serializers.ModelSerializer):
    """Вспомогательный сериализатор для добавления рецептов"""

    class Meta:
        model = Recipes
        fields = ("id", "name", "image", "cooking_time")


class SubscribeListSerializer(serializers.ModelSerializer):
    """Сериализатор Избранного"""
    # is_subscribed = serializers.SerializerMethodField()
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
        read_only_fields = ("recipes", "recipes_count")

    def __check_user_authorized(self, obj):
        request = self.context.get('request')
        return request and request.user.is_authenticated

    # def get_is_subscribed(self, obj):
    #     request = self.context.get('request')
    #     if self.__check_user_authorized(obj) is True:
    #         return Follow.objects.filter(
    #             user=request.user, author=obj).exists()
    #     return False

    def get_recipes(self, obj):
        recipes = obj.recipes.all()
        return SupportRecipesSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        recipes = Recipes.objects.filter(author=obj.id)
        return recipes.count()


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор подписчиков"""

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
