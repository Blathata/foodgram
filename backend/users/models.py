"""Модуль для создания, настройки и управления моделью пользователей."""

from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db.models import (
    CASCADE,
    BooleanField,
    CharField,
    EmailField,
    ImageField,
    ForeignKey,
    Model,
    UniqueConstraint,
    CheckConstraint,
    F,
    Q,
)

from core.enums import Limits
from core import help_texts


class MyUser(AbstractUser):
    """Кастомная модель пользователя"""
    USER_REGEX = r'^[\w.@+-]+$'

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ("username", "first_name", "last_name")

    username = CharField(
        max_length=Limits.MAX_LEN_USERNAME_USER.value,
        unique=True,
        null=False,
        help_text=help_texts.HELP_TEXT_USERNAME_USER,
        verbose_name='Юзернейм',
        validators=[
            RegexValidator(
                regex=USER_REGEX,
                message='Используйте только буквы и символы: w . @ + - ',
            ),
        ]
    )
    email = EmailField(
        max_length=Limits.MAX_LEN_EMAIL_USER.value,
        unique=True,
        null=False,
        help_text=help_texts.HELP_TEXT_EMAIL_USER,
        verbose_name='Электроная почта пользователя'
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
    avatar = ImageField(
        upload_to='avatar/',
        blank=True,
        null=True,
        verbose_name='Аватар'
    )


    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscription(Model):
    """Модель подписок"""

    user = ForeignKey(
        MyUser,
        on_delete=CASCADE,
        related_name="follower",
        verbose_name="Подписчик",
    )
    author = ForeignKey(
        MyUser,
        on_delete=CASCADE,
        related_name="following",
        verbose_name="Автор",
    )

    class Meta:
        ordering = ("-id",)
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            UniqueConstraint(
                fields=["user", "author"], name="unique_follow"
            ),
            CheckConstraint(
                check=~Q(author=F("user")),
                name="check_follower_author",
            ),
        ]

    def __str__(self):
        return f"{self.user} подписался на {self.author}"
