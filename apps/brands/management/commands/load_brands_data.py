from django.utils import timezone
from datetime import datetime
from django.core.management.base import BaseCommand
from pathlib import Path
import json
from apps.brands.models import Brand, BrandsPartners
from apps.partners.models import Partner
from decouple import config

ENV = config('SITE_ENV', 'local')


class Command(BaseCommand):
    help = 'Loading initial data from fixtures'
    file_path = Path(__file__).parent.parent.parent.parent.parent / f'data/prod/brands.json'

    def populate_brands(self):
        if self.file_path.exists():
            try:
                with open(self.file_path, 'r') as fp:
                    data_json_list = json.loads(fp.read())
                    for data_json in data_json_list:
                        partners = data_json.pop('partners')
                        sort_order = data_json.pop('sortOrder')
                        data_json['sort_order'] = sort_order

                        date = data_json.pop('date')
                        naive_datetime = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                        aware_datetime = timezone.make_aware(naive_datetime, timezone.get_default_timezone())

                        data_json['date'] = aware_datetime

                        is_exist = Brand.objects.filter(name=data_json['name']).exists()
                        if is_exist:
                            brand = Brand.objects.get(name=data_json['name'])
                        else:
                            brand = Brand.objects.create(**data_json)
                        if partners:
                            for partner in partners.split(','):
                                partner, is_created = Partner.objects.get_or_create(id=int(partner))
                                if partner:
                                    bp, created = BrandsPartners.objects.get_or_create(brand=brand, partner=partner)
                                    bp.save()
                        print(f"Brand {brand.name} is created!")
                self.stdout.write(self.style.SUCCESS('Successfully loaded brands data!'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(e))
        else:
            self.stdout.write(self.style.ERROR(f"{self.file_path} does not exits!"))

    def handle(self, *args, **options):
        # Your custom code goes here
        self.populate_brands()
