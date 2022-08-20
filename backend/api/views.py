from rest_framework import viewsets, filters, mixins, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from api.serializers import MyUserSerializer, MySignupSerializer
from users.models import User


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для доступа к Пользовател(-ю/ям)"""

    queryset = User.objects.all()
    serializer_class = MyUserSerializer
    permission_classes = (AllowAny,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("id",)
    lookup_field = "id"


@api_view(["GET"])
@permission_classes([IsAuthenticated,])
def get_profile(request):
    serializer = MyUserSerializer(request.user)
    return Response(serializer.data)


# class SignUpViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
#     """Вьюсет для регистрации пользователя"""
#
#     queryset = User.objects.all()
#     serializer_class = MySignupSerializer
#     permission_classes = (AllowAny,)
#
#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         instance = serializer.save()
#         instance.set_unusable_password()
#         instance.save()
#         return Response(serializer.data, status=status.HTTP_200_OK)
