from django.core.management.base import BaseCommand
from pathlib import Path
import json
from apps.sts.models import SearchLocation, LocationType
from decouple import config

ENV = config('SITE_ENV', 'local')


class Command(BaseCommand):
    help = 'Loading initial data from fixtures'
    file_path = Path(__file__).parent.parent.parent.parent.parent / f'data/prod/sts_search_location.json'

    def populate_data(self):
        try:
            with open(self.file_path, 'r') as fp:
                data_json_list = json.loads(fp.read())
                for data_json in data_json_list:
                    sort_order = data_json.pop('sortOrder')
                    data_json['sort_order'] = sort_order
                    location_type = data_json.pop('location_type')
                    if location_type:
                        location_type_obj, created = LocationType.objects.get_or_create(name=location_type)
                        data_json['location_type'] = location_type_obj
                    sl = SearchLocation.objects.create(**data_json)
                    print(f"Search Location {sl.search_location} is added!")
            self.stdout.write(self.style.SUCCESS('Successfully loaded search location data!'))
        except Exception as e:
            print(f"{e}")

    def handle(self, *args, **options):
        # Your custom code goes here
        self.populate_data()
        