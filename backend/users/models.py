from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import UniqueConstraint

from pkg_resources import _


class CustomUser(AbstractUser):
    """Модель Пользователя"""
    email = models.EmailField(_("email address"), blank=True, unique=True)
    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = ("username", "first_name", "last_name")

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return self.email


class Follow(models.Model):
    """модель Подписок"""
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Юзер",
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name="Автор_рецепта"
    )

    class Meta:
        verbose_name = "Подписка_рецепты"
        constraints = [
            UniqueConstraint(fields=("user", "author"), name="unique_follow")
        ]

    def __str__(self):
        return f"Пользователь {self.user} подписан на {self.author}"
