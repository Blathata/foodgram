from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from .views import (
    IngredientViewSet, 
    RecipeViewSet, 
    TagViewSet, 
    CustomUserViewSet,
    UserAvatarView,
    UserSelfView
    )


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
    path(
        'users/me/avatar/', UserAvatarView.as_view(), name='user-avatar'
    ),
    path(
        'users/me/', UserSelfView.as_view(), name='user-self'
    ),
    # path(
    #     'users/set_password/',
    #     djoser_views.UserViewSet.as_view({'post': 'set_password'}),
    #     name='user-set-password'
    # ),
    # path('s/<str:short_id>/', redirect_to_recipe, name='short-link-redirect'),
]
