import csv
from django.core.management.base import BaseCommand
from market.models import ZipCode

### Command to load ZIP codes from a CSV file into the database
### FarmtoFork_project/farmtofork_root/market/management/commands/loadzipcodes.py
### python manage.py loadzipcodes

class Command(BaseCommand):
    help = 'Load ZIP codes from a CSV file'

    def handle(self, *args, **kwargs):
        with open('market/data/zipcodes/uszips.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                ZipCode.objects.get_or_create(
                    code=row['zip'],
                    city=row['city'],
                    state=row['state_id'],
                    latitude=row['lat'],
                    longitude=row['lng'],
                )
        self.stdout.write(self.style.SUCCESS('ZIP codes loaded successfully'))