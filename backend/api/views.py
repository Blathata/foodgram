from django.contrib.auth import get_user_model
from django.db.models import Count, Sum
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_GET
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework.viewsets import (
    ModelViewSet,
    ReadOnlyModelViewSet,
)
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)
from rest_framework.decorators import action
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.reverse import reverse

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import CustomLimitPagination
from api.permissions import IsAdminAuthorOrReadOnly
from api.serializer import (
    AvatarSerializer,
    CustomUserSerializer,
    IngredientSerializer,
    FavoriteCreateSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    ShoppingCartCreateSerializer,
    ShortRecipeSerializer,
    SubscriberCreateSerializer,
    SubscriberDetailSerializer,
    TagSerializer,
)
from recipes.models import (
    Ingredient,
    Recipe,
    RecipeIngredient,
    Tag,
)

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    """Работает с пользователями."""
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = CustomLimitPagination

    @action(["get"], detail=False, permission_classes=(IsAuthenticated,))
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        return self.retrieve(request, *args, **kwargs)

    @action(
        ["put"],
        detail=False,
        permission_classes=(IsAdminAuthorOrReadOnly,),
        url_path="me/avatar",
    )
    def avatar(self, request, *args, **kwargs):
        serializer = AvatarSerializer(
            instance=request.user,
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @avatar.mapping.delete
    def delete_avatar(self, request, *args, **kwargs):
        user = self.request.user
        user.avatar.delete()
        return Response(status=HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=("GET",),
        permission_classes=(IsAuthenticated,),
        url_path="subscriptions",
        url_name="subscriptions",
    )
    def subscriptions(self, request):
        user = request.user
        queryset = (
            user.follower
            .select_related("author")
            .prefetch_related("author__recipes")
            .annotate(recipes_count=Count("author__recipes"))
        )
        pages = self.paginate_queryset(queryset)
        serializer = SubscriberDetailSerializer(
            pages, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=("post", "delete"),
    )
    def subscribe(self, request, id):
        user = request.user

        if self.request.method == "POST":
            author = get_object_or_404(User, id=id)
            data = {"user": user.id, "author": author.id}
            serializer = SubscriberCreateSerializer(
                data=data, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            queryset = (
                user.follower
                .annotate(recipes_count=Count("author__recipes"))
                .first()
            )
            serializer = SubscriberDetailSerializer(
                queryset, context={"request": request}
            )
            return Response(
                serializer.data, status=HTTP_201_CREATED
            )

        elif request.method == "DELETE":
            if not User.objects.filter(id=id).exists():
                return Response(
                    {"errors": "Пользователь с данным ID не найден"},
                    status=HTTP_404_NOT_FOUND,
                )
            deleted_count, _ = user.follower.filter(
                user=user, author_id=id
            ).delete()
            if deleted_count == 0:
                return Response(
                    {"errors": "Вы не подписаны на данного пользователя"},
                    status=HTTP_400_BAD_REQUEST,
                )
            return Response(status=HTTP_204_NO_CONTENT)


class TagViewSet(ReadOnlyModelViewSet):
    """Работает с тэгами."""
    permission_classes = (IsAdminAuthorOrReadOnly,)
    pagination_class = None
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(ReadOnlyModelViewSet):
    """Работет с игридиентами."""
    permission_classes = (AllowAny,)
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    search_fields = ("^name",)


class RecipeViewSet(ModelViewSet):
    """Работает с рецептами."""
    permission_classes = (IsAdminAuthorOrReadOnly,)
    pagination_class = CustomLimitPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    queryset = Recipe.objects.select_related("author").prefetch_related(
        "tags", "ingredients"
    )

    def get_serializer_class(self):
        if self.action in ("list", "retrieve", "get-link"):
            return RecipeReadSerializer
        return RecipeWriteSerializer

    @action(
        detail=True,
        methods=("GET",),
        permission_classes=(AllowAny,),
        url_path="get-link",
        url_name="get-link",
    )
    def get_link(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        reverse_link = reverse("short_url", args=[recipe.pk])
        return Response(
            {"short-link": request.build_absolute_uri(reverse_link)},
            status=HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=("POST", "DELETE",),
        permission_classes=(IsAuthenticated,),
        url_path="shopping_cart",
        url_name="shopping_cart",
    )
    def shopping_cart(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)

        if request.method == "POST":
            data = {"user": user.id, "recipe": recipe.id}
            serializer = ShoppingCartCreateSerializer(
                data=data, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            serializer = ShortRecipeSerializer(
                recipe, context={"request": request}
            )
            return Response(
                serializer.data, status=HTTP_201_CREATED
            )

        elif request.method == "DELETE":
            deleted_count, _ = user.shopping_list.filter(
                user=user, recipe=recipe
            ).delete()
            if deleted_count == 0:
                return Response(
                    {"detail": f'"{recipe.name}" отсутствует в покупках.'},
                    status=HTTP_400_BAD_REQUEST,
                )
            return Response(status=HTTP_204_NO_CONTENT)

    @staticmethod
    def shopping_list_to_txt(ingredients):
        return "\n".join(
            f'{ingredient["ingredient__name"]} - {ingredient["sum"]} '
            f'({ingredient["ingredient__measurement_unit"]})'
            for ingredient in ingredients
        )

    @action(
        detail=False,
        methods=("GET",),
        permission_classes=(IsAuthenticated,),
        url_path="download_shopping_cart",
        url_name="download_shopping_cart",
    )
    def download_shopping_cart(self, request):
        ingredients = (
            RecipeIngredient.objects.filter(
                recipe__shopping_list__user=request.user
            )
            .values("ingredient__name", "ingredient__measurement_unit")
            .annotate(sum=Sum("amount"))
        )
        shopping_list = self.shopping_list_to_txt(ingredients)
        return HttpResponse(shopping_list, content_type="text/plain")

    @action(
        detail=True,
        methods=("POST", "DELETE"),
        permission_classes=(IsAuthenticated,),
        url_path="favorite",
        url_name="favorite",
    )
    def favorite(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)

        if request.method == "POST":
            data = {"user": user.id, "recipe": recipe.id}
            serializer = FavoriteCreateSerializer(
                data=data, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            serializer = ShortRecipeSerializer(
                recipe, context={"request": request}
            )
            return Response(
                serializer.data, status=HTTP_201_CREATED
            )

        elif request.method == "DELETE":
            deleted_count, _ = user.favorite.filter(
                user=user, recipe=recipe
            ).delete()
            if deleted_count == 0:
                return Response(
                    {"detail": f'Рецепт "{recipe.name}" не в избранном.'},
                    status=HTTP_400_BAD_REQUEST,
                )
            return Response(status=HTTP_204_NO_CONTENT)


@require_GET
def short_url(request, pk):
    if not Recipe.objects.filter(pk=pk).exists():
        raise Http404(f'Рецепт с id "{pk}" не существует.')

    return redirect(f"/recipes/{pk}/")
