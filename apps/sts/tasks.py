import subprocess

# from celery import shared_task
from django.utils import timezone
import json
import boto3
from datetime import datetime
from django.conf import settings
from apps.brands.models import Brand
from apps.sts.models import (Location, Device, BrandLocationDefinedSetsRatio, PredictedRatio, SearchLocation, RatioSet,
                             PartnerRatio)
from apps.property.models import PropertyGroup
from apps.partners.models import Partner
from decouple import config
from pathlib import Path
from django.contrib.auth import get_user_model
from core.utils import Utils

User = get_user_model()
utils = Utils()


def get_prediction_data():
    table_name = config('PD_AWS_TABLE_NAME')
    file = f"{settings.BASE_DIR}/data/prediction_data/sts_prediction_data.json"
    file_path = Path(file)
    if not file_path.exists():
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.touch()

    pd_aws_access_key = config('PD_AWS_ACCESS_KEY_ID', '')
    pd_aws_secret_access_key = config('PD_AWS_SECRET_ACCESS_KEY', '')

    if pd_aws_access_key:
        dynamo_client = boto3.resource(
                service_name=config('PD_AWS_SERVICE_NAME'),
                region_name=config('PD_AWS_REGION_NAME'),
                aws_access_key_id=pd_aws_access_key,
                aws_secret_access_key=pd_aws_secret_access_key
            )
    else:
        dynamo_client = boto3.resource(
            service_name=config('PD_AWS_SERVICE_NAME'),
            region_name=config('PD_AWS_REGION_NAME')
        )

    table = dynamo_client.Table(table_name)
    response = table.scan()
    data_items = response['Items']
    data_list = []
    partner = {
        'VRBO': 'VRBO',
        'HA': 'VRBO',
        'AT': 'VRBO',
        'HL': 'VRBO',
        'FW': 'VRBO',
        'HAUK': 'VRBO',
        'HAAU': 'VRBO',
        'HAES': 'VRBO',
        'BC': 'BC',
        'AB': 'AB',
        'HG': 'HG',
        'TA': 'TA',
        'KY': 'KY',
        'TC': 'TC',
        'EP': 'EP',
        'LT': 'LT',
        'HP': 'HP',
    }
    for item in data_items:
        data = {
            "date": item['date'],
            "user_id": item['user_id'],
            "ratio": {partner[k]: int(v) for k, v in item['ratio'].items()},
            "ratio_title": " ".join([f"{partner[k]}_{v}%" for k, v in item['ratio'].items()])
        }
        data_list.append(data)

    with open(file, 'w') as fp:
        fp.write(json.dumps(data_list))


# @shared_task()
def update_predicted_ratio_field_in_sts_db(file):
    with open(file, 'r') as fp:
        file_data = fp.read()
        json_data = json.loads(file_data)
        ratio_set_dict = {}
        for data in json_data:
            user_id = data['user_id']
            date = data['date']
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            ratio = data['ratio']
            ratio_title = data['ratio_title']
            try:
                pdrs, created = PredictedRatio.objects.get_or_create(
                    user_id=user_id,
                    prediction_date=date_obj
                )
                pdrs.predicted_ratio = ratio
                pdrs.predicted_ratio_title = ratio_title
                pdrs.revision += 1
                pdrs.save()
            except Exception as e:
                ValueError(f"Error: {e}")

            site_key, country_code, device_type = user_id.split('_')
            if country_code.upper() in ['EU', 'NA']:
                ratio_set_dict[user_id] = True
            brand = Brand.objects.filter(key=site_key.upper()).first()
            country = Location.objects.filter(country_code=country_code.upper()).first()
            device = Device.objects.filter(type__icontains=device_type).first()
            brand_location_ratio_sets = BrandLocationDefinedSetsRatio.objects.filter(
                brand=brand,
                location=country,
                device=device
            )
            if country_code.upper() == 'GB' and f"{site_key}_eu_{device_type}" not in ratio_set_dict:
                ratio_set_dict[f"{site_key}_eu_{device_type}"] = True
                country = Location.objects.filter(country_code='EU', location_type='continent').first()
                continent_ratio_sets = BrandLocationDefinedSetsRatio.objects.filter(
                    brand=brand,
                    location=country,
                    device=device
                )
                brand_location_ratio_sets = brand_location_ratio_sets.union(continent_ratio_sets)

            if country_code.upper() == 'US' and f"{site_key}_na_{device_type}" not in ratio_set_dict:
                ratio_set_dict[f"{site_key}_na_{device_type}"] = True
                country = Location.objects.filter(country_code='NA', location_type='continent').first()
                continent_ratio_sets = BrandLocationDefinedSetsRatio.objects.filter(
                    brand=brand,
                    location=country,
                    device=device
                )
                brand_location_ratio_sets = brand_location_ratio_sets.union(continent_ratio_sets)

            for blrs in brand_location_ratio_sets:
                blrs.predicted_ratio = pdrs
                # blrs.predicted_ratio_title = ratio_title
                # blrs.predicted_ratio_user_id = user_id
                blrs.save()


# @shared_task()
def bulk_create_ratio_sets(user_id, brand_ids, device_ids, location_id, search_location_id, property_group_id, ratio_set_id):
    ratio_set = RatioSet.objects.get(id=ratio_set_id)
    brand_list = Brand.objects.filter(id__in=brand_ids)
    location = Location.objects.get(id=location_id)
    search_location = SearchLocation.objects.get(id=search_location_id)
    property_group = PropertyGroup.objects.get(id=property_group_id)
    user = get_user_model().objects.get(id=user_id)

    new_ratio_sets = []
    update_ratio_sets = []
    for brand in brand_list:
        devices = Device.objects.filter(id__in=device_ids)
        for device in devices:
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
    BrandLocationDefinedSetsRatio.objects.bulk_create(new_ratio_sets)
    BrandLocationDefinedSetsRatio.objects.bulk_update(update_ratio_sets, ['ratio_set', 'ratio_set_title', 'updated_at'])


# @shared_task()
def clone_ratio_set_task(user_id, object_id, brand_ids):
    obj = BrandLocationDefinedSetsRatio.objects.get(id=object_id)
    brand_list = Brand.objects.filter(id__in=brand_ids)
    user = get_user_model().objects.get(id=user_id)

    for brand in brand_list:
        Utils.process_brand_locations(user, brand, [obj])


# @shared_task()
def bulk_clone_ratio_set_task(user_id, brand_ids, ratio_set_ids):
    brand_list = Brand.objects.filter(id__in=brand_ids)
    ratio_set_list = BrandLocationDefinedSetsRatio.objects.filter(id__in=ratio_set_ids)
    user = get_user_model().objects.get(id=user_id)

    for brand in brand_list:
        Utils.process_brand_locations(user, brand, ratio_set_list)


def perform_bulk_update_task(ratio_set_title, partner_ratios_ids, partner_ids, selected_object_ids):
    selected_objects = BrandLocationDefinedSetsRatio.objects.filter(id__in=selected_object_ids)
    ratio_set = RatioSet.objects.create(
        title=ratio_set_title
    )
    ratios = [(pid, v) for (pid, v) in zip(partner_ids, partner_ratios_ids) if v != '']
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
        obj.ratio_set_title = obj.ratio_set_short_title
        obj.updated_at = timezone.now()
        obj_list.append(obj)
        site_key_list.append(obj.brand.key)

    BrandLocationDefinedSetsRatio.objects.bulk_update(obj_list, ['ratio_set', 'ratio_set_title', 'updated_at'])
    # For the file write issue, unable to write the log file.
    # django_command = f'python manage.py generate_ratio_set_json_and_upload_s3 --site_keys {",".join(site_key_list)}'
    # utils.make_dir('log')
    # with open(f'log/s3-cache-{datetime.now().strftime("%Y-%m-%d")}.txt', 'a') as log_file:
    #     subprocess.Popen(
    #         django_command,
    #         shell=True,
    #         stdout=log_file,
    #         stderr=log_file,
    #         text=True,
    #     )
    try:
        django_command = f'python manage.py generate_ratio_set_json_and_upload_s3 --site_keys {",".join(site_key_list)}'
        subprocess.Popen(
            django_command,
            shell=True,
            text=True,
        )
    except Exception as err:
        print(f'Sub process running err: {err}')

