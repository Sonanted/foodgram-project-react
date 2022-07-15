from django.core.validators import MinValueValidator
from django.db import models

from django.contrib.auth import get_user_model
User = get_user_model()

class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )
    color = models.CharField(
        max_length=7,
        blank=True,
        null=True
    )
    slug = models.SlugField(
        max_length=200,
        blank=True,
        null=True
    )


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200
    )
    measurement_unit = models.CharField(
        max_length=200
    )


class Recipe(models.Model):
    tags = models.ManyToManyField(
        to=Tag
    )
    author = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    ingredients = models.ManyToManyField(
        to=Ingredient
    )
    name = models.CharField(
        max_length=200
    )
    image = models.ImageField()
    text = models.TextField()
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)]
    )


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(
        to=Recipe,
        on_delete=models.CASCADE,
        related_name='used_in'
        )
    ingredient = models.ForeignKey(
        to=Ingredient,
        on_delete=models.CASCADE,
        related_name='used_in'
    )
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)]
    )


class Follow(models.Model):
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='following'
    )


class Favorite(models.Model):
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        to=Recipe,
        on_delete=models.CASCADE
    )


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        to=Recipe,
        on_delete=models.CASCADE
    )
