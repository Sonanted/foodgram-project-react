from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

api_v1 = DefaultRouter()

api_v1.register(r'tags', views.TagViewSet, basename='tags')
api_v1.register(r'ingredients', views.IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('v1/', include(api_v1.urls)),
    path('v1/', include('djoser.urls.jwt')),
]