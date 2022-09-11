from colorfield.fields import ColorField
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint

from users.models import CustomUser


class Tags(models.Model):
    """модели Тегов"""
    name = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="Название_тега"
    )
    color = ColorField(
        unique=True,
        verbose_name="Цвет_тега",
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name="Слаг_тега"
    )

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class Ingredients(models.Model):
    """модели Ингредиентов"""
    name = models.CharField(
        max_length=150,
        verbose_name="Название_ингредиента",
    )
    measurement_unit = models.CharField(
        max_length=50,
        verbose_name="Мера_измерения_ингредиента",
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        ordering = ["name"]
        constraints = [
            UniqueConstraint(
                fields=["name", "measurement_unit"],
                name="unique_ingredients")
        ]

    def __str__(self):
        return f"{self.name}, {self.measurement_unit}"


class Recipes(models.Model):
    """модели Рецептов"""
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name="recipes",
        verbose_name="Автор_рецепта",
    )
    name = models.CharField(
        max_length=150,
        verbose_name="Название_блюда",
    )
    image = models.ImageField(
        upload_to="images",
        null=False,
        verbose_name="Картинка_блюда",
    )
    text = models.TextField(
        help_text="Введите текст отзыва",
        verbose_name="Описание_блюда",
    )
    ingredients = models.ManyToManyField(
        Ingredients,
        related_name="recipes",
        through="AmountIngredients",
        verbose_name="Ингредиенты",
    )
    tags = models.ManyToManyField(
        Tags,
        related_name="recipes",
        through="TagsRecipes",
        verbose_name="Тег",
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="Время_приготовления",
        validators=[MinValueValidator(1, message="Минимальное значение 1!")]
    )
    published = models.DateTimeField("Дата публикации", auto_now_add=True)

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ["name"]

    def __str__(self):
        return self.name


class AmountIngredients(models.Model):
    """пром_модель Ингредиентов"""
    ingredients = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        null=True,
        related_name="ingredients_list",
        verbose_name="Ингредиент",
    )
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        null=True,
        related_name="ingredients_list",
        verbose_name="Рецепт",
    )
    amount = models.SmallIntegerField(
        verbose_name="Количество_ингредиентов",
        validators=[MinValueValidator(1, message="Минимальное количество 1!")]
    )

    class Meta:
        verbose_name = "Лист_Ингредиентов"
        constraints = [
            UniqueConstraint(
                fields=["ingredients", "recipe"],
                name="unique_ingredients_amount")
        ]

    def __str__(self):
        return (
            f"{self.ingredients.name}"
            f"{self.amount}_{self.ingredients.measurement_unit}"
        )


class TagsRecipes(models.Model):
    """пром_модель Тегов"""
    tag = models.ForeignKey(Tags, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Теги_Рецепта"

    def __str__(self):
        return f"Теги_ {self.tag} для рецепта_ {self.recipe}"


# from django.db.models import Sum
# class Shopping_cart(models.Model):
#     field_name_sum = ModelName.objects.aggregate(Sum("field_name"))


class Favorite(models.Model):
    """модель Избранные_рецепты"""
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        null=True,
        related_name="favorite",
        verbose_name="Юзер",
    )
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        null=True,
        related_name="favorite",
        verbose_name="Рецепт"
    )

    class Meta:
        verbose_name = "Избранные_рецепты"
        constraints = [
            UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_favorite")
        ]

    def __str__(self):
        return f"{self.user} - {self.recipe}"


class ShoppingList(models.Model):
    """модель Список_Покупок"""
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        null=True,
        related_name="shoppinglist",
        verbose_name="Юзер",
    )
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        null=True,
        related_name="shoppinglist",
        verbose_name="Рецепт"
    )

    class Meta:
        verbose_name = "Список_Покупок"
        constraints = [
            UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_shoppinglist")
        ]

    def __str__(self):
        return f"{self.user} - {self.recipe}"
