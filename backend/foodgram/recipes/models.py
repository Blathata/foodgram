from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db.models import (
    CASCADE,
    SET_NULL,
    CharField,
    SlugField,
    ForeignKey,
    ImageField,
    ManyToManyField,
    Model,
    PositiveSmallIntegerField,
    TextField,
    UniqueConstraint

)

from core.enums import Limits


User = get_user_model()


class Ingredient(Model):
    """ Модель Ингридиент """

    name = CharField(
        'Название',
        max_length=Limits.MAX_LEN_NAME_INGREDIENT_CHARFIELD.value
    )
    measurement_unit = CharField(
        'Единица измерения',
        max_length=Limits.MAX_LEN_MEASUREMENT_CHARFIELD.value
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(Model):
    """ Модель Тэг """

    name = CharField(
        'Название',
        unique=True,
        max_length=Limits.MAX_LEN_NAME_TAG_CHARFIELD.value
    )
    color = CharField(
        'Цветовой HEX-код',
        unique=True,
        max_length=Limits.MAX_LEN_COLOR_CHARFIELD.value,
        validators=[
            RegexValidator(
                regex='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
                message='Введенное значение не является цветом в формате HEX!'
            )
        ]
    )
    slug = SlugField(
        'Уникальный слаг',
        unique=True,
        max_length=200
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(Model):
    """ Модель Рецепт """

    name = CharField(
        'Название',
        max_length=Limits.MAX_LEN_NAME_RECIPES_CHARFIELD.value
    )
    author = ForeignKey(
        User,
        related_name='recipes',
        on_delete=SET_NULL,
        null=True,
        verbose_name='Автор',
    )
    text = TextField(
        verbose_name="Описание блюда",
        max_length=Limits.MAX_LEN_TEXT_TEXTFIELD.value,
    )
    image = ImageField(
        upload_to="photos/%Y/%m/%d/",
        default=None,
        blank=True,
        null=True,
        verbose_name='Изображение',
    )
    cooking_time = PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[
            MinValueValidator(1, message='Минимальное значение 1!')
            ]
    )
    ingredients = ManyToManyField(
        Ingredient,
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    tags = ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги'
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class Favourite(Model):
    """Модель избаных рецептов"""
    pass


class ShoppingCart(Model):
    """Модель покупок"""
    pass


class IngredientInRecipe(Model):
    """Модель связи моделей Ingredient и Recipe"""
    pass
