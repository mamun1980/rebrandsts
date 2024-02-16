from core.service import CoreService
import json
import boto3
from django.conf import settings
from pathlib import Path
from decouple import config
from datetime import datetime

from apps.sts.models import (Location, Device, BrandLocationDefinedSetsRatio, PredictedRatio, SearchLocation, RatioSet,
                             PartnerRatio)
from apps.brands.models import Brand


class PredictionService:
    core_service = CoreService()

    @staticmethod
    def download_prediction_data_file():
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

        try:
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
        except Exception as e:
            print(e)

    @staticmethod
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