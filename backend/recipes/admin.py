from django.contrib.admin import register, ModelAdmin
from django.contrib import messages
from django.contrib.admin import action, display

from .models import (
    Ingredient,
    Recipe,
    Tag,
    ShoppingCart,
    Favourite,
    IngredientInRecipe,
    )


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    list_display = ('name',
                    'id',
                    'author',
                    'in_favorites',
                    'is_published'
                    )
    ordering = ('name',)
    list_editable = ('is_published',)
    readonly_fields = ('in_favorites',)
    list_filter = ('tags', 'is_published')
    list_per_page = 10
    actions = ('set_published', 'set_draft')
    search_fields = ('name',)


    @display(description='В избранных')
    def in_favorites(self, obj):
        return obj.favorites.count()

    @action(description="Опубликовать выбранные рецепты")
    def set_published(self, request, queryset):
        count = queryset.update(is_published=Recipe.Status.PUBLISHED)
        self.message_user(request, f"Изменено {count} записей.")

    @action(description="Снять с публикации выбранные рецепты")
    def set_draft(self, request, queryset):
        count = queryset.update(is_published=Recipe.Status.DRAFT)
        self.message_user(
            request, f"{count} записей сняты с публикации!",
            messages.WARNING,
            )


@register(Ingredient)
class IngredientAdmin(ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    list_filter = ('name',)


@register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ('name', 'color', 'slug',)


@register(ShoppingCart)
class ShoppingCartAdmin(ModelAdmin):
    list_display = ('user', 'recipe',)


@register(Favourite)
class FavouriteAdmin(ModelAdmin):
    list_display = ('user', 'recipe',)


@register(IngredientInRecipe)
class IngredientInRecipe(ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount',)
