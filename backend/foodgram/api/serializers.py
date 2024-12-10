from django.contrib.auth import get_user_model

from rest_framework.serializers import ModelSerializer

from recipes.models import Ingredient, Recipe, Tag

User = get_user_model()

class IngredientSerializer(ModelSerializer):
    """Сериализатор для вывода ингридиентов."""

    class Meta:
        model = Ingredient
        fields = "__all__"
        read_only_fields = ("__all__",)


class RecipeSerializer(ModelSerializer):
    """Сериализатор для модели Recipe."""
    class Meta:
        model = Recipe
        fields = "id", "name", "image", "cooking_time"
        read_only_fields = ("__all__",)


class TagSerializer(ModelSerializer):
    """Сериализатор для вывода тэгов."""

    class Meta:
        model = Tag
        fields = "__all__"
        read_only_fields = ("__all__",)
