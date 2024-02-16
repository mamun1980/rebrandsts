from django.core.management.base import BaseCommand
from pathlib import Path
import json
from apps.brands.models import Brand, StaticSiteMapUrl
from decouple import config

ENV = config('SITE_ENV', 'local')


class Command(BaseCommand):
    help = 'Loading initial data from fixtures'
    file_path = Path(__file__).parent.parent.parent.parent.parent / f'data/prod/static_sitemap_urls.json'

    def populate_brands(self):
        try:
            with open(self.file_path, 'r') as fp:
                data_json_list = json.loads(fp.read())
                for data_json in data_json_list:
                    print(data_json)
                    brand = Brand.objects.filter(key=data_json.pop('brand_key'))[0]
                    data_json['brand'] = brand
                    static_sitemaps = data_json.pop('static_sitemap')
                    sitemaps = json.loads(static_sitemaps)
                    data_json['static_sitemap'] = sitemaps
                    StaticSiteMapUrl.objects.create(**data_json)

                # Brand.objects.bulk_create(brand_list)
        except Exception as e:
            print(f"{e}")

    def handle(self, *args, **options):
        # Your custom code goes here
        self.populate_brands()
        self.stdout.write(self.style.SUCCESS('Successfully loaded brands data!'))