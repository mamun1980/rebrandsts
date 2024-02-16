from django.utils import timezone
from datetime import datetime

from django.core.management.base import BaseCommand
from django.db import IntegrityError
from pathlib import Path
from django.contrib.auth.models import User
import json
from apps.sts.models import BrandLocationDefinedSetsRatio, RatioGroup, PartnerRatio, RatioSet
from apps.partners.models import Partner
from apps.brands.models import Brand
from apps.property.models import PropertyGroup
from apps.sts.models import Location, SearchLocation, Device
from decouple import config

ENV = config('SITE_ENV', 'local')


class Command(BaseCommand):
    help = 'Loading initial data from fixtures'
    file_path = Path(__file__).parent.parent.parent.parent.parent / f'data/prod/sts_brand_locations_defined_sets_ratio.json'

    def populate_data(self):
        if self.file_path.exists():
            try:
                with open(self.file_path, 'r') as fp:
                    data_json_list = json.loads(fp.read())
                    for data_json in data_json_list:
                        # print(data_json)
                        id = data_json['id']

                        accommodation_type = data_json['accommodation_type']
                        property_group = PropertyGroup.objects.filter(name__icontains=accommodation_type)

                        device_name = data_json['device']
                        device = Device.objects.filter(type__icontains=device_name).first()

                        location_id = data_json['location_id']
                        location = Location.objects.filter(id=int(location_id)).first()

                        brand_id = data_json['brand_id']
                        brand = Brand.objects.filter(id=int(brand_id)).first()

                        search_location_id = data_json['search_location_id']
                        search_location = SearchLocation.objects.filter(id=int(search_location_id)).first()

                        brand_locations_id = data_json['brand_locations_id']
                        # updated_at = data_json['last_updated']
                        status = data_json['status']
                        created_by = data_json['created_by']
                        defined_set_name = data_json['defined_set_name']
                        date = data_json['date']
                        naive_datetime = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                        aware_date = timezone.make_aware(naive_datetime, timezone.get_default_timezone())

                        user = User.objects.first()

                        rg_id = int(data_json['rg_id'])
                        ratio_group = RatioGroup.objects.filter(id=rg_id).first()
                        if not ratio_group:
                            continue

                        try:
                            bdr = BrandLocationDefinedSetsRatio.objects.create(
                                id=id,
                                brand_location_id=brand_locations_id,
                                defined_set_name=defined_set_name if defined_set_name else None,
                                ratio_group=ratio_group,
                                ratio_set=ratio_group.ratio_set if ratio_group.ratio_set else None,
                                # ratio_group_data=ratio_group.get_json_data(),
                                property_group=property_group[0] if property_group.count()>0 else None,
                                device=device,
                                location=location,
                                brand=brand,
                                search_location=search_location,
                                status=int(status),
                                created_by=user,
                                date=aware_date,
                                updated_at=timezone.now()
                            )
                        except IntegrityError as e:
                            bdr = BrandLocationDefinedSetsRatio.objects.get(id=id)
                            bdr.brand_location_id = brand_locations_id
                            bdr.defined_set_name = defined_set_name if defined_set_name else None
                            bdr.ratio_group = ratio_group
                            bdr.ratio_set = ratio_group.ratio_set if ratio_group.ratio_set else None
                            bdr.property_group = property_group[0] if property_group.count()>0 else None
                            bdr.device = device
                            bdr.location = location
                            bdr.brand = brand
                            bdr.search_location = search_location
                            bdr.status = int(status)
                            bdr.created_by = user
                            bdr.date = aware_date
                            bdr.updated_at = timezone.now()
                            bdr.save()
                        print(f"Brand Location Defined Sets Ratio for {bdr.brand.name} location {bdr.location.country} device {bdr.device.type} is added!")

                    self.stdout.write(self.style.SUCCESS('Successfully loaded ratio data!'))

            except Exception as e:
                # import pdb; pdb.set_trace()
                print(f"{e}")
        else:
            self.stdout.write(self.style.ERROR(f"{self.file_path} does not exits!"))

    def handle(self, *args, **options):
        self.populate_data()
        