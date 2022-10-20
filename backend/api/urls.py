from django.urls import include, path, re_path
from rest_framework.routers import SimpleRouter

from api.views import (IngredientsViewSet, MainSubscribeViewSet,
                       RecipesViewSet, SubscribeListView, TagsViewSet)

router = SimpleRouter()
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
    path("", include(router.urls)),
    path("", include("djoser.urls")),
    re_path(r"^auth/", include("djoser.urls.authtoken")),
]
