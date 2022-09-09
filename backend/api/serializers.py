from django.db.models import F
from rest_framework import serializers
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404

from api.validations import validate_tags, validate_ingredients
from recipes.models import Tags, Ingredients, Favorite, ShoppingList, Recipes, \
    AmountIngredients, TagsRecipes
from users.models import Subscription, CustomUser

from drf_extra_fields.fields import Base64ImageField


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
        """Проверка 'subscribed' на наличие подписок"""
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=request.user,
            author=obj.id
        ).exists()


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


class GetRecipesSerializer(serializers.ModelSerializer):
    """GET Сериализатор Рецептов"""
    tags = TagsSerializer(many=True)
    author = ListDetailUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
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

    def get_is_favorited(self, object):
        """Рецепт в избранном"""
        user_id = self.context.get('request').user.id
        return Favorite.objects.filter(
            user=user_id,
            recipe=object.id
        ).exists()

    def get_is_in_shopping_cart(self, object):
        """Ингредиенты_Рецепта в корзине"""
        user_id = self.context.get('request').user.id
        return ShoppingList.objects.filter(
            user=user_id,
            recipe=object.id
        ).exists()

    @staticmethod
    def get_ingredients(obj):
        queryset = AmountIngredients.objects.filter(recipe=obj)
        return AllIngredientsSerializer(queryset, many=True).data

    def to_representation(self, objects):
        data = super().to_representation(objects)
        data["image"] = objects.image.url
        return data


class CreateRecipesSerializer(serializers.ModelSerializer):
    """Создание/обновление/удаление Сериализатор Рецептов"""
    author = ListDetailUserSerializer(read_only=True)
    ingredients = AmountRecipeSerializer(
        source='amountingredients_set',
        many=True
    )
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

    def validate_ingredients(self, value):
        ingredients = value
        if not ingredients:
            raise ValidationError({
                'ingredients': 'Необходимо добавить ингредиенты!'
            })
        ingredients_list = []
        for item in ingredients:
            ingredient = get_object_or_404(Ingredients, id=item['id'])
            if ingredient in ingredients_list:
                raise ValidationError({
                    'ingredients': 'Ингридиенты не повторяются!'
                })
            ingredients_list.append(ingredient)
        return value

    def validate_tags(self, value):
        tags = value
        if not tags:
            raise ValidationError({
                'tags': 'Необходимо добавить тег!'
            })
        tags_list = []
        for tag in tags:
            if tag in tags_list:
                raise ValidationError({
                    'tags': 'Теги не повторяются!'
                })
            tags_list.append(tag)
        return value

    @staticmethod
    def add_ingredients_tags(ingredients, recipe, tags):
        for ingredient in ingredients:
            amount = ingredient['amount']
            if AmountIngredients.objects.filter(
                    recipe=recipe,
                    ingredients=ingredients['id']
            ).exists():
                amount += F('amount')
            AmountIngredients.objects.update_or_create(
                recipe=recipe,
                ingredients=ingredients['id'],
                defaults={'amount': amount}
            )
        for tag in tags:
            recipe.tags.add(tag)
            TagsRecipes.objects.create(
                    tag=tag,
                    recipe=recipe,
                )

    def create(self, validated_data):
        print(f'!!!{validated_data}!!!')
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        recipe = Recipes.objects.create(**validated_data)
        self.add_ingredients_tags(ingredients, recipe, tags)
        return recipe

    def update(self, recipe, validated_data):
        AmountIngredients.objects.filter(recipe=recipe).delete()
        TagsRecipes.objects.filter(recipe=recipe).delete()
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        self.add_ingredients_tags(ingredients, recipe, tags)
        return super().update(recipe, validated_data)

    def to_representation(self, objects):
        data = super().to_representation(objects)
        data["image"] = objects.image.url
        return data

# class SubscriptionSerializer(serializers.ModelSerializer):
