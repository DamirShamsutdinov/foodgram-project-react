from rest_framework.validators import ValidationError

from recipes.models import Ingredients, Tags


def validate_ingredients(data):
    """Валидация ингредиентов и количества."""
    if not data:
        raise ValidationError({'ingredients': ['Обязательное поле.']})
    if len(data) < 1:
        raise ValidationError({'ingredients': ['Нет ингредиентов.']})
    unique_ingredient = []
    for ingredient in data:
        if not ingredient.get('id'):
            raise ValidationError({'ingredients': ['Нет id ингредиента.']})
        id = ingredient.get('id')
        if not Ingredients.objects.filter(id=id).exists():
            raise ValidationError(
                {'ingredients': ['В базе нет такого ингредиента.']})
        if id in unique_ingredient:
            raise ValidationError(
                {'ingredients': ['Уже есть такой ингредиент']})
        unique_ingredient.append(id)
        amount = int(ingredient.get('amount'))
        if amount < 1:
            raise ValidationError({'amount': ['Минимальное колличество - 1.']})
    return data


def validate_tags(data):
    """Валидация тэгов."""
    if not data:
        raise ValidationError({'tags': ['Обязательное поле.']})
    for tag in data:
        if not Tags.objects.filter(id=tag).exists():
            raise ValidationError({'tags': ['Неверный Тег']})
    return data