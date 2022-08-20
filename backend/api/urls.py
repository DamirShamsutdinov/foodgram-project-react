from rest_framework.routers import DefaultRouter
from django.urls import path, include, re_path

from api.views import UserViewSet, get_profile

router = DefaultRouter()
router.register("users", UserViewSet, basename="users")

urlpatterns = [
    path("users/me/", get_profile, name="get_profile"),
    path("", include(router.urls)),
    path("", include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
