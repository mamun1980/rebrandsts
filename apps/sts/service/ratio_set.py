from core.service import CoreService
import ast
from django.utils import timezone
import subprocess
from simple_history.utils import bulk_create_with_history, bulk_update_with_history
from apps.sts.models import (Location, Device, BrandLocationDefinedSetsRatio, SearchLocation, RatioSet, PartnerRatio)
from apps.brands.models import Brand
from apps.partners.models import Partner
from apps.property.models import PropertyGroup
from django.contrib.auth import get_user_model
from core.utils import Utils

User = get_user_model()
utils = Utils()


class RatioSetService:
    core_service = CoreService()

    @staticmethod
    def clone_ratio_set(user_id, object_id, brand_ids):

        brand_ids = ast.literal_eval(brand_ids)
        obj = BrandLocationDefinedSetsRatio.objects.get(id=object_id)
        brand_list = Brand.objects.filter(id__in=brand_ids)
        user = get_user_model().objects.get(id=user_id)

        site_key_list = []
        for brand in brand_list:
            if brand.key not in site_key_list:
                site_key_list.append(brand.key)
            Utils.process_brand_locations(user, brand, [obj])

        try:
            django_command = (f'python manage.py generate_ratio_set_json_and_upload_s3 --site_keys'
                              f' {",".join(site_key_list)}')
            subprocess.Popen(
                django_command,
                shell=True,
                text=True,
            )
        except Exception as err:
            print(f'Sub process running err: {err}')

    @staticmethod
    def bulk_clone_ratio_set(user_id, ratio_set_ids, brand_ids):
        brand_ids = ast.literal_eval(brand_ids)
        ratio_set_ids = ast.literal_eval(ratio_set_ids)

        brand_list = Brand.objects.filter(id__in=brand_ids)
        ratio_set_list = BrandLocationDefinedSetsRatio.objects.filter(id__in=ratio_set_ids)
        user = get_user_model().objects.get(id=user_id)

        site_key_list = []
        for brand in brand_list:
            if brand.key not in site_key_list:
                site_key_list.append(brand.key)
            Utils.process_brand_locations(user, brand, ratio_set_list)

        print(f"{'*' * 50}")
        try:
            django_command = (f'python manage.py generate_ratio_set_json_and_upload_s3 --site_keys'
                              f' {",".join(site_key_list)}')
            subprocess.Popen(
                django_command,
                shell=True,
                text=True,
            )
        except Exception as err:
            print(f'Sub process running err: {err}')

    @staticmethod
    def bulk_create(data):
        # print(data)
        ratio_set_id = data.get('ratio_set_id')
        brand_ids = data.get('brand_id_list')
        location_id = data.get('loc_id')
        search_location_id = data.get('search_loc_id')
        property_group_id = data.get('property_group_id')
        user_id = data.get('user_id')
        device_ids = data.get('device_ids')


        ratio_set = RatioSet.objects.get(id=ratio_set_id)
        brand_list = Brand.objects.filter(id__in=brand_ids)
        location = Location.objects.get(id=location_id)
        search_location = SearchLocation.objects.get(id=search_location_id)
        property_group = PropertyGroup.objects.get(id=property_group_id)
        user = get_user_model().objects.get(id=user_id)

        new_ratio_sets = []
        update_ratio_sets = []
        site_key_list = []
        for brand in brand_list:
            devices = Device.objects.filter(id__in=device_ids)
            for device in devices:
                if brand.key not in site_key_list:
                    site_key_list.append(brand.key)
                try:
                    bl_rs = BrandLocationDefinedSetsRatio.objects.get(
                        brand=brand,
                        location=location,
                        search_location=search_location,
                        device=device,
                        property_group=property_group
                    )
                    bl_rs.ratio_set = ratio_set
                    bl_rs.ratio_set_title = ratio_set.ratio_title
                    bl_rs.updated_at = timezone.now()
                    update_ratio_sets.append(bl_rs)
                except BrandLocationDefinedSetsRatio.DoesNotExist:

                    new_ratio_sets.append(
                        BrandLocationDefinedSetsRatio(
                            brand=brand,
                            location=location,
                            search_location=search_location,
                            device=device,
                            property_group=property_group,
                            ratio_set=ratio_set,
                            created_by=user,
                            ratio_set_title=ratio_set.ratio_title,
                            brand_name=brand.name,
                            property_group_name=property_group.name,
                            location_name=f"{location.country} ({location.country_code})",
                            search_location_name=search_location.search_location,
                            device_name=device.type,
                            created_at=timezone.now(),
                            updated_at=timezone.now()
                        )
                    )
        # BrandLocationDefinedSetsRatio.objects.bulk_create(new_ratio_sets)
        for rs in new_ratio_sets:
            rs._change_reason = f"Ratio set created by {user} at {timezone.now()}"
            rs._history_user = user
            rs._history_date = timezone.now()
        bulk_create_with_history(new_ratio_sets, BrandLocationDefinedSetsRatio, batch_size=500)
        # BrandLocationDefinedSetsRatio.objects.bulk_update(
        # update_ratio_sets, ['ratio_set', 'ratio_set_title', 'updated_at'])
        for rs in update_ratio_sets:
            rs._change_reason = f"Ratio set updated by {user} at {timezone.now()}"
            rs._history_user = user
            rs._history_date = timezone.now()
        bulk_update_with_history(update_ratio_sets, BrandLocationDefinedSetsRatio,
                                 ['ratio_set', 'ratio_set_title', 'updated_at'], batch_size=500)

        try:
            django_command = (f'python manage.py generate_ratio_set_json_and_upload_s3 --site_keys'
                              f' {",".join(site_key_list)}')
            subprocess.Popen(
                django_command,
                shell=True,
                text=True,
            )
        except Exception as err:
            print(f'Sub process running err: {err}')

    @staticmethod
    def perform_bulk_update(ratios, selected_object_ids):
        selected_objects = BrandLocationDefinedSetsRatio.objects.filter(id__in=selected_object_ids)
        ratio_set = RatioSet.objects.create(
            title='Bulk Update Ratio'
        )

        for pid, ratio in ratios:
            partner = Partner.objects.get(id=int(pid))

            PartnerRatio.objects.create(
                partner=partner,
                ratio=int(ratio),
                ratioset=ratio_set
            )
        ratio_set.save()

        obj_list = []
        site_key_list = []
        for obj in selected_objects:
            obj.ratio_set = ratio_set
            obj.ratio_set_title = ratio_set.ratio_title
            obj.updated_at = timezone.now()
            obj_list.append(obj)
            if obj.brand.key not in site_key_list:
                site_key_list.append(obj.brand.key)

        # BrandLocationDefinedSetsRatio.objects.bulk_update(obj_list, ['ratio_set', 'ratio_set_title', 'updated_at'])
        for rs in obj_list:
            rs._change_reason = f"Bulk Update Ratio set by {rs.created_by} at {timezone.now()}"
            rs._history_user = rs.created_by
            rs._history_date = timezone.now()
        bulk_update_with_history(obj_list, BrandLocationDefinedSetsRatio,
                                 ['ratio_set', 'ratio_set_title', 'updated_at'], batch_size=500)

        try:
            django_command = (f'python manage.py generate_ratio_set_json_and_upload_s3 --site_keys'
                              f' {",".join(site_key_list)}')
            subprocess.Popen(
                django_command,
                shell=True,
                text=True,
            )
        except Exception as err:
            print(f'Sub process running err: {err}')
