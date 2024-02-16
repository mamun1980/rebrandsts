from django.utils import timezone
from datetime import datetime
from django.core.management.base import BaseCommand
from pathlib import Path
import json
from apps.property.models import PropertyType, PartnerPropertyType, PartnerPropertyMapping
from decouple import config

ENV = config('SITE_ENV', 'local')


class Command(BaseCommand):
    help = 'Loading initial data from fixtures'
    property_mapping_file = Path(__file__).parent.parent.parent.parent.parent / f'data/prod/sqs_terms_left.json'

    def generate_property_types_and_mapping(self):
        if self.property_mapping_file.exists():
            try:
                with open(self.property_mapping_file, 'r') as fp:
                    data_json_list = json.loads(fp.read())
                    for data_json in data_json_list:
                        id = data_json.pop('id')
                        brand_type = data_json.pop('brand_type')
                        property_name = data_json.pop('keyword')
                        create_date = data_json.pop('create_date')
                        update_date = data_json.pop('update_date')

                        property_obj = PropertyType.objects.create(
                            id=id,
                            name=property_name,
                            brand_type=brand_type.lower() if brand_type else None,
                            create_date=timezone.now(),
                            update_date=timezone.now()
                        )
                        print(f"Property type {property_obj.name} is created!")
                        for k, v in data_json.items():
                            # partner = Partner.objects.filter(domain_name__icontains=k)
                            if v:
                                partner_property_ids = [int(i) for i in v.split(',') if i != '']
                                for pid in partner_property_ids:
                                    ppt = PartnerPropertyType.objects.get(id=pid)
                                    if ppt:
                                        PartnerPropertyMapping.objects.create(
                                            property_type=property_obj,
                                            partner_property=ppt
                                        )
                    self.stdout.write(self.style.SUCCESS('Successfully generated property mapping data!'))

            except Exception as e:
                self.stdout.write(self.style.ERROR(e))
        else:
            self.stdout.write(self.style.ERROR(f"{self.property_mapping_file} does not exits!"))

    def handle(self, *args, **options):
        # Your custom code goes here
        self.generate_property_types_and_mapping()
