import datetime

from decouple import config
from django.core.management.base import BaseCommand
from django.utils import timezone

from api import BASE_STS_PATH
from api.services import STSAPIService
from apps.sts.service.s3_service import S3Services
from core.service import CoreService
from core.utils import Utils


class Command(BaseCommand):
    help = "Upload STS ratio set JSON data to S3."

    def add_arguments(self, parser):
        parser.add_argument('--site_keys', nargs='?', type=str, default=None)

    def handle(self, *args, **options):
        start_time = timezone.datetime.now().replace(microsecond=0)
        self.stdout.write('Uploading STS ratio set json data to S3...')
        site_keys = options.get('site_keys')
        site_key_list = site_keys.split(',')
        core_service = CoreService()
        utils = Utils()
        s3_service = S3Services()
        ratio_service = STSAPIService()
        bucket_name = config('S3_BUCKET_NAME')
        site_env = config('SITE_ENV', 'dev')
        s3_config = core_service.s3_config()
        s3_client = core_service.s3_connection(s3_config)
        for brands_key in site_key_list:
            try:
                brands_key = brands_key.strip()
                site_key = brands_key.lower()
                data = ratio_service.get_ratio(brands_key.upper())
                data['updated_at'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                file_location = f"{BASE_STS_PATH}{site_key}.json"
                utils.remove_files(BASE_STS_PATH, f"{site_key}.json")
                utils.write_json_file(data=data, file_location=file_location)
                s3_object_name = f"{site_env}/{site_key}.json"
                s3_service.s3_file_process(bucket_name, file_location, s3_object_name, s3_client)
            except Exception as err:
                self.stdout.errors(err)

        end_time = timezone.datetime.now().replace(microsecond=0)
        execution_time = (end_time - start_time)
        self.stdout.write(f"Start Time: {str(start_time)}")
        self.stdout.write(f"End Time: {str(end_time)}")
        self.stdout.write(f"Execution Time: {str(execution_time)}")
