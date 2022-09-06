from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter

from api.views import TagsViewSet, IngredientsViewSet, RecipesViewSet

router = DefaultRouter()
router.register("tags", TagsViewSet, basename="tags")
router.register("ingredients", IngredientsViewSet, basename="ingredients")
router.register("recipes", RecipesViewSet, basename="recipes")

urlpatterns = [
    path('', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
