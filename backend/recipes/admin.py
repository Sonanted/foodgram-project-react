from django.contrib import admin

from .models import Favorite, Recipe, Ingredient, Tag, IngredientRecipe


# Register your models here.
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'color',
        'slug',
    )


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit',
    )


class IngredientInline(admin.TabularInline):
    model = IngredientRecipe


class RecipeAdmin(admin.ModelAdmin):
    inlines = (IngredientInline,)
    list_display = (
        'id',
        'author',
        'name',
        'text',
        'cooking_time',
        'favorites'
    )
    list_filter = ('name',)

    def favorites(self, obj):
        return Favorite.objects.filter(recipe=obj).count()


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
