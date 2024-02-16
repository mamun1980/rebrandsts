from django.core.management.base import BaseCommand
from pathlib import Path
import json
from apps.sts.models import Location
from decouple import config

ENV = config('SITE_ENV', 'local')


class Command(BaseCommand):
    help = 'Loading initial data from fixtures'
    file_path = Path(__file__).parent.parent.parent.parent.parent / f'data/prod/sts_locations.json'

    def populate_data(self):
        continent = ['NA', 'EU', 'ROW']
        try:
            with open(self.file_path, 'r') as fp:
                data_json_list = json.loads(fp.read())
                for data_json in data_json_list:
                    cc = data_json['country_code']
                    if cc in continent:
                        location_type = 'continent'
                    else:
                        location_type = 'country'
                    data_json['location_type'] = location_type

                    loc = Location.objects.create(**data_json)
                    print(f"Location {loc.country} is added!")
            self.stdout.write(self.style.SUCCESS('Successfully loaded location data!'))
        except Exception as e:
            print(f"{e}")

    def handle(self, *args, **options):
        self.populate_data()
        