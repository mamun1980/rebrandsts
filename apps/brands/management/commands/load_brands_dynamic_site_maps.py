from django.core.management.base import BaseCommand
from pathlib import Path
import json
from apps.brands.models import DynamicSiteMapUrl
from decouple import config

ENV = config('SITE_ENV', 'local')


class Command(BaseCommand):
    help = 'Loading initial data from fixtures'
    file_path = Path(__file__).parent.parent.parent.parent.parent / f'data/prod/dynamic_sitemap_urls.json'

    def populate_brands(self):
        try:
            with open(self.file_path, 'r') as fp:
                data_json_list = json.loads(fp.read())
                for data_json in data_json_list:
                    print(data_json)
                    DynamicSiteMapUrl.objects.create(**data_json)
        except Exception as e:
            print(f"{e}")

    def handle(self, *args, **options):
        # Your custom code goes here
        self.populate_brands()
        self.stdout.write(self.style.SUCCESS('Successfully loaded brands data!'))