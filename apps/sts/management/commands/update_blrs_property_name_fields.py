import concurrent.futures
from django.core.management.base import BaseCommand
from apps.sts.models import BrandLocationDefinedSetsRatio


class Command(BaseCommand):
    help = 'Updating property_name fields in BrandLocationDefinedRatioSet'

    def update_title_field(self, obj):
        obj.ratio_set_title = obj.ratio_set_short_title
        obj.brand_name = obj.brand.name
        obj.property_group_name = obj.property_group.name
        obj.location_name = f"{obj.location.country} ({obj.location.country_code})"
        obj.search_location_name = obj.search_location.search_location
        obj.device_name = obj.device.type
        return obj

    def handle(self, *args, **options):
        obj_list = list(BrandLocationDefinedSetsRatio.objects.all())
        updated_obj_list = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            for obj in obj_list:
                updated_obj = executor.submit(self.update_title_field, obj)
                updated_obj_list.append(updated_obj)

        obj_list = [updated_obj.result() for updated_obj in updated_obj_list]

        BrandLocationDefinedSetsRatio.objects.bulk_update(
            obj_list,
            ['ratio_set_title', 'brand_name', 'property_group_name', 'location_name', 'search_location_name', 'device_name'],
            100
        )

        self.stdout.write(self.style.SUCCESS('Successfully updated all ratio titles!'))
        
