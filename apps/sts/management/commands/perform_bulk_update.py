import json
import ast
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.sts.service.ratio_set import RatioSetService
from core.service import CoreService


class Command(BaseCommand):
    help = "Clone Ratio Set"
    core_service = CoreService()
    ratioset_service = RatioSetService()

    def add_arguments(self, parser):
        parser.add_argument('--ratio_set_title', type=str, default=None)
        parser.add_argument('--partner_ratios_ids', type=str, default=None)
        parser.add_argument('--partner_ids', type=str, default=None)
        parser.add_argument('--selected_object_ids', type=str, default=None)

    def handle(self, *args, **options):
        start_time = timezone.datetime.now().replace(microsecond=0)

        partner_ratios_ids = options.get('partner_ratios_ids')
        partner_ids = options.get('partner_ids')
        selected_object_ids = options.get('selected_object_ids')

        partner_ratios_ids = ast.literal_eval(partner_ratios_ids)
        partner_ids = ast.literal_eval(partner_ids)
        selected_object_ids = ast.literal_eval(selected_object_ids)

        ratios = [(pid, v) for (pid, v) in zip(partner_ids, partner_ratios_ids) if v != 0]

        try:
            print(f"{'*' * 50}")
            self.stdout.write('Bulk Updating ratio sets...')

            self.ratioset_service.perform_bulk_update(ratios, selected_object_ids)
        except json.JSONDecodeError as e:
            self.stderr.write(self.style.ERROR(f'Error decoding JSON: {e}'))

        end_time = timezone.datetime.now().replace(microsecond=0)
        execution_time = (end_time - start_time)
        self.stdout.write(f"Start Time: {str(start_time)}")
        self.stdout.write(f"End Time: {str(end_time)}")
        self.stdout.write(f"Execution Time: {str(execution_time)}")