import csv

from django.core.management import BaseCommand
from recipes.models import Ingredients, Tags


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open('./data/ingredients.csv', encoding='utf-8') as _file:
            reader = csv.reader(_file)
            next(reader)
            for row in reader:
                name, unit = row
                Ingredients.objects.get_or_create(
                    name=name,
                    measurement_unit=unit
                )
            self.stdout.write("Ingredients import successfully")

        with open('./data/tags.csv', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                name, color, slug = row
                Tags.objects.get_or_create(
                    name=name,
                    color=color,
                    slug=slug
                )
            self.stdout.write("Tags import successfully")
