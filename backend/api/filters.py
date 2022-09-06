from django_filters import rest_framework as filters

from recipes.models import Tags


class RecipeFilter(filters.FilterSet):
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')

    class Meta:
        model = Tags
        fields = ["name", "color", "slug"]
