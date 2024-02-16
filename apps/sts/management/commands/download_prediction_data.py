import datetime

from decouple import config
from django.core.management.base import BaseCommand
from django.utils import timezone

from api import BASE_STS_PATH
from api.services import STSAPIService
from apps.sts.service.prediction_service import PredictionService
from core.service import CoreService
from core.utils import Utils


class Command(BaseCommand):
    help = "Download Predicted ratio data."
    core_service = CoreService()
    prediction_service = PredictionService()

    def handle(self, *args, **options):
        start_time = timezone.datetime.now().replace(microsecond=0)
        self.stdout.write('Downloading...')

        self.prediction_service.download_prediction_data_file()

        end_time = timezone.datetime.now().replace(microsecond=0)
        execution_time = (end_time - start_time)
        self.stdout.write(f"Start Time: {str(start_time)}")
        self.stdout.write(f"End Time: {str(end_time)}")
        self.stdout.write(f"Execution Time: {str(execution_time)}")
