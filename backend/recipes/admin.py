from django.contrib import admin
from recipes.models import (AmountIngredients, Favorite, Ingredients, Recipes,
                            ShoppingList, Tags, TagsRecipes)


@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "color", "slug",)
    search_fields = ("name",)
    list_filter = ("name",)
    empty_value_display = "-пусто-"


@admin.register(Ingredients)
class IngredientsAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "measurement_unit")
    search_fields = ("name",)
    list_filter = ("name",)
    empty_value_display = "-пусто-"


class AmountIngredientsInline(admin.StackedInline):
    model = AmountIngredients
    autocomplete_fields = ("ingredients",)


@admin.register(Recipes)
class RecipesAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "author",
        "name",
        "image",
        "text",
        "cooking_time",
        "published",
        "is_favorite"
    )
    list_filter = ("name", "author", "tags",)
    search_fields = ("name", "author",)
    inlines = (AmountIngredientsInline,)
    empty_value_display = "-пусто-"

    def is_favorite(self, obj):
        return obj.favorite.count()


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "recipe")
    list_filter = ("user",)
    search_fields = ("user",)
    empty_value_display = "-пусто-"


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "recipe")
    list_filter = ("user",)
    search_fields = ("user",)
    empty_value_display = "-пусто-"
