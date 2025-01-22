import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework.serializers import (
    ImageField,
    ModelSerializer,
    SerializerMethodField,
    ReadOnlyField,
    IntegerField,
    PrimaryKeyRelatedField,
    ValidationError,
)
from djoser.serializers import UserCreateSerializer, UserSerializer

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingList,
    Tag,
)
from users.models import Subscription
from core import constants

from core.utils import get_serializer_method_field_value

User = get_user_model()


class Base64ImageField(ImageField):

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            img_format, img_str = data.split(";base64,")
            ext = img_format.split("/")[-1]
            data = ContentFile(base64.b64decode(img_str), name="image." + ext)
        return super().to_internal_value(data)


class CustomUserSerializer(UserSerializer):
    """Сериализатор для работы с информацией о пользователях."""

    is_subscribed = SerializerMethodField()
    avatar = Base64ImageField(allow_null=True, required=False)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "avatar",
        )

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False
        return request.user.follower.filter(author=obj).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор создание нового пользователя"""

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "password",
        )


class AvatarSerializer(ModelSerializer):
    avatar = Base64ImageField(allow_null=True)

    class Meta:
        model = User
        fields = ("avatar",)


class TagSerializer(ModelSerializer):

    class Meta:
        model = Tag
        fields = ("id", "name", "slug")


class IngredientSerializer(ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class RecipeIngredientSerializer(ModelSerializer):

    id = ReadOnlyField(source="ingredient.id")
    name = ReadOnlyField(source="ingredient.name")
    measurement_unit = ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeIngredientWriteSerializer(ModelSerializer):
    id = IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ("id", "amount")


class RecipeReadSerializer(ModelSerializer):

    tags = TagSerializer(many=True)
    author = CustomUserSerializer()
    ingredients = RecipeIngredientSerializer(
        source="ingredient_list", many=True
    )
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_is_favorited(self, recipe):
        return get_serializer_method_field_value(
            self.context, Favorite, recipe, "user_id", "recipe"
        )

    def get_is_in_shopping_cart(self, recipe):
        return get_serializer_method_field_value(
            self.context, ShoppingList, recipe, "user_id", "recipe"
        )


class RecipeWriteSerializer(ModelSerializer):
    tags = PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        label="Tags",
    )
    ingredients = RecipeIngredientWriteSerializer(
        many=True,
        label="Ingredients",
    )
    image = Base64ImageField(allow_null=True, label="images")

    class Meta:
        model = Recipe
        fields = (
            "tags",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def validate_tags(self, value):
        if not value:
            raise ValidationError("Добавьте тег")

        if len(value) != len(set(value)):
            raise ValidationError("Теги должны быть уникальными")

        return value

    def validate_ingredients(self, value):
        if not value:
            raise ValidationError("Добавьте ингредиент")

        ingredient_ids = [ingredient["id"] for ingredient in value]
        existing_ingredient_count = Ingredient.objects.filter(
            id__in=ingredient_ids
        ).count()
        if existing_ingredient_count != len(ingredient_ids):
            raise ValidationError(
                "Один или несколько ингредиентов не существуют"
            )

        return value

    def validate_image(self, value):
        if not value:
            raise ValidationError(
                "Вы должны добавить изображение для рецепта"
            )
        return value

    def to_representation(self, instance):
        serializer = RecipeReadSerializer(
            instance, context={"request": self.context.get("request")}
        )
        return serializer.data

    def create_tags(self, tags, recipe):
        recipe.tags.set(tags)

    def create_ingredients(self, ingredients, recipe):
        for ingredient_data in ingredients:
            ingredient_id = ingredient_data["id"]
            ingredient = Ingredient.objects.get(pk=ingredient_id)
            amount = ingredient_data["amount"]
            RecipeIngredient.objects.create(
                ingredient=ingredient, recipe=recipe, amount=amount
            )

    def create(self, validated_data):
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        user = self.context.get("request").user
        recipe = Recipe.objects.create(**validated_data, author=user)
        self.create_tags(tags, recipe)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.get("tags")
        if tags is None:
            raise ValidationError({"tags": "Добавьте тег"})
        ingredients = validated_data.get("ingredients")
        if ingredients is None:
            raise ValidationError(
                {"ingredients": "Добавьте ингридиент"}
            )
        instance.tags.set(tags)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        self.create_ingredients(validated_data.pop("ingredients"), instance)
        return super().update(instance, validated_data)


class ShortRecipeSerializer(ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class SubscriberCreateSerializer(ModelSerializer):

    class Meta:
        model = Subscription
        fields = ("id", "user", "author")
        read_only_fields = ("id",)

    def validate(self, data):
        request = self.context.get("request")
        user = request.user
        author = data.get("author")

        if user == author:
            raise ValidationError(
                "Вы не можете подписаться на себя"
            )
        if Subscription.objects.filter(user=user, author=author).exists():
            raise ValidationError(
                "Вы уже подписаны на этого пользователя"
            )

        return data

    def create(self, validated_data):
        return Subscription.objects.create(**validated_data)


class SubscriberDetailSerializer(ModelSerializer):
    email = ReadOnlyField(source="author.email")
    id = ReadOnlyField(source="author.id")
    username = ReadOnlyField(source="author.username")
    first_name = ReadOnlyField(source="author.first_name")
    last_name = ReadOnlyField(source="author.last_name")
    is_subscribed = SerializerMethodField()
    recipes = SerializerMethodField()
    recipes_count = IntegerField(read_only=True)
    avatar = Base64ImageField(source="author.avatar")

    class Meta:
        model = Subscription
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
            "avatar",
        )

    def get_is_subscribed(self, obj):
        user = self.context.get("request").user
        return Subscription.objects.filter(
            author=obj.author, user=user
        ).exists()

    def get_recipes(self, obj):
        request = self.context.get("request")
        limit = request.GET.get("recipes_limit", constants.PAGE_SIZE)
        limit = (
            int(limit)
            if isinstance(limit, str) and limit.isdigit()
            else constants.PAGE_SIZE
        )

        return ShortRecipeSerializer(
            Recipe.objects.filter(author=obj.author)[:limit],
            many=True,
            context={"request": request},
        ).data


class ShoppingCartCreateSerializer(ModelSerializer):
    class Meta:
        model = ShoppingList
        fields = ("id", "user", "recipe")
        read_only_fields = ("id",)

    def validate(self, data):
        user = self.context["request"].user
        recipe = data.get("recipe")

        if ShoppingList.objects.filter(user=user, recipe=recipe).exists():
            raise ValidationError(
                f'Рецепт "{recipe.name}" уже добавлен в список покупок.'
            )

        return data

    def create(self, validated_data):
        return ShoppingList.objects.create(**validated_data)


class FavoriteCreateSerializer(ModelSerializer):
    class Meta:
        model = Favorite
        fields = ("id", "user", "recipe")
        read_only_fields = ("id",)

    def validate(self, data):
        user = self.context["request"].user
        recipe = data.get("recipe")

        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            raise ValidationError(
                f'Рецепт "{recipe.name}" уже добавлен в избранное.'
            )

        return data

    def create(self, validated_data):
        return Favorite.objects.create(**validated_data)
