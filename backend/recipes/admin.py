from django.contrib import admin

from recipes.models import Tags, Ingredients, TagsRecipes, Recipes, \
    AmountIngredients

admin.site.register(Tags)
admin.site.register(Ingredients)
admin.site.register(Recipes)
admin.site.register(TagsRecipes)
admin.site.register(AmountIngredients)
