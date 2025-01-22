from api.views import (
    CustomUserViewSet,
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet,
)
from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter

app_name = "api"

router = DefaultRouter()
router.register("ingredients", IngredientViewSet, basename="ingredients")
router.register("recipes", RecipeViewSet, basename="recipes")
router.register("tags", TagViewSet, basename="tags")
router.register("users", CustomUserViewSet, basename="users")

urlpatterns = [
    path("", include(router.urls)),
    path("", include("djoser.urls")),
    path(
        "docs/",
        TemplateView.as_view(template_name="docs/redoc.html"),
        name="redoc",
    ),
    path("auth/", include("djoser.urls.authtoken")),
]
