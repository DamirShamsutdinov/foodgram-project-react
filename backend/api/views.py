from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin

from api.filters import RecipeFilter
from api.permissions import IsUserSuperuserOrReadOnly
from api.serializers import TagsSerializer, \
    IngredientsSerializer, GetRecipesSerializer, CreateRecipesSerializer
from recipes.models import Tags, Ingredients, Recipes


class TagsViewSet(ListModelMixin, RetrieveModelMixin, viewsets.GenericViewSet):
    """Вьюсет для получения Тега"""
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    permission_classes = (IsUserSuperuserOrReadOnly,)
    pagination_class = None


class IngredientsViewSet(ListModelMixin, RetrieveModelMixin,
                         viewsets.GenericViewSet):
    """Вьюсет для получения Ингредиентов"""
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    permission_classes = (IsUserSuperuserOrReadOnly,)
    pagination_class = None


class RecipesViewSet(viewsets.ModelViewSet):
    """Вьюсет для получения Рецептов"""
    queryset = Recipes.objects.all()
    permission_classes = (IsUserSuperuserOrReadOnly,)
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = (DjangoFilterBackend,)
    # filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH', 'DELETE'):
            return CreateRecipesSerializer
        return GetRecipesSerializer




