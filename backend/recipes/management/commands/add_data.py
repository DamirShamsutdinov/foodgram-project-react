import csv

from django.core.management import BaseCommand

from recipes.models import Ingredients


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open('../data/ingredients.csv', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)
            next(reader)
            for row in reader:
                name, unit = row
                Ingredients.objects.get_or_create(
                    name=name,
                    measurement_unit=unit
                )
            self.stdout.write("Ingredients import successfully")
