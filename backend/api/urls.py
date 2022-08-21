from rest_framework.routers import DefaultRouter
from django.urls import path, include, re_path

router = DefaultRouter()


urlpatterns = [
    path("", include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
