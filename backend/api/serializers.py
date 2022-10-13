from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


from recipes.models import (AmountIngredients, Favorite, Ingredients, Recipes,
                            ShoppingList, Tags, TagsRecipes)
from users.serializers import CurrentUserSerializer


class TagsSerializer(serializers.ModelSerializer):
    """Сериализатор модели Теги"""

    class Meta:
        fields = "__all__"
        model = Tags


class IngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиенты"""

    class Meta:
        model = Ingredients
        fields = ("id", "name", "measurement_unit")


class AllIngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиенты в рецепте"""
    id = serializers.ReadOnlyField(source="ingredients.id")
    name = serializers.ReadOnlyField(source="ingredients.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredients.measurement_unit"
    )

    class Meta:
        model = AmountIngredients
        fields = ("id", "name", "measurement_unit", "amount")


class AmountRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиенты для создания рецепта"""
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredients.objects.all())

    class Meta:
        model = AmountIngredients
        fields = ("id", "amount")


class SupportRecipesSerializer(serializers.ModelSerializer):
    """Сериализатор рецепта для добавления в Избранное"""

    class Meta:
        model = Recipes
        fields = ("id", "name", "image", "cooking_time")


class GetRecipesSerializer(serializers.ModelSerializer):
    """GET Сериализатор Рецептов"""
    tags = TagsSerializer(many=True)
    author = CurrentUserSerializer()
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipes
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
            "published"
        )
        ordering = ("-published",)
        read_only_fields = ("author", "ingredients", "is_favorited", "is_in_shopping_cart",)

    @staticmethod
    def get_ingredients(obj):
        queryset = AmountIngredients.objects.filter(recipe=obj)
        return AllIngredientsSerializer(queryset, many=True).data

    def __checked_queryset(self, obj, model):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        queryset = model.objects.filter(
            user=request.user.id, recipe=obj.id).exists()
        return queryset

    def get_is_favorited(self, obj):
        return self.__checked_queryset(obj=obj, model=Favorite)

    def get_is_in_shopping_cart(self, obj):
        return self.__checked_queryset(obj=obj, model=ShoppingList)


class CreateRecipesSerializer(serializers.ModelSerializer):
    """Создание/обновление/удаление Сериализатор Рецептов"""
    # author = CurrentUserSerializer()
    ingredients = AmountRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tags.objects.all(),
        many=True
    )
    image = Base64ImageField()
    published = serializers.HiddenField(default=timezone.now)

    class Meta:
        model = Recipes
        fields = (
            "author",
            "ingredients",
            "tags",
            "image",
            "name",
            "text",
            "cooking_time",
            "published"
        )
        read_only_fields = ("author",)

    def validate(self, data):
        ingredients_d = data['ingredients']
        ingredients_set = set()
        for ingredient in ingredients_d:
            if ingredient['amount'] <= 0:
                raise serializers.ValidationError(
                    'Вес ингредиента должен быть больше 0'
                )
            if ingredient['id'] in ingredients_set:
                raise serializers.ValidationError(
                    'Ингредиент в рецепте не должен повторяться.'
                )
            ingredients_set.add(ingredient['id'])
        tags_d = data["tags"]
        tags_set = set()
        for tag in tags_d:
            if not tag:
                raise ValidationError({
                    "tags": "Необходимо добавить тег!"
                })
            if tag in tags_set:
                raise ValidationError({
                    "tags": "Теги для рецепта уникальны!"
                })
            tags_set.add(tag)
        return data

    @staticmethod
    def add_ingredients_tags(ingredients, recipe, tags):
        for ingredient in ingredients:
            AmountIngredients.objects.update_or_create(
                recipe=recipe,
                ingredients=ingredient["id"],
                amount=ingredient["amount"]
            )
        for tag in tags:
            recipe.tags.add(tag)

    def create(self, validated_data):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        recipe = Recipes.objects.create(**validated_data)
        self.add_ingredients_tags(ingredients, recipe, tags)
        return recipe

    def update(self, recipe, validated_data):
        AmountIngredients.objects.filter(recipe=recipe).delete()
        TagsRecipes.objects.filter(recipe=recipe).delete()
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        self.add_ingredients_tags(ingredients, recipe, tags)
        return super().update(recipe, validated_data)

    def to_representation(self, instance):
        request = self.context.get("request")
        context = {"request": request}
        return GetRecipesSerializer(instance, context=context).data
