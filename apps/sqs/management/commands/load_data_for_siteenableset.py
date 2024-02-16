from django.core.management.base import BaseCommand
from pathlib import Path
import json
from apps.sqs.models import SetList, SiteEnableSets
from apps.brands.models import Brand
from decouple import config

ENV = config('SITE_ENV', 'local')


class Command(BaseCommand):
    help = 'Loading initial data from fixtures'
    file_path = Path(__file__).parent.parent.parent.parent.parent / f'data/prod/site_enable_sets.json'

    def populate_data(self):
        try:
            with open(self.file_path, 'r') as fp:
                data_json_list = json.loads(fp.read())
                for data_json in data_json_list:
                    print(data_json)
                    created_at = data_json.pop('create_date')
                    updated_at = data_json.pop('update_date')
                    data_json['created_at'] = created_at
                    data_json['updated_at'] = updated_at
                    set_list_id = int(data_json.pop('set_list_id'))
                    set_list = SetList.objects.get(id=set_list_id)
                    data_json['set_list'] = set_list
                    brand_key = data_json.pop('site')
                    try:
                        data_json['site'] = Brand.objects.get(key=brand_key.upper())
                    except Brand.DoesNotExist:
                        continue
                    site_enable_set = SiteEnableSets.objects.create(**data_json)
                    print(f"site_enable_set data {site_enable_set.set_list.name} for site {site_enable_set.site.name } is created")

        except Exception as e:
            print(f"{e}")

    def handle(self, *args, **options):
        # Your custom code goes here
        self.populate_data()
        self.stdout.write(self.style.SUCCESS('Successfully loaded brand location partners property data!'))