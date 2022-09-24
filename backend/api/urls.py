from api.views import (IngredientsViewSet, MainSubscribeViewSet,
                       RecipesViewSet, SubscribeListView, TagsViewSet)
from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("tags", TagsViewSet, basename="tags")
router.register("ingredients", IngredientsViewSet, basename="ingredients")
router.register("recipes", RecipesViewSet, basename="recipes")

urlpatterns = [
    path(
        "users/subscriptions/",
        SubscribeListView.as_view(),
        name="subscriptions"
    ),
    path(
        "users/<int:user_id>/subscribe/",
        MainSubscribeViewSet.as_view(),
        name="subscribe"
    ),
    path("", include("djoser.urls")),
    re_path(r"^auth/", include("djoser.urls.authtoken")),
    path("", include(router.urls)),
]
