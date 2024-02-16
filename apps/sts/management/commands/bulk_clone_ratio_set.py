import json
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.sts.service.ratio_set import RatioSetService
from core.service import CoreService


class Command(BaseCommand):
    help = "Clone Ratio Set"
    core_service = CoreService()
    ratioset_service = RatioSetService()

    def add_arguments(self, parser):
        parser.add_argument('--user_id', type=int, default=None)
        parser.add_argument('--ratio_set_ids', type=str, default=None)
        parser.add_argument('--brand_ids', type=str, default=None)

    def handle(self, *args, **options):
        start_time = timezone.datetime.now().replace(microsecond=0)

        user_id = options.get('user_id')
        ratio_set_ids = options.get('ratio_set_ids')
        brand_ids = options.get('brand_ids')

        try:
            # print(f"{'*' * 50}")
            self.stdout.write('Cloning ratio sets...')
            # print(f"User ID: {user_id}, Object ID: {object_id} and Brands IDs: {brand_ids}")
            self.ratioset_service.bulk_clone_ratio_set(user_id, ratio_set_ids, brand_ids)
        except json.JSONDecodeError as e:
            self.stderr.write(self.style.ERROR(f'Error decoding JSON: {e}'))

        end_time = timezone.datetime.now().replace(microsecond=0)
        execution_time = (end_time - start_time)
        self.stdout.write(f"Start Time: {str(start_time)}")
        self.stdout.write(f"End Time: {str(end_time)}")
        self.stdout.write(f"Execution Time: {str(execution_time)}")