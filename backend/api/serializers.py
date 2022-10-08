from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (AmountIngredients, Favorite, Ingredients, Recipes,
                            ShoppingList, Tags)
from rest_framework import serializers

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
    id = serializers.IntegerField(source="ingredients.id")
    name = serializers.CharField(source="ingredients.name")
    measurement_unit = serializers.CharField(
        source="ingredients.measurement_unit"
    )

    class Meta:
        model = AmountIngredients
        fields = ("id", "name", "measurement_unit", "amount")


class AmountRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиенты для создания рецепта"""
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredients.objects.all())
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
    author = CurrentUserSerializer()
    ingredients = serializers.SerializerMethodField()
    image = Base64ImageField()
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
        )
        read_only_fields = ("is_favorited", "is_in_shopping_cart")

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
    ingredients = AmountRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tags.objects.all(),
        many=True
    )
    image = Base64ImageField()

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
        )
        read_only_fields = ("author",)

    def add_ingredients(self, recipe, ingredients):
        for ingredient in ingredients:
            ingredient_id = ingredient.get("id")
            amount = ingredient.get("amount")
            AmountIngredients.objects.create(
                ingredients_id=ingredient_id,
                amount=amount,
                recipe=recipe
            )

    def create(self, validated_data):
        tags_d = validated_data.pop("tags")
        ingredients_d = validated_data.pop("ingredients")
        recipe = Recipes.objects.create(**validated_data)
        self.add_ingredients(recipe, ingredients_d)
        for tag in tags_d:
            recipe.tags.add(get_object_or_404(Tags, id=tag.id))
        recipe.save()
        return recipe

    def validate(self, data):
        ingredients_data = data['ingredients']
        ingredients_set = set()
        for ingredient in ingredients_data:
            if ingredient['amount'] <= 0:
                raise serializers.ValidationError(
                    'Вес ингредиента должен быть больше 0'
                )
            if ingredient['id'] in ingredients_set:
                raise serializers.ValidationError(
                    'Ингредиент в рецепте не должен повторяться.'
                )
            ingredients_set.add(ingredient['id'])
        return data

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.get(
            "cooking_time",
            instance.cooking_time
        )
        instance.tags.clear()
        instance.ingredients.clear()
        AmountIngredients.objects.filter(recipe=instance).delete()
        tags_d = validated_data.pop("tags")
        ingredients_d = validated_data.pop("ingredients")
        for tag in tags_d:
            instance.tags.add(get_object_or_404(Tags, id=tag.id))
        self.add_ingredients(instance, ingredients_d)
        return super().update(instance, validated_data)


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
