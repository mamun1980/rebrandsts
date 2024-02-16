import datetime

from decouple import config
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.sts.service.prediction_service import PredictionService


class Command(BaseCommand):
    help = "Update predicted ratio field into database"
    prediction_service = PredictionService()

    def add_arguments(self, parser):
        parser.add_argument('--file', nargs='?', type=str, default=None)

    def handle(self, *args, **options):
        start_time = timezone.datetime.now().replace(microsecond=0)
        file = options.get('file')
        self.stdout.write('Updating predicted ratio field into database........')
        print(f"file path: {file}")
        self.prediction_service.update_predicted_ratio_field_in_sts_db(file)

        end_time = timezone.datetime.now().replace(microsecond=0)
        execution_time = (end_time - start_time)
        self.stdout.write(f"Start Time: {str(start_time)}")
        self.stdout.write(f"End Time: {str(end_time)}")
        self.stdout.write(f"Execution Time: {str(execution_time)}")
