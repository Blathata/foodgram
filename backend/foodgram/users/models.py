from django.contrib.auth.models import AbstractUser
from django.db.models import (
    CASCADE,
    BooleanField,
    CharField,
    EmailField,
    ForeignKey,
    Model,
    UniqueConstraint,
)

from core.enums import Limits
from core import help_texts


class MyUser(AbstractUser):
    """Кастомная модель пользователя"""
    email = EmailField(
        max_length=Limits.MAX_LEN_EMAIL_USER.value,
        unique=True,
        help_text=help_texts.HELP_TEXT_EMAIL_USER,
        verbose_name='Электроная почта пользователя'
    )
    username = CharField(
        max_length=Limits.MAX_LEN_USERNAME_USER.value,
        unique=True,
        help_text=help_texts.HELP_TEXT_USERNAME_USER,
        verbose_name='Юзернейм'
    )
    first_name = CharField(
        max_length=Limits.MAX_LEN_FIRST_NAME_USER.value,
        help_text=help_texts.HELP_TEXT_FIRST_NAME_USER,
        verbose_name= 'Имя пользователя'
    )
    last_name = CharField(
        max_length=Limits.MAX_LEN_LAST_NAME_USER.value,
        help_text=help_texts.HELP_TEXT_LAST_NAME_USER,
        verbose_name= 'Фамилия пользователя'
    )
    password = CharField(
        max_length=Limits.MAX_LEN_PASSWORD_USER.value,
        help_text=help_texts.HELP_TEXT_PASSWORD_USER,
        verbose_name="Пароль",
    )
    is_active = BooleanField(
        default=True,
        verbose_name="Активирован",
    )


    class Meta:
        ordering = ['id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscribe(Model):
    """Модель подписок"""
    user = ForeignKey(
        MyUser,
        related_name='subscriber',
        verbose_name="Подписчик",
        on_delete=CASCADE,
    )
    author = ForeignKey(
        MyUser,
        related_name='subscribing',
        verbose_name="Автор",
        on_delete=CASCADE,
    )

    class Meta:
        ordering = ['-id']
        constraints = [
            UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription'
                )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
