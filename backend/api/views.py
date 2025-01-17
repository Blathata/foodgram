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
from rest_framework.permissions import AllowAny, SAFE_METHODS, IsAuthenticated

from recipes.models import Ingredient, Recipe, Tag
from .filters import IngredientFilter, RecipeFilter
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from users.models import Subscribe
from .serializers import (
    AvatarSerializer,
    CustomUserSerializer,
    IngredientSerializer,
    RecipeReadSerializer,
    UserSerializer,
    RecipeShortSerializer,
    SubscribeSerializer,
    RecipeWriteSerializer,
    TagSerializer
    )
from .pagination import CustomPagination


User = get_user_model()


class CustomUserViewSet(UserViewSet):
    
    permission_classes = (AllowAny,)
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
        permission_classes=[IsAuthenticated]
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

class UserSelfView(APIView):
    """Получения данных аутентифицированного текущего пользователя."""

    permission_classes = (IsAuthenticated,)
    pagination_class = CustomPagination

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

class UserAvatarView(APIView):
    """Работа с аватаром."""

    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        user = request.user
        serializer = AvatarSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            'avatar': request.build_absolute_uri(user.avatar.url)
        }, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        user = request.user
        user.avatar.delete(save=True)
        return Response(status=status.HTTP_204_NO_CONTENT)

class IngredientViewSet(ModelViewSet):
    """Представление для работы с моделью Ingredient через API"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    http_method_names = ('get',)
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    pagination_class = None
    filterset_class = IngredientFilter


class TagViewSet(ModelViewSet):
    """Представление для работы с моделью Tag через API"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny, )
    http_method_names = ['get']
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    """Представление для работы с моделью Recipe через API"""
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly | IsAdminOrReadOnly,)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        """Добавление информации обьекта запроса"""
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        """Возвращает класс, сериализатора взависимости от метода"""
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer
