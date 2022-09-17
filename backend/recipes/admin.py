from django.contrib import admin

from recipes.models import (AmountIngredients, Ingredients, Recipes, Tags,
                            TagsRecipes, Favorite, ShoppingList)


@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "name",
        "color",
        "slug",
    )
    search_fields = ("name",)
    empty_value_display = "-пусто-"


@admin.register(Ingredients)
class IngredientsAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "name",
        "measurement_unit"
    )
    search_fields = ("name",)
    empty_value_display = "-пусто-"


@admin.register(Recipes)
class RecipesAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "author",
        "name",
        "image",
        "text",
        "ingredients",
        "tags",
        "cooking_time",
        "published"
    )
    search_fields = ("name",)
    empty_value_display = "-пусто-"


@admin.register(AmountIngredients)
class AmountIngredientsAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "ingredients",
        "recipe",
        "amount",
    )
    search_fields = ("recipe", "ingredients")
    empty_value_display = "-пусто-"


@admin.register(TagsRecipes)
class TagsRecipesAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "tag",
        "recipe"
    )
    search_fields = ("tag", "recipe")
    empty_value_display = "-пусто-"


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "user",
        "recipe"
    )
    search_fields = ("user", "recipe")
    empty_value_display = "-пусто-"


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    llist_display = (
        "pk",
        "user",
        "recipe"
    )
    search_fields = ("user", "recipe")
    empty_value_display = "-пусто-"
