from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from slugify import slugify
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
    UniqueConstraint,
    IntegerChoices,
    BooleanField,
    Manager,
)

from core.enums import Limits
from core import help_texts

User = get_user_model()


class PublishedManager(Manager):
    """Пользовательский менеджер модели"""
    def get_queryset(self):
        return super().get_queryset().filter(is_published=Recipe.Status.PUBLISHED)


class Ingredient(Model):
    """ Модель Ингридиент """

    name = CharField(
        max_length=Limits.MAX_LEN_NAME_INGREDIENT_CHARFIELD.value,
        verbose_name = 'Название',
    )
    measurement_unit = CharField(
        max_length=Limits.MAX_LEN_MEASUREMENT_CHARFIELD.value,
        verbose_name = 'Единица измерения',
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
        max_length=Limits.MAX_LEN_NAME_TAG_CHARFIELD.value,
        unique=True,
        help_text=help_texts.HELP_TEXT_NAME_TAG,
        verbose_name = 'Название'
    )
    color = CharField(
        max_length=Limits.MAX_LEN_COLOR_CHARFIELD.value,
        unique=True,
        help_text=help_texts.HELP_TEXT_COLOR_TAG,
        validators=[
            RegexValidator(
                regex='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
                message='Введенное значение не является цветом в формате HEX!'
            ),
        ],
        verbose_name = 'Цветовой HEX-код',
    )
    slug = SlugField(
        max_length=Limits.MAX_LEN_SLUG_TAG.value,
        unique=True,
        blank=True,
        help_text=help_texts.HELP_TEXT_SLUG_TAG,
        verbose_name="Slug",
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


    def save(self,  *args, **kwargs):
        """Перезаписывает поле slug c поля name"""
        self.slug = slugify(self.name)
        return super(Tag, self).save(*args, **kwargs)


class Recipe(Model):
    """ Модель Рецепт """
    class Status(IntegerChoices):
        """Отображает статус публикации"""
        DRAFT = 0, 'Черновик'
        PUBLISHED = 1, 'Опубликовано'

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
    is_published = BooleanField(
        choices=tuple(map(lambda x: (bool(x[0]), x[1]), Status.choices)),
        default=Status.DRAFT,
        verbose_name="Статус",
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

    objects = Manager()
    published = PublishedManager()

    def __str__(self):
        return self.name


class Favourite(Model):
    """Модель избраных рецептов"""

    user = ForeignKey(
        User,
        on_delete=CASCADE,
        related_name='favorites',
        verbose_name='Пользователь',
    )
    recipe = ForeignKey(
        Recipe,
        on_delete=CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            UniqueConstraint(fields=['user', 'recipe'], name='unique_favourite')
        ]

    def __str__(self):
        return f'{self.user} добавил "{self.recipe}" в Избранное'


class ShoppingCart(Model):
    """Модель покупок"""
    user = ForeignKey(
        User,
        on_delete=CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь',
    )
    recipe = ForeignKey(
        Recipe,
        on_delete=CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзина покупок'
        constraints = [
            UniqueConstraint(fields=['user', 'recipe'], name='unique_shopping_cart')
        ]

    def __str__(self):
        return f'{self.user} добавил "{self.recipe}" в Корзину покупок'


class IngredientInRecipe(Model):
    """Модель связи моделей Ingredient и Recipe"""

    recipe = ForeignKey(
        Recipe,
        on_delete= CASCADE,
        related_name='ingredient_list',
        verbose_name='Рецепт',
    )
    ingredient = ForeignKey(
        Ingredient,
        on_delete= CASCADE,
        verbose_name='Ингредиент',
    )
    amount = PositiveSmallIntegerField(
        validators=[MinValueValidator(1, message='Минимальное количество 1!')],
        verbose_name='Количество',
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'

    def __str__(self):
        return (
            f'{self.ingredient.name} ({self.ingredient.measurement_unit}) - {self.amount} '
        )
