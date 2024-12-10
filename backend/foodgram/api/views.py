from rest_framework.mixins import (
CreateModelMixin,
RetrieveModelMixin,
UpdateModelMixin,
ListModelMixin,
)
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from recipes.models import Ingredient, Recipe, Tag
from .serializers import IngredientSerializer, RecipeSerializer, TagSerializer


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
