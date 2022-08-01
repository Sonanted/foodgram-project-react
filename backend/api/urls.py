from django.urls import include, path
from djoser.views import TokenCreateView, TokenDestroyView
from rest_framework.routers import DefaultRouter

from .views import (
    IngredientViewSet, RecipeViewSet, SubscribeViewSet, TagViewSet, UserViewSet
)


api_router = DefaultRouter()
api_router.register('users', UserViewSet, basename='users')
api_router.register('tags', TagViewSet, basename='tags')
api_router.register('ingredients', IngredientViewSet, basename='ingredients')
api_router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path(
        'users/subscriptions/',
        SubscribeViewSet.as_view({'get': 'list'}),
        name='subscriptions'
    ),
    path(
        'users/<int:user_id>/subscribe/',
        SubscribeViewSet.as_view({'post': 'create', 'delete': 'destroy'}),
        name='subscribe'
    ),
    path('', include(api_router.urls)),
    path(
        'auth/token/login/', TokenCreateView.as_view(),
        name='token-create'
    ),
    path(
        'auth/token/logout/', TokenDestroyView.as_view(),
        name='token-destroy'
    ),
]
