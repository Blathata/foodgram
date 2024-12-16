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


class MyUser(AbstractUser):
    """Кастомная модель пользователя"""
    email = EmailField(
        max_length=256,
        unique=True,
        help_text='Обязательно к заполнению. ',
        verbose_name='Электроная почта пользователя'
    )
    username = CharField(
        max_length=32,
        unique=True,
        help_text='Обязательно к заполнению. ',
        verbose_name='Юзернейм'
    )
    first_name = CharField(
        max_length=32,
        help_text='Обязательно к заполнению. ',
        verbose_name= 'Имя пользователя'
    )
    last_name = CharField(
        max_length=32,
        help_text='Обязательно к заполнению. ',
        verbose_name= 'Фамилия пользователя'
    )
    password = CharField(
        verbose_name="Пароль",
        max_length=128,
        help_text='Обязательно к заполнению. ',
    )
    is_active = BooleanField(
        verbose_name="Активирован",
        default=True,
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
