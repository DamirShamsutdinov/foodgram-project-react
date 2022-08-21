from rest_framework import permissions

allowed_methods = ("GET", "POST")


class GetPost(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.method in allowed_methods

    def has_permission(self, request, view):
        return request.method in allowed_methods