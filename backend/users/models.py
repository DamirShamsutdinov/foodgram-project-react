from django.contrib.auth.models import AbstractUser
from django.db.models import CharField
from django.db import models
from pkg_resources import _


class User(AbstractUser):
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


class Subscription(models.Model):
    """Подписка на других авторов рецепта"""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )

    def __str__(self):
        return f'Пользователь {self.author}, подписался на {self.following}'


