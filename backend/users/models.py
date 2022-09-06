from django.contrib.auth.models import AbstractUser
from django.db.models import CharField, UniqueConstraint
from django.db import models
from pkg_resources import _


class CustomUser(AbstractUser):
    """Модель Пользователя"""
    password = CharField(_('password'), max_length=150)
    email = models.EmailField(_('email address'), blank=True, unique=True)
    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = [
        "username",
        "first_name",
        "last_name",
    ]

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return self.email


class Subscription(models.Model):
    """Подписка на других авторов рецепта"""
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name=''
    )
    constraints = [UniqueConstraint(
        fields=['user', 'author'],
        name='unique_subscription')
    ]

    def __str__(self):
        return f'Пользователь {self.user}, подписался на {self.author}'
