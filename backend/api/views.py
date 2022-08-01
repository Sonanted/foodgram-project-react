from django.db.models.aggregates import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.serializers import SetPasswordSerializer
from rest_framework import status, validators, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response

from recipes.models import (
    Favorite, Ingredient, IngredientRecipe, Tag, Recipe, ShoppingCart
)
from users.models import Subscribe, User
from .permissions import IsReadOnly, IsAuthorOrReadOnly, UserPermission
from .serializers import (
    IngredientSerializer, RecipeCutSerializer, RecipeReadSerializer,
    RecipeWriteSerializer, SubscribeSerializer, TagSerializer, UserSerializer
)

SUBSCRIBE_TO_YOURSELF_ERROR = 'Нельзя подписатья на самого себя!'
UNSUBSCRIBE_TO_YOURSELF_ERROR = 'Вы пытаетесь отписаться от самого себя!'
EXIST_SUBSCRIBE_ERROR = 'Вы уже подписаны на этого пользователя!'
NON_EXIST_UNSUBSCRIBE_ERROR = 'Вы и так не подписаны на этого пользователя!'
CART_INGREDIENTS_FORMAT = '\t{name}, {measurement_unit}: {amount}'
SHOPPING_CART_FILENAME = 'shopping_cart.txt'


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (UserPermission,)

    def perform_create(self, serializer):
        password = serializer.validated_data['password']
        user = serializer.save()
        user.set_password(password)
        user.save()

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(self.request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def set_password(self, request):
        serializer = SetPasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        self.request.user.set_password(
            serializer.validated_data['new_password']
        )
        self.request.user.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (IsReadOnly,)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (IsReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name',)
    search_fields = ('name',)


class SubscribeViewSet(viewsets.ModelViewSet):
    serializer_class = SubscribeSerializer
    permission_classes = (IsAuthenticated,)

    def get_author(self, user_id):
        return get_object_or_404(User, id=user_id)

    def list(self, request):
        queryset = User.objects.filter(following__user=self.request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, user_id=None):
        author = self.get_author(user_id)
        if request.user == author:
            raise validators.ValidationError(SUBSCRIBE_TO_YOURSELF_ERROR)

        if Subscribe.objects.filter(user=request.user, author=author).exists():
            raise validators.ValidationError(EXIST_SUBSCRIBE_ERROR)

        Subscribe.objects.create(
            user=request.user,
            author=author
        )
        serializer = SubscribeSerializer(
            author, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, user_id=None):
        author = self.get_author(user_id)
        if request.user == author:
            raise validators.ValidationError(UNSUBSCRIBE_TO_YOURSELF_ERROR)
        if not Subscribe.objects.filter(
            user=request.user, author=author
        ).exists():
            raise validators.ValidationError(NON_EXIST_UNSUBSCRIBE_ERROR)
        Subscribe.objects.filter(
            user=request.user,
            author=author
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = (
        'is_favorited', 'author', 'is_in_shopping_cart', 'tags'
    )

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_intersection_model(self, request, pk, model):
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = RecipeCutSerializer(recipe, context={'request': request})
        if request.method == 'POST':
            model.objects.create(
                user=request.user,
                recipe=recipe
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            model.objects.filter(
                user=request.user,
                recipe=recipe
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True, methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk):
        return self.get_intersection_model(request, pk, Favorite)

    @action(
        detail=True, methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        return self.get_intersection_model(request, pk, ShoppingCart)

    @action(
        detail=False, methods=['get'],
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        text_lines = ['Список покупок\n']
        for item in IngredientRecipe.objects.filter(
            recipe__cart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(
            amount=Sum('total_amount')
        ):
            text_lines.append(
                CART_INGREDIENTS_FORMAT.format(
                    name=item['ingredient__name'],
                    measurement_unit=item['ingredient__measurement_unit'],
                    amount=item['total_amount']
                )
            )
        response_content = '\n'.join(text_lines)
        response = HttpResponse(
            response_content, content_type='text/plain; charset=utf8'
        )
        response['Content-Disposition'] = 'attachment; filename={0}'.format(
            SHOPPING_CART_FILENAME
            )
        return response
