from datetime import datetime
from http import HTTPStatus

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST

from api.filters import RecipeFilter
from api.permissions import IsUserSuperuserOrReadOnly
from api.serializers import TagsSerializer, \
    IngredientsSerializer, GetRecipesSerializer, \
    CreateRecipesSerializer
from recipes.models import Tags, Ingredients, Recipes, Favorite, ShoppingList, \
    AmountIngredients


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

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        return serializer.save(author=self.request.user)
