from rest_framework.mixins import (
CreateModelMixin,
RetrieveModelMixin,
UpdateModelMixin,
ListModelMixin,
)
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated

from recipes.models import Ingredient, Recipe, Tag
from users.models import Subscribe
from .serializers import (
    IngredientSerializer,
    RecipeSerializer,
    TagSerializer,
    CustomUserSerializer,
    SubscribeSerializer
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
    def subscribe(self, request, **kwargs):
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
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(subscribing__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(pages,
                                         many=True,
                                         context={'request': request})
        return self.get_paginated_response(serializer.data)


class IngredientViewSet(CreateModelMixin,
                   RetrieveModelMixin,
                   UpdateModelMixin,
                   ListModelMixin,
                   GenericViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(CreateModelMixin,
                   RetrieveModelMixin,
                   UpdateModelMixin,
                   ListModelMixin,
                   GenericViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer


class TagViewSet(CreateModelMixin,
                   RetrieveModelMixin,
                   UpdateModelMixin,
                   ListModelMixin,
                   GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
