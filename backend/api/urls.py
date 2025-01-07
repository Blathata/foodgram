from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from .views import IngredientViewSet, RecipeViewSet, TagViewSet, CustomUserViewSet

app_name = 'api'

router = DefaultRouter()

router.register('ingredients', IngredientViewSet,)
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet,)
router.register("users", CustomUserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
