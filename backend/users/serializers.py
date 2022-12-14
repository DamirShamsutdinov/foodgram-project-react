from djoser.serializers import UserSerializer
from rest_framework import serializers

from recipes.models import Recipes

from .models import CustomUser, Follow


class CurrentUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

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
        if not request.user.is_authenticated:
            return False
        return Follow.objects.filter(user=request.user, author=obj).exists()


class SupportRecipesSerializer(serializers.ModelSerializer):
    """Сериализатор рецепта для добавления"""

    class Meta:
        model = Recipes
        fields = ("id", "name", "image", "cooking_time")


class SubscribeListSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    email = serializers.ReadOnlyField(source='author.email')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes(self, obj):
        recipes = Recipes.objects.filter(author=obj.author)
        return SupportRecipesSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        recipes = Recipes.objects.filter(author=obj.author)
        return recipes.count()

    def get_is_subscribed(self, obj):
        return CurrentUserSerializer.get_is_subscribed(self, obj.author)

    # def __check_user_authorized(self, obj):
    #     request = self.context.get('request')
    #     return request and request.user.is_authenticated
    #
    # def get_is_subscribed(self, obj):
    #     request = self.context.get('request')
    #     if self.__check_user_authorized(obj) is True:
    #         return Follow.objects.filter(
    #             user=request.user, author=obj).exists()
    #     return False


class SubscribeSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CustomUser
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed',
                  'recipes', 'recipes_count')

    def get_recipes(self, obj):
        recipes = Recipes.objects.filter(author_id=obj.id)
        serializer = SupportRecipesSerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        recipes = Recipes.objects.filter(author_id=obj.id)
        return recipes.count()

    def get_is_subscribed(self, obj):
        return True
