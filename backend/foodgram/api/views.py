from rest_framework.mixins import (
CreateModelMixin,
RetrieveModelMixin,
UpdateModelMixin,
ListModelMixin,
)
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from django.core.handlers.wsgi import WSGIRequest
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet, ReadOnlyModelViewSet
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated

from recipes.models import Ingredient, Recipe, Tag
from .filters import IngredientFilter, RecipeFilter
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from users.models import Subscribe
from .serializers import (
    CustomUserSerializer,
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeShortSerializer,
    SubscribeSerializer,
    RecipeWriteSerializer,
    TagSerializer
    )
from .pagination import CustomPagination


User = get_user_model()


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = CustomPagination

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request: WSGIRequest, **kwargs)-> Response:
        """Создаёт/удалет связь между пользователями."""
        user = request.user
        author_id = self.kwargs.get('id')
        author = get_object_or_404(User, id=author_id)

        if request.method == 'POST':
            serializer = SubscribeSerializer(author,
                                             data=request.data,
                                             context={"request": request})
            serializer.is_valid(raise_exception=True)
            Subscribe.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            subscription = get_object_or_404(Subscribe,
                                             user=user,
                                             author=author)
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]aa
    )
    def subscriptions(self, request: WSGIRequest)-> Response:
        """Список подписок пользоваетеля."""
        user = request.user
        queryset = User.objects.filter(subscribing__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(pages,
                                         many=True,
                                         context={'request': request})
        return self.get_paginated_response(serializer.data)


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.published.all()
    permission_classes = (IsAuthorOrReadOnly | IsAdminOrReadOnly,)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer
