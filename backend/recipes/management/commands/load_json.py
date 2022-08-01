import json
import os

from django.core.management import BaseCommand

from foodgram.settings import BASE_DIR
from recipes.models import Ingredient

JSON_DATA_FILE = os.path.join(BASE_DIR, 'data/ingredients.json')


class Command(BaseCommand):

    def handle(self, *args, **options):
        ingredients = open(JSON_DATA_FILE, 'r', encoding='utf-8')
        for item in json.load(ingredients):
            Ingredient.objects.create(
                name=item['name'],
                measurement_unit=item['measurement_unit']
            )
