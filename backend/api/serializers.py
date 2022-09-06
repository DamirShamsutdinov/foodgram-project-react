from django.db.models import F
from rest_framework import serializers
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404

from recipes.models import Tags, Ingredients, Favorite, ShoppingList, Recipes, \
    AmountIngredients
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


class IngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор модели Ингредиенты"""

    class Meta:
        model = Ingredients
        fields = (
            "id",
            "name",
            "measurement_unit"
        )


class IngredientsInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор модели Ингредиенты_Рецепта"""
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredients.objects.all())

    class Meta:
        model = AmountIngredients
        fields = (
            "id",
            "amount"
        )


class GetRecipesSerializer(serializers.ModelSerializer):
    """GET Сериализатор Рецептов"""
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tags.objects.all(),
        many=True
    )
    image = Base64ImageField()
    author = ListDetailUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
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
            "published"
        )
        ordering = ("-published",)

    def get_ingredients(self, obj):
        recipe = obj
        ingredients = recipe.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('amountingredients__amount')
        )
        return ingredients


    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
            recipe=obj,
            user=request.user
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return ShoppingList.objects.filter(
            recipe=obj,
            user=request.user
        ).exists()

    def to_representation(self, instance):
        return GetRecipesSerializer(
            instance, context={'request': self.context['request']}
        ).data


class CreateRecipesSerializer(serializers.ModelSerializer):
    """Создание/обновление/удаление Сериализатор Рецептов"""
    ingredients = IngredientsInRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tags.objects.all(),
        many=True
    )
    image = Base64ImageField()
    published = serializers.HiddenField(default=timezone.now)

    class Meta:
        model = Recipes
        fields = (
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
                'ingredients': 'Нужен хотя бы один ингредиент!'
            })
        ingredients_list = []
        for item in ingredients:
            ingredient = get_object_or_404(Ingredients, id=item['id'])
            if ingredient in ingredients_list:
                raise ValidationError({
                    'ingredients': 'Ингридиенты не могут повторяться!'
                })
            if int(item['amount']) <= 0:
                raise ValidationError({
                    'amount': 'Количество ингредиента должно быть больше 0!'
                })
            ingredients_list.append(ingredient)
        return value

    def validate_tags(self, value):
        tags = value
        if not tags:
            raise ValidationError({
                'tags': 'Нужно выбрать хотя бы один тег!'
            })
        tags_list = []
        for tag in tags:
            if tag in tags_list:
                raise ValidationError({
                    'tags': 'Теги должны быть уникальными!'
                })
            tags_list.append(tag)
        return value

    def create_ingredients_amounts(self, ingredients, recipe):
        objs = [
            AmountIngredients(
                ingredient=Ingredients.objects.get(id=ingredient['id']),
                recipe=recipe,
                amount=ingredient['amount']
            )
            for ingredient in ingredients
        ]
        AmountIngredients.objects.bulk_create(objs)

    def create(self, validated_data):
        request = self.context.get('request')
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        recipe = Recipes.objects.create(author=request.user, **validated_data)
        recipe.tags.set(tags)
        self.create_ingredients_amounts(
            recipe=recipe,
            ingredients=ingredients
        )
        return recipe

    def update(self, instance, validated_data):
        instance.ingredients = validated_data.pop(
            'ingredients',
            instance.ingredients
        )
        if 'ingredients' in validated_data:
            ingredients_data = validated_data.pop('ingredients')
            lst = []
            for ingredient in ingredients_data:
                current_ingredient, status = Ingredients.objects.get_or_create(
                    **ingredient
                )
                lst.append(current_ingredient)
            instance.achievements.set(lst)
        instance.tags = validated_data.get('tags', instance.tags)
        if 'tags' in validated_data:
            tags_data = validated_data.pop('tags')
            lst = []
            for tag in tags_data:
                current_tag, status = Tags.objects.get_or_create(**tag)
                lst.append(current_tag)
            instance.achievements.set(lst)
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )
        instance.save()
        return instance

    def to_representation(self, instance):
        return GetRecipesSerializer(
            instance,
            context={'request': self.context['request']}
        ).data

# class SubscriptionSerializer(serializers.ModelSerializer):

