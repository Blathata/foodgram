from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework.fields import IntegerField, SerializerMethodField
from rest_framework.serializers import ModelSerializer
from rest_framework import status
from drf_extra_fields.fields import Base64ImageField
from rest_framework.exceptions import ValidationError

from recipes.models import Ingredient, Recipe, Tag
from users.models import Subscribe

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    """Сериализатор для работы с моделью User"""
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        """Проверяет пользователей на подписку"""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscribe.objects.filter(user=user, author=obj).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор создание нового пользователя"""
    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
    )


class SubscribeSerializer(CustomUserSerializer):
    """Сериализатор работы с подпиской"""
    recipes_count = SerializerMethodField()
    recipes = SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + (
                "recipes", "recipes_count",
                )

        read_only_fields = ("__all__",)


    def validate(self, data):
        author = self.instance
        user = self.context.get('request').user
        if Subscribe.objects.filter(author=author, user=user).exists():
            raise ValidationError(
                detail='Вы уже подписаны на этого пользователя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        if user == author:
            raise ValidationError(
                detail='Вы не можете подписаться на самого себя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        return data

    def get_recipes_count(self, obj):
        """Показывает общее количество рецептов у каждого автора."""
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipeShortSerializer(recipes, many=True, read_only=True)
        return serializer.data


class RecipeShortSerializer(ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


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
