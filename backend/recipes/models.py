"""Модуль для создания, настройки и управления моделями пакета `recipe`."""

from django.contrib.auth import get_user_model
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator, 
    RegexValidator
    )
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
    """ Ингридиенты для рецепта. """

    name = CharField(
        max_length=Limits.MAX_LEN_NAME_INGREDIENT.value,
        db_index=True,
        verbose_name = 'Название',
    )
    measurement_unit = CharField(
        max_length=Limits.MAX_LEN_MEASUREMENT_INGREDIENT.value,
        verbose_name = 'Единица измерения',
    )

    class Meta:
        ordering = ["-id"]
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        constraints = (
            UniqueConstraint(
                fields=("name", "measurement_unit"),
                name="unique_ingredient",
            ),
        )

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(Model):
    """ Тэги для рецептов."""
    SLAG_REGEX = r'^[-a-zA-Z0-9_]+$'
    
    name = CharField(
        max_length=Limits.MAX_LEN_NAME_TAG.value,
        unique=True,
        help_text=help_texts.HELP_TEXT_NAME_TAG,
        verbose_name = 'Название'
    )
    slug = SlugField(
        max_length=Limits.MAX_LEN_SLUG_TAG.value,
        unique=True,
        help_text=help_texts.HELP_TEXT_SLUG_TAG,
        verbose_name="Slug",
        validators=[
            RegexValidator(
                regex=SLAG_REGEX,
                message='Используйте только буквы и символы'
            ),
        ]
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        constraints = (
        UniqueConstraint(
            fields=('name', 'slug'),
            name='unique_tags',
            ),
        )

    def __str__(self):
        return self.name


class Recipe(Model):
    """"Модель для рецептов."""
    class Status(IntegerChoices):
        """Отображает статус публикации"""
        DRAFT = 0, 'Черновик'
        PUBLISHED = 1, 'Опубликовано'

    name = CharField(
        verbose_name='Название',
        max_length=Limits.MAX_LEN_NAME_RECIPES.value
    )
    text = TextField(
        verbose_name="Описание блюда",
        max_length=Limits.MAX_LEN_TEXT_RECIPES.value,
    )
    image = ImageField(
        upload_to="photos/%Y/%m/%d/",
        verbose_name='Изображение',
    )
    author = ForeignKey(
        User,
        on_delete=CASCADE,
        related_name="recipes",
        verbose_name="Автор рецепта",
    ) 
    is_published = BooleanField(
        choices=tuple(map(lambda x: (bool(x[0]), x[1]), Status.choices)),
        default=Status.DRAFT,
        verbose_name="Статус",
    )
    cooking_time = PositiveSmallIntegerField(
        validators=(
            MinValueValidator(1, f"Не может быть меньше 1 минут(ы)",),
            MaxValueValidator(1440,f'Не может быть больше 1440 минут(ы)'),
        ),
        verbose_name="Время приготовления (минут)",
    )
    ingredients = ManyToManyField(
        Ingredient,
        related_name='recipes',
        through="RecipeIngredient",
        verbose_name='Ингредиенты'
    )
    tags = ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги'
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    objects = Manager()
    published = PublishedManager()

    def __str__(self):
        return self.name


class RecipeIngredient(Model):
    """Промежуточная модель для связи рецептов с ингредиентами."""

    recipe = ForeignKey(
        Recipe,
        on_delete=CASCADE,
        related_name="ingredient_list",
        verbose_name="Рецепт",
    )
    ingredient = ForeignKey(
        Ingredient,
        on_delete=CASCADE,
        related_name="ingredient_recipe",
        verbose_name="Ингредиент",
    )
    amount = PositiveSmallIntegerField(
        validators=(
            MinValueValidator(1,f"Минимальное количество — 1",),
            MaxValueValidator(100,f'Максимальное количество — 1000'),
        ),
        verbose_name="Количество",
    )

    class Meta:
        ordering = ["-id"]
        verbose_name = "Количество ингредиента"
        verbose_name_plural = "Количество ингредиентов"
        constraints = (
            UniqueConstraint(
                fields=("ingredient", "recipe"),
                name="unique_recipe_ingredient",
            ),
        )

    def __str__(self):
        return f"Рецепт {self.recipe} содержит ингредиент {self.ingredient}"


class Favorite(Model):
    """Избранные рецепты."""

    user = ForeignKey(
        User,
        on_delete=CASCADE,
        related_name="favorite",
        verbose_name="Пользователь",
    )
    recipe = ForeignKey(
        Recipe,
        on_delete=CASCADE,
        related_name="favorite",
        verbose_name="Рецепт",
    )


    class Meta:
        ordering = ["-id"]
        verbose_name = "Избранное"
        verbose_name_plural = "Избранные рецепты"

        constraints = (
            UniqueConstraint(
                fields=("user", "recipe"), 
                name="unique_favorite_recipe",
            ),
        )

    def __str__(self):
        return f'{self.user} добавил "{self.recipe}" в Избранное'
    

class ShoppingList(Model):
    """Модель для хранения списка покупок."""

    user = ForeignKey(
        User,
        on_delete=CASCADE,
        related_name="shopping_list",
        verbose_name="Пользователь",
    )
    recipe = ForeignKey(
        Recipe,
        on_delete=CASCADE,
        related_name="shopping_list",
        verbose_name="Рецепт",
    )

    class Meta:
        verbose_name = "Список покупок"
        verbose_name_plural = "Списки покупок"

        constraints = (
            UniqueConstraint(
                fields=("user", "recipe"),
                name="unique_shopping_list_recipe",
            ),
        )

    def __str__(self):
        return (
            f"{self.user} добавил {self.recipe} в список покупок"
        )
