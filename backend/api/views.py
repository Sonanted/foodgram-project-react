from rest_framework import viewsets

from recipes.models import Recipe, Ingredient, Tag
from . import serializers

class RecipeViewSet(viewsets.ModelViewSet):
    pass


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer = serializers.TagSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer = serializers.IngredientSerializer