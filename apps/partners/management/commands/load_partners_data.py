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
    file_path = Path(__file__).parent.parent.parent.parent.parent / f'data/prod/partners.json'

    def populate_brands(self):
        if self.file_path.exists():
            partners = {'VRBO': 12, 'BC': 11, 'AB': 16, 'HG': 22, 'TA': 19, 'KY': 23, 'TC': 20, 'EP': 24, 'LT': 25,
                       'HP': 26, 'HAES': 12, 'HAAU': 12, 'HAUK': 12, 'FW': 12, 'HL': 12, 'AT': 12, 'HA': 12}
            try:
                with open(self.file_path, 'r') as fp:
                    data_json_list = json.loads(fp.read())

                    for data_json in data_json_list:
                        date = data_json.pop('date')
                        if date:
                            naive_datetime = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                            aware_datetime = timezone.make_aware(naive_datetime, timezone.get_default_timezone())
                            data_json['date'] = aware_datetime
                        else:
                            data_json['date'] = timezone.now()

                        sort_order = data_json.pop('sortOrder')
                        data_json['sort_order'] = sort_order
                        data_json['feed'] = partners.get(data_json.get('key'))
                        partner = Partner.objects.create(**data_json)
                        print(f"partner {partner.name} created.")
                self.stdout.write(self.style.SUCCESS('Successfully loaded partners data!'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(e))
        else:
            self.stdout.write(self.style.ERROR(f"{self.file_path} does not exits!"))

    def handle(self, *args, **options):
        # Your custom code goes here
        self.populate_brands()
