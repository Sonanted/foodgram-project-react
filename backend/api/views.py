from django.shortcuts import get_object_or_404, get_list_or_404
from djoser.serializers import SetPasswordSerializer
from rest_framework import mixins, status, viewsets, validators
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipes.models import Tag, Recipe, Ingredient
from users.models import User, Subscribe

from .permissions import UserPermission, IsReadOnly
from .serializers import UserSerializer, TagSerializer, IngredientSerializer, SubscribeSerializer

SUBSCRIBE_TO_YOURSELF_ERROR = 'Нельзя подписатья на самого себя!'
UNSUBSCRIBE_TO_YOURSELF_ERROR = 'Вы пытаетесь отписаться от самого себя!'
EXIST_SUBSCRIBE_ERROR = 'Вы уже подписаны на этого пользователя!'
NON_EXIST_UNSUBSCRIBE_ERROR = 'Вы и так не подписаны на этого пользователя!'


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (UserPermission,)

    def perform_create(self, serializer):
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        serializer.save()
        user = get_object_or_404(User, username=username)
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
        if serializer.is_valid():
            self.request.user.set_password(
                serializer.validated_data['new_password']
            )
            self.request.user.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsReadOnly,)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsReadOnly,)


class SubscribeViewSet(viewsets.ModelViewSet):
    serializer_class = SubscribeSerializer
    permission_classes = (IsAuthenticated,)

    def get_author(self, user_id):
        return get_object_or_404(User, id=user_id)

    def list(self, request):
        queryset = User.objects.filter(following__user=self.request.user)
        serializer = SubscribeSerializer(
            queryset,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)

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
