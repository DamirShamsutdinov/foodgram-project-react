from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.filters import RecipeFilter
from api.permissions import IsUserSuperuserOrReadOnly
from api.serializers import (CreateRecipesSerializer, GetRecipesSerializer,
                             IngredientsSerializer, SupportRecipesSerializer,
                             TagsSerializer)
from recipes.models import (AmountIngredients, Favorite, Ingredients, Recipes,
                            ShoppingList, Tags)
from users.models import CustomUser, Follow
from users.serializers import SubscribeSerializer


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

    @action(detail=True, methods=["post", "delete"], url_path="favorite")
    def favorite(self, request, pk=None):
        """Удаление и добавление рецептов в Избранное"""
        user = request.user
        if request.method == "POST":
            recipe = get_object_or_404(Recipes, pk=pk)
            relation = Favorite.objects.filter(user=user, recipe=recipe)
            if relation.exists():
                return Response(
                    "Уже есть в списке Избранных!",
                    status=status.HTTP_400_BAD_REQUEST
                )
            Favorite.objects.create(user=user, recipe=recipe)
            serializer = SupportRecipesSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == "DELETE":
            recipe = get_object_or_404(Recipes, pk=pk)
            relation = Favorite.objects.filter(user=user, recipe=recipe)
            if not relation.exists():
                return Response(
                    "Нет в избранном!",
                    status=status.HTTP_400_BAD_REQUEST
                )
            relation.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=True, methods=["post", "delete"], url_path="shopping_cart")
    def shopping_cart(self, request, pk=None):
        """Удаление и добавление рецептов в Покупки"""
        user = request.user
        if request.method == "POST":
            recipe = get_object_or_404(Recipes, pk=pk)
            relation = ShoppingList.objects.filter(user=user, recipe=recipe)
            if relation.exists():
                return Response(
                    "Уже есть в списке Покупок!",
                    status=status.HTTP_400_BAD_REQUEST
                )
            ShoppingList.objects.create(user=user, recipe=recipe)
            serializer = SupportRecipesSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == "DELETE":
            recipe = get_object_or_404(Recipes, pk=pk)
            relation = ShoppingList.objects.filter(user=user, recipe=recipe)
            if not relation.exists():
                return Response(
                    "Нет в списке покупок!",
                    status=status.HTTP_400_BAD_REQUEST
                )
            relation.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

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
    serializer_class = SubscribeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CustomUser.objects.filter(following__user=self.request.user)


class MainSubscribeViewSet(APIView):
    serializer_class = SubscribeSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user_id = self.kwargs["user_id"]
        if user_id == request.user.id:
            return Response(
                {"error": "Нельзя подписаться на себя"},
                status=status.HTTP_400_BAD_REQUEST
            )
        author = get_object_or_404(CustomUser, id=user_id)
        if Follow.objects.filter(
                user=request.user,
                author_id=user_id
        ).exists():
            return Response(
                {"error": "Вы уже подписаны на пользователя"},
                status=status.HTTP_400_BAD_REQUEST
            )
        Follow.objects.create(
            user=request.user,
            author_id=user_id
        )
        return Response(
            self.serializer_class(author, context={"request": request}).data,
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, *args, **kwargs):
        user_id = self.kwargs.get("user_id")
        get_object_or_404(CustomUser, id=user_id)
        subscription = Follow.objects.filter(
            user=request.user,
            author_id=user_id
        )
        if subscription:
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"error": "Подписки на автора - нет"},
            status=status.HTTP_400_BAD_REQUEST
        )
