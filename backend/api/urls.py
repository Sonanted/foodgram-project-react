from django.urls import include, path
from rest_framework.routers import DefaultRouter
from djoser.views import TokenCreateView, TokenDestroyView
from .views import UserViewSet, TagViewSet, IngredientViewSet, SubscribeViewSet, RecipeViewSet


api_router = DefaultRouter()
api_router.register('users', UserViewSet, basename='users')
api_router.register('tags', TagViewSet, basename='tags')
api_router.register('ingredients', IngredientViewSet, basename='ingredients')
api_router.register('recipes', RecipeViewSet, basename='recipes')
api_router.register(r'users/(?P<user_id>\d+)/subscribe', SubscribeViewSet, basename='subscribe')
# api_router.register(r'users/subscriptions', SubscriptionsViewSet, basename='subscriptions')

urlpatterns = [
    path('users/subscriptions/', SubscribeViewSet.as_view({'get': 'list'}), name='subscriptions'),
    path('users/<user_id>/subscribe/', SubscribeViewSet.as_view({'post': 'create', 'delete': 'destroy'}), name='subscribe'),
    path('', include(api_router.urls)),
    path('auth/token/login/', TokenCreateView.as_view()),
    path('auth/token/logout/', TokenDestroyView.as_view()),
    
]
