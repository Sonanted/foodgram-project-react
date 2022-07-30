from rest_framework import serializers
# from rest_framework.validators import UniqueValidator
from django.shortcuts import get_object_or_404
from recipes.models import Tag, Ingredient, Recipe, Favorite, ShoppingCart
from users.models import User, Subscribe


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'password', 'first_name', 'last_name', 'is_subscribed'
        )
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return obj.following.filter(user=request.user).exists()


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class SubscribeSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    # recipes = serializers.SerializerMethodField()
    # recipes_count = serializers.IntegerField(
    #     source='recipes.count',
    #     read_only=True
    # )

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return obj.following.filter(user=request.user).exists()


class FavoriteSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Favorite
        fields = (
            'user',
            'recipe'
        )

    def validate(self, obj):
        user = self.context['request'].user
        recipe = obj['recipe']

        if (self.context.get('request').method == 'GET'
                and user.is_favorited.filter(recipe=recipe).exists()):
            raise serializers.ValidationError(
                'Этот рецепт уже есть в избранном')

        if (self.context.get('request').method == 'DELETE'
                and not user.is_favorited.filter(recipe=recipe).exists()):
            raise serializers.ValidationError(
                'Этого рецепта не было в вашем избранном')

        return obj


class ShoppingCartSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = ShoppingCart
        fields = (
            'user',
            'recipe'
        )

    def validate(self, obj):
        user = self.context['request'].user
        recipe = obj['recipe']

        if (self.context.get('request').method == 'GET'
                and user.is_in_shopping_cart.filter(recipe=recipe).exists()):
            raise serializers.ValidationError(
                'Этот рецепт уже есть в списке покупок')

        if (self.context.get('request').method == 'DELETE' and
                not user.is_in_shopping_cart.filter(recipe=recipe).exists()):
            raise serializers.ValidationError(
                'Этого рецепта не было в вашем списке покупок')

        return obj


class RecipeSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    author = UserSerializer()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited', 'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time')

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return request.user.favorite.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return request.user.cart.filter(recipe=obj).exists()
