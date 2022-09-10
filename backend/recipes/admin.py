from django.contrib import admin

from recipes.models import (AmountIngredients, Ingredients, Recipes, Tags,
                            TagsRecipes)

admin.site.register(Tags)
admin.site.register(Ingredients)
admin.site.register(Recipes)
admin.site.register(TagsRecipes)
admin.site.register(AmountIngredients)
