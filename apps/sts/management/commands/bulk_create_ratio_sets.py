import datetime
import json
import ast
from decouple import config
from django.core.management.base import BaseCommand
from django.utils import timezone
from ast import literal_eval
from api import BASE_STS_PATH
from api.services import STSAPIService
from apps.sts.service.ratio_set import RatioSetService
from core.service import CoreService
from core.utils import Utils


class Command(BaseCommand):
    help = "Download Predicted ratio data."
    core_service = CoreService()
    ratioset_service = RatioSetService()

    def add_arguments(self, parser):
        parser.add_argument('--user_id', type=int, default=None)
        parser.add_argument('--brand_id_list', type=str, default=None)
        parser.add_argument('--device_ids', type=str, default=None)
        parser.add_argument('--loc_id', type=int, default=None)
        parser.add_argument('--search_loc_id', type=int, default=None)
        parser.add_argument('--property_group_id', type=int, default=None)
        parser.add_argument('--ratio_set_id', type=int, default=None)

    def handle(self, *args, **options):
        start_time = timezone.datetime.now().replace(microsecond=0)

        user_id = options.get('user_id')
        brand_id_list = options.get('brand_id_list')
        device_ids = options.get('device_ids')
        loc_id = options.get('loc_id')
        search_loc_id = options.get('search_loc_id')
        property_group_id = options.get('property_group_id')
        ratio_set_id = options.get('ratio_set_id')

        data = {
            "user_id": user_id,
            "brand_id_list": ast.literal_eval(brand_id_list),
            "device_ids": ast.literal_eval(device_ids),
            "loc_id": loc_id,
            "search_loc_id": search_loc_id,
            "property_group_id": property_group_id,
            "ratio_set_id": ratio_set_id
        }

        try:
            self.stdout.write('Bulk creating...')
            self.ratioset_service.bulk_create(data)
        except json.JSONDecodeError as e:
            self.stderr.write(self.style.ERROR(f'Error decoding JSON: {e}'))

        end_time = timezone.datetime.now().replace(microsecond=0)
        execution_time = (end_time - start_time)
        self.stdout.write(f"Start Time: {str(start_time)}")
        self.stdout.write(f"End Time: {str(end_time)}")
        self.stdout.write(f"Execution Time: {str(execution_time)}")