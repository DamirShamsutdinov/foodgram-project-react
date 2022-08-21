from rest_framework import serializers
from users.models import Subscription, CustomUser


class ListDetailUserSerializer(serializers.ModelSerializer):
    """Сериализатор модели Юзер GET запрос."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            # "password",
            "is_subscribed"
        )

    def get_is_subscribed(self, obj):
        """Проверка 'subscribed' на наличие подписок"""
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            author=request.user,
            follower=obj.id
        ).exists()

# class SubscriptionSerializer(serializers.ModelSerializer):
