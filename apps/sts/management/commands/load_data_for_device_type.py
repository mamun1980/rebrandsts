from django.core.management.base import BaseCommand
from pathlib import Path
import json
from apps.sts.models import Device
from decouple import config

ENV = config('SITE_ENV', 'local')


class Command(BaseCommand):
    help = 'Loading initial data from fixtures'
    file_path = Path(__file__).parent.parent.parent.parent.parent / f'data/prod/device_type.json'

    def populate_data(self):
        try:
            with open(self.file_path, 'r') as fp:
                data_json_list = json.loads(fp.read())
                for data_json in data_json_list:
                    sort_order = data_json.pop('sortOrder')
                    data_json['sort_order'] = sort_order
                    type = data_json.pop('name')
                    data_json['type'] = type
                    created_at = data_json.pop('create_date')
                    data_json['created_at'] = created_at
                    updated_at = data_json.pop('update_date')
                    data_json['updated_at'] = updated_at
                    Device.objects.create(**data_json)
            self.stdout.write(self.style.SUCCESS('Successfully loaded location data!'))
        except Exception as e:
            print(f"{e}")

    def handle(self, *args, **options):
        self.populate_data()
        