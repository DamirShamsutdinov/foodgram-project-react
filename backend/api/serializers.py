from django.shortcuts import get_object_or_404
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
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

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
    author = ListDetailUserSerializer()
    ingredients = serializers.SerializerMethodField()
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
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
        )
        read_only_fields = ("is_favorited", "is_in_shopping_cart",)

    def get_ingredients(self, obj):
        queryset = AmountIngredients.objects.filter(recipe=obj)
        return AllIngredientsSerializer(queryset, many=True).data

    def __checked_queryset(self, obj, model):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        queryset = model.objects.filter(
            user=request.user, recipe=obj.id).exists()
        return queryset

    def get_is_favorited(self, obj):
        return self.__checked_queryset(obj=obj, model=Favorite)

    def get_is_in_shopping_cart(self, obj):
        return self.__checked_queryset(obj=obj, model=ShoppingList)


class CreateRecipesSerializer(serializers.ModelSerializer):
    """Создание/обновление/удаление Сериализатор Рецептов"""
    author = ListDetailUserSerializer()
    ingredients = AmountRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tags.objects.all(),
        many=True
    )

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
        )
        read_only_fields = ('author',)

    def create(self, validated_data):
        tags_d = validated_data.pop("tags")
        ingredients_d = validated_data.pop("ingredients")
        recipe = Recipes.objects.create(**validated_data)
        for ingredient in ingredients_d:
            amount = ingredient["amount"]
            id = ingredient['id']
            AmountIngredients.objects.create(
                ingredients=get_object_or_404(Ingredients, id=id),
                recipe=recipe,
                amount=amount
            )
        for tag in tags_d:
            recipe.tags.add(tag)
        return recipe

    def validate(self, data):
        ingredients_d = data["ingredients"]
        ingredients_set = set()
        for ingredient in ingredients_d:
            if ingredient["id"] in ingredients_set:
                raise serializers.ValidationError(
                    {"ingredients": "Ингредиенты в рецепте уникальны!"}
                )
            if ingredient["amount"] <= 0:
                raise ValidationError({
                    "ingredients": "Необходимо добавить ингредиенты!"
                })
            ingredients_set.append(ingredient["id"])
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
        return data

    def update(self, instance, validated_data):
        tags_d = validated_data.pop("tags")
        ingredients_d = validated_data.pop("ingredients")
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        AmountIngredients.objects.filter(recipe=instance).delete()
        for ingredient in ingredients_d:
            amount = ingredient['amount']
            id = ingredient['id']
            AmountIngredients.objects.create(
                ingredient=get_object_or_404(Ingredients, id=id),
                recipe=instance,
                amount=amount
            )
        instance.save()
        instance.tags.set(tags_d)
        return instance

    def to_representation(self, instance):
        request = self.context.get("request")
        context = {"request": request}
        return GetRecipesSerializer(instance, context=context).data


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор модели Избранные_рецепты"""

    class Meta:
        fields = "__all__"
        model = Favorite

    def validate(self, data):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        recipe = data['recipe']
        if Favorite.objects.filter(user=request.user, recipe=recipe).exists():
            raise serializers.ValidationError({
                'status': 'Рецепт уже в избранном!'
            })
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return SupportRecipesSerializer(
            instance.recipe, context=context).data


class ShoppingListSerializer(serializers.ModelSerializer):
    """Сериализатор модели Список_покупок"""

    class Meta:
        fields = "__all__"
        model = ShoppingList

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return SupportRecipesSerializer(
            instance.recipe, context=context).data
