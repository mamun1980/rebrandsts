from django.utils import timezone
from datetime import datetime
from django.core.management.base import BaseCommand
from pathlib import Path
import json

from apps.property.models import PartnerPropertyType
from apps.partners.models import Partner
from decouple import config

ENV = config('SITE_ENV', 'local')


class Command(BaseCommand):
    help = 'Loading initial data from fixtures'
    file_path = Path(__file__).parent.parent.parent.parent.parent / f'data/prod/property_types_by_partners.json'

    def populate_partner_property_data(self):
        if self.file_path.exists():
            try:
                with open(self.file_path, 'r') as fp:
                    data_json_list = json.loads(fp.read())
                    for data_json in data_json_list:
                        partner_name = data_json['brand_type'].lower()
                        property_name = data_json['keyword']

                        id = data_json['id']
                        partner = Partner.objects.filter(domain_name__icontains=partner_name)
                        if partner:
                            obj = PartnerPropertyType.objects.create(
                                id=id,
                                name=property_name,
                                partner=partner[0],
                                create_date=timezone.now(),
                                update_date=timezone.now()
                            )
                            print(f"Partner Property Type {obj.name} is created!")
                self.stdout.write(self.style.SUCCESS('Successfully generated property mapping data!'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(e))
        else:
            self.stdout.write(self.style.ERROR(f"{self.file_path} does not exits!"))

    def handle(self, *args, **options):
        # Your custom code goes here
        self.populate_partner_property_data()
