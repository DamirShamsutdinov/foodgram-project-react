from rest_framework import serializers
from pkg_resources import _
from rest_framework.validators import UniqueValidator

from users.models import User, Subscription


class MyUserSerializer(serializers.ModelSerializer):
    """Сериализатор модели Юзер GET запрос."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed"
        )

    def get_is_subscribed(self, obj):
        user_id = obj.id if isinstance(obj, User) else obj.author.id
        request_user = self.context.get('request').user.id
        queryset = Subscription.objects.filter(
            author=user_id,
            following=request_user
        ).exists()
        return queryset


# class SubscriptionSerializer(serializers.ModelSerializer):


class MySignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "email",
            "username",
            "first_name",
            "last_name",
            "password"
        )

    def validate_username(self, attrs):
        if attrs == "me":
            raise serializers.ValidationError(
                'Запрещено имя "me", придумайте другое имя!'
            )
        return attrs

# class TokenSerializer(TokenObtainSerializer):
#     token_class = AccessToken
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields["confirmation_code"] = serializers.CharField(
#             required=False
#         )
#         self.fields["password"] = serializers.HiddenField(default="")
#
#     def validate(self, attrs):
#         self.user = get_object_or_404(User, username=attrs["username"])
#         if self.user.confirmation_code != attrs["confirmation_code"]:
#             raise serializers.ValidationError("Неверный код подтверждения")
#         data = str(self.get_token(self.user))
#
#         return {"token": data}
