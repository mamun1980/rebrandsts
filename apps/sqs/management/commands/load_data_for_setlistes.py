from django.core.management.base import BaseCommand
from pathlib import Path
import json
from apps.sqs.models import SetListES
from decouple import config

ENV = config('SITE_ENV', 'local')


class Command(BaseCommand):
    help = 'Loading initial data from fixtures'
    file_path = Path(__file__).parent.parent.parent.parent.parent / f'data/prod/set_list_es.json'

    def populate_data(self):
        try:
            with open(self.file_path, 'r') as fp:
                data_json_list = json.loads(fp.read())
                for data_json in data_json_list:
                    # print(data_json)
                    created_at = data_json.pop('create_date')
                    updated_at = data_json.pop('update_date')
                    data_json['created_at'] = created_at
                    data_json['updated_at'] = updated_at
                    set_list = SetListES.objects.create(**data_json)
                    print(f"set_list_es data {set_list.name} is created")

        except Exception as e:
            print(f"{e}")

    def handle(self, *args, **options):
        # Your custom code goes here
        self.populate_data()
        self.stdout.write(self.style.SUCCESS('Successfully loaded brand location partners property data!'))