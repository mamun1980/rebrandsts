from django.core.management.base import BaseCommand
from pathlib import Path
import json
from apps.brands.models import Brand, BrandsPartners
from apps.partners.models import Partner, Provider
from apps.property.models import PropertyGroup
from apps.sts.models import Location
from apps.sqs.models import Device, BrandLocationPartnerProperty, BrandLocationPartnerPropertyProvider
from decouple import config

ENV = config('SITE_ENV', 'local')


class Command(BaseCommand):
    help = 'Loading initial data from fixtures'
    file_path = Path(__file__).parent.parent.parent.parent.parent / f'data/prod/sts_brand_locations_defined_kayak_provider.json'

    def populate_data(self):
        # 
        try:
            with open(self.file_path, 'r') as fp:
                data_json_list = json.loads(fp.read())
                for data_json in data_json_list:
                    # print(data_json)
                    id = data_json['id']
                    brand_id = data_json['brand_id']
                    location_id = data_json['location_id']
                    accommodation_type = data_json['accommodation_type']
                    device_type = data_json['device']
                    status = data_json['status']

                    providers = data_json['provider_order_separated'].split(',')

                    brand = Brand.objects.get(id=brand_id)
                    location = Location.objects.get(id=location_id)
                    property_group = PropertyGroup.objects.get(name=accommodation_type)
                    device = Device.objects.get(type=device_type)
                    partner = Partner.objects.get(key='KY')

                    blpp, created = BrandLocationPartnerProperty.objects.get_or_create(
                        id=id,
                        brand=brand,
                        location=location,
                        partner=partner,
                        property_group=property_group,
                        device=device
                    )
                    for i, provider_id in enumerate(providers):
                        provider = Provider.objects.get(id=provider_id)
                        obj, created = BrandLocationPartnerPropertyProvider.objects.update_or_create(
                            loc=blpp,
                            provider=provider,
                            order= i+1,
                            status = status
                        )
                        print(obj)
        except Exception as e:
            print(f"{e}")

    def handle(self, *args, **options):
        # Your custom code goes here
        self.populate_data()
        self.stdout.write(self.style.SUCCESS('Successfully loaded brand location partners property data!'))