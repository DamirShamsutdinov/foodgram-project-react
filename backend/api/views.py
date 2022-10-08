from api.filters import RecipeFilter
from api.paginations import CustomPagination
from api.permissions import IsUserSuperuserOrReadOnly
from api.serializers import (CreateRecipesSerializer, GetRecipesSerializer,
                             IngredientsSerializer, SupportRecipesSerializer,
                             TagsSerializer)
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (AmountIngredients, Favorite, Ingredients, Recipes,
                            ShoppingList, Tags)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from users.models import CustomUser, Follow
from users.serializers import SubscribeSerializer, SubscribeListSerializer


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
    http_method_names = ["get", "post", "patch", "delete"]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == "GET":
            return GetRecipesSerializer
        return CreateRecipesSerializer

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        return serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        serializer = CreateRecipesSerializer(
            instance=serializer.instance,
            context={"request": self.request}
        )
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def __base(self, request, cur_model, pk=None):
        recipe = get_object_or_404(Recipes, pk=pk)
        user = self.request.user
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        checked_queryset = cur_model.objects.filter(
            user=user, recipe=recipe)
        if request.method == 'POST':
            if not checked_queryset:
                created = cur_model.objects.create(user=user, recipe=recipe)
                serializer = SupportRecipesSerializer(created.recipe)
                return Response(
                    status=status.HTTP_201_CREATED, data=serializer.data)
            else:
                if cur_model == Favorite:
                    data = {'errors': 'Этот рецепт уже в избранном'}
                elif cur_model == ShoppingList:
                    data = {'errors': 'Этот рецепт уже в покупках'}
                return Response(status=status.HTTP_400_BAD_REQUEST, data=data)
        elif request.method == 'DELETE':
            if not checked_queryset:
                if cur_model == Favorite:
                    data = {
                        'errors': 'Этого рецепта нет в избранном'}
                elif cur_model == ShoppingList:
                    data = {
                        'errors': 'Этого рецепта нет в списке покупок'}
                return Response(status=status.HTTP_400_BAD_REQUEST, data=data)
            else:
                checked_queryset.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post", "delete"], url_path="favorite")
    def favorite(self):
        return self.__base(request, cur_model=Favorite, pk=pk)

    @action(detail=True, methods=["post", "delete"], url_path="shopping_cart")
    def shopping_cart(self):
        return self.__base(request, cur_model=ShoppingList, pk=pk)

    @action(detail=False, methods=["get"], url_path="download_shopping_cart")
    def download_shopping_cart(self, request):
        ingredients = AmountIngredients.objects.filter(
            recipe__shoppinglist__user=request.user).values(
            'ingredients__name', 'ingredients__measurement_unit').annotate(
            amount=Sum('amount'))
        shopping_cart = '\n'.join([
            f'{i["ingredients__name"]} '
            f'({i["ingredients__measurement_unit"]}) – '
            f'{i["amount"]}'
            for i in ingredients
        ])
        response = HttpResponse(shopping_cart, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename=shopping_cart.txt')
        return response


class SubscribeListView(ListAPIView):
    """Вью подписок"""
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        queryset = CustomUser.objects.filter(following__user=user)
        page = self.paginate_queryset(queryset)
        serializer = SubscribeListSerializer(
            page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)


class MainSubscribeViewSet(APIView):
    """Подписка/отписка"""
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        data = {'author': id, 'user': request.user.id}
        serializer = SubscribeSerializer(
            data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        user = request.user
        author = get_object_or_404(CustomUser, id=id)
        follow = get_object_or_404(Follow, user=user, author=author)
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
