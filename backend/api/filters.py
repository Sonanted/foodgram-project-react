from django_filters import rest_framework as django_filter
from recipes.models import Recipe
from rest_framework import filters
from users.models import User


class RecipeFilter(django_filter.FilterSet):
    author = django_filter.ModelChoiceFilter(queryset=User.objects.all())
    tags = django_filter.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = django_filter.BooleanFilter(method='get_is_favorites')
    is_in_shopping_cart = django_filter.BooleanFilter(
        method='get_is_in_shopping_list')

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorites(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def get_is_in_shopping_list(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(carts__user=self.request.user)
        return queryset.all()


class IngredientFilter(filters.SearchFilter):
    search_param = 'name'