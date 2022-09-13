from django.utils import timezone
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from recipes.models import (AmountIngredients, Favorite, Ingredients, Recipes,
                            ShoppingList, Tags, TagsRecipes)
from users.serializers import ListDetailUserSerializer


class TagsSerializer(serializers.ModelSerializer):
    """Сериализатор модели Теги"""

    class Meta:
        fields = "__all__"
        model = Tags


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор модели Избранные_рецепты"""

    class Meta:
        fields = "__all__"
        model = Favorite


class ShoppingListSerializer(serializers.ModelSerializer):
    """Сериализатор модели Список_покупок"""

    class Meta:
        fields = "__all__"
        model = ShoppingList


class IngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор модели Ингредиенты"""

    class Meta:
        model = Ingredients
        fields = ("id", "name", "measurement_unit")


class AllIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="ingredients.id")
    name = serializers.ReadOnlyField(source="ingredients.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredients.measurement_unit"
    )

    class Meta:
        model = AmountIngredients
        fields = ("id", "name", "measurement_unit", "amount")


class AmountRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор модели Ингредиенты_Рецепта"""
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

    def checked_queryset(self, obj, Model):
        user_id = self.context.get("request").user.id
        return Model.objects.filter(
            user=user_id,
            recipe=obj.id
        ).exists()

    tags = TagsSerializer(many=True)
    author = ListDetailUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField(read_only=True)
    is_favorited = checked_queryset(obj, Favorite)
    is_in_shopping_cart = checked_queryset(obj, ShoppingList)
    published = serializers.HiddenField(default=timezone.now)

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

    # def get_is_favorited(self, obj):
    #     """Рецепт в избранном"""
    #     user_id = self.context.get("request").user.id
    #     return Favorite.objects.filter(
    #         user=user_id,
    #         recipe=obj.id
    #     ).exists()
    #
    # def get_is_in_shopping_cart(self, obj):
    #     """Ингредиенты_Рецепта в корзине"""
    #     user_id = self.context.get("request").user.id
    #     return ShoppingList.objects.filter(
    #         user=user_id,
    #         recipe=obj.id
    #     ).exists()

    @staticmethod
    def get_ingredients(obj):
        queryset = AmountIngredients.objects.filter(recipe=obj)
        return AllIngredientsSerializer(queryset, many=True).data

    def to_representation(self, obj):
        data = super().to_representation(obj)
        data["image"] = obj.image.url
        return data


class CreateRecipesSerializer(serializers.ModelSerializer):
    """Создание/обновление/удаление Сериализатор Рецептов"""
    author = ListDetailUserSerializer(read_only=True)
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
            "id",
            "author",
            "ingredients",
            "tags",
            "image",
            "name",
            "text",
            "cooking_time",
            "published"
        )

    def validate(self, data):
        ingredients = data["ingredients"]
        ingredients_list = []
        for ingredient in ingredients:
            if ingredient["id"] in ingredients_list:
                raise serializers.ValidationError(
                    {"ingredients": "Ингредиенты в рецепте уникальны!"}
                )
                ingredients_list.append(ingredient["id"])
            if ingredient["amount"] <= 0:
                raise ValidationError({
                    "ingredients": "Необходимо добавить ингредиенты!"
                })
        tags = data["tags"]
        if not tags:
            raise ValidationError({
                "tags": "Необходимо добавить тег!"
            })
        tags_list = []
        for tag in tags:
            if tag in tags_list:
                raise ValidationError({
                    "tags": "Теги для рецепта уникальны!"
                })
            tags_list.append(tag)
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
